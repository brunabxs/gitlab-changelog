#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from unittest import mock
from urllib.error import HTTPError

from gitlab_changelog import get_merge_request_changes
from tests.unit import BaseTest


@mock.patch('gitlab_changelog.clean_content')
@mock.patch('gitlab_changelog.urlopen')
class TestGetMergeRequestChanges(BaseTest):
    """This class tests the get_merge_request_changes method"""

    def test_error_on_request_must_raise_http_error(self, mock_urlopen, mock_clean_content):
        mock_urlopen.side_effect = HTTPError('url', 'cde', 'msg', 'hdrs', 'fp')
        with self.assertRaises(HTTPError):
            get_merge_request_changes('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha')

    def test_no_merge_request_must_not_call_clean_content(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(b'[]')
        self.assertFalse(mock_clean_content.called, get_merge_request_changes('https://gitlab.com',
                                                                              'gitlab_token', 'project_id',
                                                                              'commit_sha'))

    def test_no_merge_request_must_return_empty_list(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(b'[]')
        actual = get_merge_request_changes('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha')
        self.assertEqual(actual, [])

    def test_no_merge_request_with_commit_sha_must_not_call_clean_content(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(b'[{"merge_commit_sha": "other_commit_sha"}]')
        self.assertFalse(mock_clean_content.called, get_merge_request_changes('https://gitlab.com',
                                                                              'gitlab_token', 'project_id',
                                                                              'commit_sha'))

    def test_no_merge_request_with_commit_sha_must_return_empty_list(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(b'[{"merge_commit_sha": "other_commit_sha"}]')
        actual = get_merge_request_changes('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha')
        self.assertEqual(actual, [])

    def test_merge_request_with_commit_sha_must_call_clean_content(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(str.encode('[{"merge_commit_sha": "commit_sha1"}, '
                                                              '{"merge_commit_sha": "commit_sha", '
                                                              '"source_branch": "source_branch", '
                                                              '"target_branch": "target_branch", '
                                                              '"description": "description"}]'))
        mock_clean_content.return_value = ['description']
        get_merge_request_changes('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha')
        mock_clean_content.assert_called_once_with('description')

    def test_merge_request_with_commit_sha_must_return_merge_request_changes(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(str.encode('[{"merge_commit_sha": "commit_sha1"}, '
                                                              '{"merge_commit_sha": "commit_sha", '
                                                              '"source_branch": "source_branch", '
                                                              '"target_branch": "target_branch", '
                                                              '"description": "description"}]'))
        mock_clean_content.return_value = ['description']
        actual = get_merge_request_changes('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha')
        self.assertEqual(actual, ['description'])

    def test_must_request_api(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(str.encode('[{"merge_commit_sha": "commit_sha1"}, '
                                                              '{"merge_commit_sha": "commit_sha", '
                                                              '"source_branch": "source_branch", '
                                                              '"target_branch": "target_branch", '
                                                              '"description": "description"}]'))
        get_merge_request_changes('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha')
        self.assertEqual(mock_urlopen.call_args[0][0].full_url,
                         'https://gitlab.com/api/v4/projects/project_id/merge_requests')

    def test_request_must_contain_header_private_token(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(str.encode('[{"merge_commit_sha": "commit_sha1"}, '
                                                              '{"merge_commit_sha": "commit_sha", '
                                                              '"source_branch": "source_branch", '
                                                              '"target_branch": "target_branch", '
                                                              '"description": "description"}]'))
        get_merge_request_changes('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha')
        self.assertEqual(mock_urlopen.call_args[0][0].headers['Private-token'], 'gitlab_token')

    def test_request_must_contain_method_get(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(str.encode('[{"merge_commit_sha": "commit_sha1"}, '
                                                              '{"merge_commit_sha": "commit_sha", '
                                                              '"source_branch": "source_branch", '
                                                              '"target_branch": "target_branch", '
                                                              '"description": "description"}]'))
        get_merge_request_changes('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha')
        self.assertEqual(mock_urlopen.call_args[0][0].method, 'GET')


if __name__ == '__main__':
    unittest.main()
