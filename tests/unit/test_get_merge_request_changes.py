#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from unittest import mock

from gitlab_changelog import get_merge_request_changes


@mock.patch('gitlab_changelog.urlopen')
class TestGetMergeRequestChanges(unittest.TestCase):
    """This class tests the get_merge_request_changes method"""
    
    def mock_read(self, return_value):
        mock_read = mock.MagicMock()
        mock_read.read.return_value = return_value
        return mock_read

    def test_no_merge_request_must_return_empty_list(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'[]')
        actual = get_merge_request_changes('https://gitlab.com/api/v4', 'gitlab_token', 'project_id', 'commit_sha')
        self.assertEqual(actual, [])

    def test_no_merge_request_with_commit_sha_must_return_empty_list(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'[{"merge_commit_sha": "other_commit_sha"}]')
        actual = get_merge_request_changes('https://gitlab.com/api/v4', 'gitlab_token', 'project_id', 'commit_sha')
        self.assertEqual(actual, [])

    def test_merge_request_with_commit_sha_must_return_merge_request_changes(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'[{"merge_commit_sha": "commit_sha1"}, {"merge_commit_sha": "commit_sha", "source_branch": "source_branch", "target_branch": "target_branch", "description": "description"}]')
        actual = get_merge_request_changes('https://gitlab.com/api/v4', 'gitlab_token', 'project_id', 'commit_sha')
        self.assertEqual(actual, ['description'])


if __name__ == '__main__':
    unittest.main()
