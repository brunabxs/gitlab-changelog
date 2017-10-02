#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from unittest import mock
from urllib.error import HTTPError

from gitlab_changelog import get_merge_request_changes


@mock.patch('gitlab_changelog.clean_content')
@mock.patch('gitlab_changelog.urlopen')
class TestGetMergeRequestChanges(unittest.TestCase):
    """This class tests the get_merge_request_changes method"""

    def mock_read(self, return_value):
        mock_read = mock.MagicMock()
        mock_read.read.return_value = return_value
        return mock_read

    def test_error_on_request_must_raise_http_error(self, mock_urlopen, mock_clean_content):
        mock_urlopen.side_effect = HTTPError('url', 'cde', 'msg', 'hdrs', 'fp')
        with self.assertRaises(HTTPError):
            get_merge_request_changes('https://gitlab.com/api/v4', 'gitlab_token', 'project_id', 'commit_sha')

    def test_no_merge_request_must_not_call_clean_content(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(b'[]')
        self.assertFalse(mock_clean_content.called, get_merge_request_changes('https://gitlab.com/api/v4',
                                                                              'gitlab_token', 'project_id',
                                                                              'commit_sha'))

    def test_no_merge_request_must_return_empty_list(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(b'[]')
        actual = get_merge_request_changes('https://gitlab.com/api/v4', 'gitlab_token', 'project_id', 'commit_sha')
        self.assertEqual(actual, [])

    def test_no_merge_request_with_commit_sha_must_not_call_clean_content(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(b'[{"merge_commit_sha": "other_commit_sha"}]')
        self.assertFalse(mock_clean_content.called, get_merge_request_changes('https://gitlab.com/api/v4',
                                                                              'gitlab_token', 'project_id',
                                                                              'commit_sha'))

    def test_no_merge_request_with_commit_sha_must_return_empty_list(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(b'[{"merge_commit_sha": "other_commit_sha"}]')
        actual = get_merge_request_changes('https://gitlab.com/api/v4', 'gitlab_token', 'project_id', 'commit_sha')
        self.assertEqual(actual, [])

    def test_merge_request_with_commit_sha_must_call_clean_content(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(str.encode('[{"merge_commit_sha": "commit_sha1"}, '
                                                              '{"merge_commit_sha": "commit_sha", '
                                                              '"source_branch": "source_branch", '
                                                              '"target_branch": "target_branch", '
                                                              '"description": "description"}]'))
        mock_clean_content.return_value = ['description']
        get_merge_request_changes('https://gitlab.com/api/v4', 'gitlab_token', 'project_id', 'commit_sha')
        mock_clean_content.assert_called_once_with('description')

    def test_merge_request_with_commit_sha_must_return_merge_request_changes(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(str.encode('[{"merge_commit_sha": "commit_sha1"}, '
                                                              '{"merge_commit_sha": "commit_sha", '
                                                              '"source_branch": "source_branch", '
                                                              '"target_branch": "target_branch", '
                                                              '"description": "description"}]'))
        mock_clean_content.return_value = ['description']
        actual = get_merge_request_changes('https://gitlab.com/api/v4', 'gitlab_token', 'project_id', 'commit_sha')
        self.assertEqual(actual, ['description'])


if __name__ == '__main__':
    unittest.main()
