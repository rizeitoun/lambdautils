import boto3
import requests
import re
import json
import util


base_url = 'https://api.github.com/repos'
client = boto3.client('codepipeline')

statuses = {
    'FAILED': 'failure',
    'STARTED': 'pending',
    'SUCCEEDED': 'success',
}
default_status = 'error'

descriptions = {
    'STARTED': 'The pipeline execution is currently running.',
    'FAILED': 'The pipeline execution was not completed successfully.',
    'CANCELED': 'The pipeline execution was canceled because the pipeline structure was updated.',
    'SUPERSEDED': 'While this pipeline execution was waiting for the next stage to be completed, a newer pipeline execution advanced and continued through the pipeline instead.',
    'RESUMED': 'A failed pipeline execution has been retried in response to the RetryStageExecution API call.',
    'SUCCEEDED': 'The pipeline execution was completed successfully.'
}
default_description = 'Unknown state.'


def get_repo_url(pipelineName, executionId):
    result = client.get_pipeline_execution(pipelineName=pipelineName, pipelineExecutionId=executionId)
    artifactRevision = result['pipelineExecution']['artifactRevisions'][0]
    sha = artifactRevision['revisionId']
    pattern = "github.com/(.*)/commit/"
    matches = re.search(pattern, artifactRevision['revisionUrl']).group(1).split('/')
    return f'{base_url}/{matches[0]}/{matches[1]}/statuses/{sha}'


def status_response(code):
    response_failed = f"Unable to post status: {code}"
    response_success = f"Status Posted: {code}"
    response = response_failed if code != 201 else response_success
    return response


def lambda_handler(event, _):
    region = event['region']
    api_token = util.decrypt_env_variable('api_token', region=region)
    headers = {'content-type': 'application/json', 'Authorization': f"token {api_token}"}

    details = event['detail']
    pipelineName = details['pipeline']
    executionId = details['execution-id']
    state = details['state']

    pipeline_url = f'https://{region}.console.aws.amazon.com/codepipeline/home?region={region}#/view/{pipelineName}'
    payload = {
        'state': statuses.get(state, default_status),
        'target_url': pipeline_url,
        'description': descriptions.get(state, default_description),
        'context': 'continuous-integration/codepipeline'
    }

    repo_url = get_repo_url(pipelineName, executionId)
    data = requests.post(repo_url, data=json.dumps(payload), headers=headers)

    return_string = 'Status posted.' if data.status_code == 201 else 'Unable to post status.'
    return util.status_output(data.status_code, return_string)