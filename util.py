import json
import os
import hashlib
import hmac
import boto3
from base64 import b64decode
from typing import Dict


def decrypt_env_variable(name: str, region: str = 'us-east-1') -> str:
    """
    AWS Key Management to decode a key saved as an environmental variable.
    Ensure KMS used has authorized IAM on Lambda function.
    """
    encrypted_var = os.environ.get(name)
    decrypted_var = boto3.client('kms', region).decrypt(CiphertextBlob=b64decode(encrypted_var))
    secret = decrypted_var['Plaintext'].decode("utf-8")
    return secret


def dictionary_encode(dictionary_in: Dict) -> str:
    """ Removes additional content added by json.dumps"""
    return json.dumps(dictionary_in, separators=(',', ':'))


def validate_hash(payload : str, secret : str, expected, encoding_scheme: str = 'ascii', algorithm=hashlib.sha1) -> bool:
    """
    Validates hash using hmac.
    """
    observed = hmac.new(secret.encode(encoding_scheme),
                        payload.encode(encoding_scheme),
                        algorithm).hexdigest()
    return hmac.compare_digest(str(expected), str(observed))


def status_output(return_key: str, return_string: str) -> Dict:
    """ Gets a status output that can be returned as a POST to client. """
    return {
        'statusCode': return_key,
        'body': json.dumps(return_string)
    }