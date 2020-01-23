import configparser
import os

path_dir = os.path.dirname(os.path.abspath(__file__))

config_defaults = {
    'git_branching':
        {
            'enc': 'ascii',
            'region': 'us-east-1',
            'pipeline_template': 'pipeline_templates/ci_pipeline.json',
            'policy_template': 'policy_templates/ecr_repo_policy.json'
        },
}

config = configparser.ConfigParser(defaults=config_defaults)
config.read(os.path.join(path_dir, 'config.cfg'))

