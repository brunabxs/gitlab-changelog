#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import unittest

from unittest import mock
from urllib.error import HTTPError

from gitlab_changelog import git_create_merge_request


@mock.patch('gitlab_changelog.urlopen')
class TestGitCreateMergeRequest(unittest.TestCase):
    """This class tests the git_create_merge_request method"""

    def mock_read(self, return_value):
        mock_read = mock.MagicMock()
        mock_read.read.return_value = return_value
        return mock_read

    def test_error_on_request_must_raise_http_error(self, mock_urlopen):
        mock_urlopen.side_effect = HTTPError('url', 'cde', 'msg', 'hdrs', 'fp')
        with self.assertRaises(HTTPError):
            git_create_merge_request('https://gitlab.com', 'gitlab_token', 'project_id', 'source_branch',
                                     'target_branch', ['version_changes'])

    def test_must_return_merge_request_iid(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"iid": "iid"}')
        actual = git_create_merge_request('https://gitlab.com', 'gitlab_token', 'project_id', 'source_branch',
                                          'target_branch', ['version_changes'])
        self.assertEqual(actual, 'iid')

    def test_must_request_api(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"iid": "iid"}')
        git_create_merge_request('https://gitlab.com', 'gitlab_token', 'project_id', 'source_branch', 'target_branch',
                                 ['version_changes'])
        self.assertEqual(mock_urlopen.call_args[0][0].full_url,
                         'https://gitlab.com/api/v4/projects/project_id/merge_requests')

    def test_request_must_contain_header_private_token(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"iid": "iid"}')
        git_create_merge_request('https://gitlab.com', 'gitlab_token', 'project_id', 'source_branch', 'target_branch',
                                 ['version_changes'])
        self.assertEqual(mock_urlopen.call_args[0][0].headers['Private-token'], 'gitlab_token')

    def test_request_must_contain_header_content_type(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"iid": "iid"}')
        git_create_merge_request('https://gitlab.com', 'gitlab_token', 'project_id', 'source_branch', 'target_branch',
                                 ['version_changes'])
        self.assertEqual(mock_urlopen.call_args[0][0].headers['Content-type'], 'application/json')

    def test_request_must_contain_method_post(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"iid": "iid"}')
        git_create_merge_request('https://gitlab.com', 'gitlab_token', 'project_id', 'source_branch', 'target_branch',
                                 ['version_changes'])
        self.assertEqual(mock_urlopen.call_args[0][0].method, 'POST')

    def test_request_must_contain_body_with_source_branch(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"iid": "iid"}')
        git_create_merge_request('https://gitlab.com', 'gitlab_token', 'project_id', 'source_branch', 'target_branch',
                                 ['version_changes'])
        decoded_data = mock_urlopen.call_args[0][0].data.decode('utf-8')
        self.assertEqual(json.loads(decoded_data).get('source_branch'), 'source_branch')

    def test_request_must_contain_body_with_target_branch(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"iid": "iid"}')
        git_create_merge_request('https://gitlab.com', 'gitlab_token', 'project_id', 'source_branch', 'target_branch',
                                 ['version_changes'])
        decoded_data = mock_urlopen.call_args[0][0].data.decode('utf-8')
        self.assertEqual(json.loads(decoded_data).get('target_branch'), 'target_branch')

    def test_request_must_contain_body_with_title(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"iid": "iid"}')
        git_create_merge_request('https://gitlab.com', 'gitlab_token', 'project_id', 'source_branch', 'target_branch',
                                 ['version_changes'])
        decoded_data = mock_urlopen.call_args[0][0].data.decode('utf-8')
        self.assertEqual(json.loads(decoded_data).get('title'),
                         'Automatic merge branch \'source_branch\' into \'target_branch\'')

    def test_request_must_contain_body_with_description(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"iid": "iid"}')
        git_create_merge_request('https://gitlab.com', 'gitlab_token', 'project_id', 'source_branch', 'target_branch',
                                 ['version_changes'])
        decoded_data = mock_urlopen.call_args[0][0].data.decode('utf-8')
        self.assertEqual(json.loads(decoded_data).get('description'), '- version_changes\n\n- - - \n\n- [ ] @brunabxs')

    def test_multiple_changes_request_must_contain_body_with_description(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"iid": "iid"}')
        git_create_merge_request('https://gitlab.com', 'gitlab_token', 'project_id', 'source_branch', 'target_branch',
                                 ['chng1', 'chng2'])
        decoded_data = mock_urlopen.call_args[0][0].data.decode('utf-8')
        self.assertEqual(json.loads(decoded_data).get('description'), '- chng1\n- chng2\n\n- - - \n\n- [ ] @brunabxs')


if __name__ == '__main__':
    unittest.main()
