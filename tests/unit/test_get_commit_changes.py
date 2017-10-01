#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from unittest import mock

from gitlab_changelog import get_commit_changes


@mock.patch('gitlab_changelog.clean_content', return_value=['title'])
@mock.patch('gitlab_changelog.urlopen')
class TestGetCommitChanges(unittest.TestCase):
    """This class tests the get_commit_changes method"""

    def mock_read(self, return_value):
        mock_read = mock.MagicMock()
        mock_read.read.return_value = return_value
        return mock_read

    # TODO: must test when no commit with sha is found

    def test_must_call_clean_content(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(b'{"title": "title"}')
        get_commit_changes('https://gitlab.com/api/v4', 'gitlab_token', 'project_id', 'commit_sha')
        mock_clean_content.assert_called_once_with('title')

    def test_commit_with_commit_sha_must_return_commit_changes(self, mock_urlopen, mock_clean_content):
        mock_urlopen.return_value = self.mock_read(b'{"title": "title"}')
        actual = get_commit_changes('https://gitlab.com/api/v4', 'gitlab_token', 'project_id', 'commit_sha')
        self.assertEqual(actual, ['title'])


if __name__ == '__main__':
    unittest.main()
