import configparser
import os

path_dir = os.path.dirname(os.path.abspath(__file__))

config_defaults = {
    'git_branching':
        {
            'enc': 'ascii',
            'region': 'us-east-1',
            'pipeline_template': 'pipeline_templates/ci_pipeline.json',
            'policy_template': 'policy_templates/ecr_repo_policy.json',
            'webhook_template': 'pipeline_templates/github_webhook.json',
            's3_bucket': 'template-storage-01162020',
        },
}

config = configparser.ConfigParser(defaults=config_defaults)
config.read(os.path.join(path_dir, 'config.cfg'))

