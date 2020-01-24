import unittest
import util
import json


class EncodingDecoding(unittest.TestCase):

    def test_dictionary_encode(self):
        with open('data/post_case_git_delete.json') as f:
            test_data = json.load(f)
        body = util.dictionary_encode(test_data['body'])
        self.assertEqual(str, type(body))
        self.assertFalse(': ' in body)
        self.assertFalse('= ' in body)
        self.assertEqual(len(body), 5919)

    def test_validate_hash(self):
        with open('data/post_case_git_delete.json') as f:
            test_data = json.load(f)

        body = util.dictionary_encode(test_data['body'])
        secret = 'zootan'
        expected = test_data['header']["X-Hub-Signature"].replace('sha1=', '')

        comparison = util.validate_hash(body, secret, expected)
        self.assertTrue(comparison)