import unittest
import util
import json
import os

example_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'post_case_git_delete.json')


class EncodingDecoding(unittest.TestCase):

    def test_dictionary_encode(self):
        with open(example_file) as f:
            test_data = json.load(f)
        body = util.dictionary_encode(test_data['body'])
        self.assertEqual(str, type(body))
        self.assertFalse(': ' in body)
        self.assertFalse('= ' in body)
        self.assertEqual(len(body), 5982)

    def test_validate_hash(self):
        with open(example_file) as f:
            test_data = json.load(f)

        body = util.dictionary_encode(test_data['body'])
        secret = 'example_secret'
        expected = test_data['headers']["X-Hub-Signature"].replace('sha1=', '')

        comparison = util.validate_hash(body, secret, expected)
        self.assertTrue(comparison)