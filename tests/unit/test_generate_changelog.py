#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from datetime import datetime
from unittest import mock

from gitlab_changelog import generate_changelog


class TestGenerateChangelog(unittest.TestCase):
    """This class tests the generate_changelog method"""

    def mock_utcnow(self, mock_datetime):
        mock_datetime.now = mock.Mock(return_value=datetime(2017, 2, 15, 13, 5, 12))
        mock_datetime.strftime = datetime.strftime

    def test_must_read_and_write_file(self):
        mock_file_open = mock.mock_open(read_data='')
        with mock.patch('gitlab_changelog.open', mock_file_open, create=True):
            generate_changelog('version', 'version_changes', 'file')

        mock_file_open.assert_called_once_with('file', mode='wr')

    # @mock.patch('gitlab_changelog.datetime')
    # def test_empty_file_must_append_entry(self, mock_datetime):
    #     self.mock_utcnow(mock_datetime)
    #     mock_file_open = mock.mock_open(read_data='')
    #     with mock.patch('gitlab_changelog.open', mock_file_open, create=True):
    #         generate_changelog('version', 'version_changes', 'file')
    #     handle = mock_file_open()
    #     handle.write.assert_called_once_with('version\n  version_changes\nWed, Feb 15 2017 13:05:12 -0300 UTC\n\n')

    # @mock.patch('gitlab_changelog.datetime')
    # def test_file_has_content_must_prepend_entry(self, mock_datetime):
    #     self.mock_utcnow(mock_datetime)
    #     mock_file_open = mock.mock_open(read_data='old_version')
    #     with mock.patch('gitlab_changelog.open', mock_file_open, create=True):
    #         generate_changelog('version', 'version_changes', 'file')
    #     handle = mock_file_open()
    #     handle.write.assert_called_once_with(
    #         'version\n  version_changes\nWed, Feb 15 2017 13:05:12 -0300 UTC\n\nold_version')


if __name__ == '__main__':
    unittest.main()
