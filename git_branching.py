import util
import boto3
import json
from config import config

""" 
Will create or destroy codepipelines and container registries when a new branch is 
created or destroyed, respectively.
"""

enc = config['git_branching']['enc']
region = config['git_branching']['region']
pipeline_template = config['git_branching']['pipeline_template']
policy_template = config['git_branching']['policy_template']


def validate_hash(body, access):
    encoded_body = util.dictionary_encode(body)
    secret = util.decrypt_env_variable('secret', region)
    expected = access.replace('sha1=', '')

    validate = util.validate_hash(encoded_body, secret, expected)

    return_data = None
    if not validate:
        return_data = util.status_output(403, "Unable to validate input.")

    return return_data


def lambda_handler(event, _):

    def get_tags(key, value):
        return [
            {key: 'project_name', value: project_name},
            {key: 'branch_owner', value: body['sender']['login']},
            {key: 'template', value: pipeline_template},
        ]

    headers = event['headers']

    try:
        access = headers['X-Hub-Signature']
    except KeyError:
        return util.status_output(403, "Unable to find signature.")

    body = event['body']

    return_data = validate_hash(body, access)
    if return_data is not None:
        return return_data

    if body['ref_type'] == 'branch':
        ecr_client = boto3.client('ecr')
        client = boto3.client('codepipeline')

        ref = body['ref']
        project_name = body['repository']['name']
        pipeline_name = f"{project_name}_{ref.replace('/', '')}"

        event_type = headers['X-GitHub-Event']
        if event_type == 'create':
            s3 = boto3.client('s3')
            template = s3.get_object(Bucket='template-storage-01162020', Key=pipeline_template)
            policy = s3.get_object(Bucket='template-storage-01162020', Key=policy_template)

            template_json = json.loads(template['Body'].read().decode("utf-8"))
            policy_json = str(json.loads(policy['Body'].read())).replace('\'', '\"')

            template_json['pipeline']['name'] = pipeline_name
            for stage in template_json['pipeline']['stages']:
                if stage['name'] == 'Source':
                    stage['actions'][0]['configuration']['Branch'] = ref
                    stage['actions'][0]['configuration']['OAuthToken'] = util.decrypt_env_variable('oauth',
                                                                                                   region=region)
            for stage in template_json['pipeline']['stages']:
                for action in stage['actions']:
                    action['region'] = region

            ecr_tags = get_tags('Key', 'Value')
            pipeline_tags = get_tags('key', 'value')
            ecr_client.create_repository(repositoryName=pipeline_name, tags=ecr_tags)
            ecr_client.put_lifecycle_policy(repositoryName=pipeline_name, lifecyclePolicyText=policy_json)
            client.create_pipeline(pipeline=template_json['pipeline'], tags=pipeline_tags)

        elif event_type == 'delete':
            client.delete_pipeline(name=pipeline_name)
            ecr_client.delete_repository(repositoryName=pipeline_name)

    return util.status_output(200, "POST successfully processed")
