#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from unittest import mock
from urllib.error import HTTPError

from gitlab_changelog import get_commit_changes
from tests.unit import BaseTest


@mock.patch('gitlab_changelog.clean_content', return_value=['title'])
@mock.patch('gitlab_changelog.urlopen')
class TestGetCommitChanges(BaseTest):
    """This class tests the get_commit_changes method"""

    def test_must_call_clean_content(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(b'{"title": "title"}')
        get_commit_changes('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha')
        mock_clean_content.assert_called_once_with('title')

    def test_error_on_request_must_raise_http_error(self, mock_urlopen, mock_clean_content):
        mock_urlopen.side_effect = HTTPError('url', 'cde', 'msg', 'hdrs', 'fp')
        with self.assertRaises(HTTPError):
            get_commit_changes('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha')

    def test_commit_with_commit_sha_must_return_commit_changes(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(b'{"title": "title"}')
        actual = get_commit_changes('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha')
        self.assertEqual(actual, ['title'])

    def test_must_request_api(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(b'{"title": "title"}')
        get_commit_changes('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha')
        self.assertEqual(mock_urlopen.call_args[0][0].full_url,
                         'https://gitlab.com/api/v4/projects/project_id/repository/commits/commit_sha')

    def test_request_must_contain_header_private_token(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(b'{"title": "title"}')
        get_commit_changes('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha')
        self.assertEqual(mock_urlopen.call_args[0][0].headers['Private-token'], 'gitlab_token')

    def test_request_must_contain_method_get(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(b'{"title": "title"}')
        get_commit_changes('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha')
        self.assertEqual(mock_urlopen.call_args[0][0].method, 'GET')


if __name__ == '__main__':
    unittest.main()
