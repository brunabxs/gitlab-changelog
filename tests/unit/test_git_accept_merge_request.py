#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import unittest

from unittest import mock
from urllib.error import HTTPError

from gitlab_changelog import git_accept_merge_request


@mock.patch('gitlab_changelog.urlopen')
class TestGitAcceptMergeRequest(unittest.TestCase):
    """This class tests the git_accept_merge_request method"""

    def mock_read(self, return_value):
        mock_read = mock.MagicMock()
        mock_read.read.return_value = return_value
        return mock_read

    def test_error_on_request_must_raise_http_error(self, mock_urlopen):
        mock_urlopen.side_effect = HTTPError('url', 'cde', 'msg', 'hdrs', 'fp')
        with self.assertRaises(HTTPError):
            git_accept_merge_request('https://gitlab.com', 'gitlab_token', 'project_id', 'source_branch',
                                     'target_branch', 'iid')

    def test_must_request_api(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{}')
        git_accept_merge_request('https://gitlab.com', 'gitlab_token', 'project_id', 'source_branch', 'target_branch',
                                 'iid')
        self.assertEqual(mock_urlopen.call_args[0][0].full_url,
                         'https://gitlab.com/api/v4/projects/project_id/merge_requests/iid/merge')

    def test_request_must_contain_header_private_token(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{}')
        git_accept_merge_request('https://gitlab.com', 'gitlab_token', 'project_id', 'source_branch', 'target_branch',
                                 'iid')
        self.assertEqual(mock_urlopen.call_args[0][0].headers['Private-token'], 'gitlab_token')

    def test_request_must_contain_method_put(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{}')
        git_accept_merge_request('https://gitlab.com', 'gitlab_token', 'project_id', 'source_branch', 'target_branch',
                                 'iid')
        self.assertEqual(mock_urlopen.call_args[0][0].method, 'PUT')

    def test_request_must_contain_body_with_merge_commit_message(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{}')
        git_accept_merge_request('https://gitlab.com', 'gitlab_token', 'project_id', 'source_branch', 'target_branch',
                                 'iid')
        decoded_data = mock_urlopen.call_args[0][0].data.decode('utf-8')
        self.assertEqual(json.loads(decoded_data).get('merge_commit_message'),
                         'Automatic merge branch \'source_branch\' into \'target_branch\'')


if __name__ == '__main__':
    unittest.main()
