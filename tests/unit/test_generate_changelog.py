#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from unittest import mock

from ci_helper import generate_changelog, NoChanges
from tests.unit import BaseTest


class TestGenerateChangelog(BaseTest):
    """This class tests the generate_changelog method"""

    def test_must_read_and_write_file(self):
        mock_file_open = mock.mock_open(read_data='')
        with mock.patch('ci_helper.open', mock_file_open, create=True):
            generate_changelog('version', 'version_changes', 'file')

        mock_file_open.assert_any_call('file', mode='r')
        mock_file_open.assert_any_call('file', mode='w')
        assert mock_file_open.call_count == 2

    def test_empty_version_changes_must_raise_no_changes(self):
        mock_file_open = mock.mock_open(read_data='')
        with mock.patch('ci_helper.open', mock_file_open, create=True):
            with self.assertRaises(NoChanges):
                generate_changelog('version', [], 'file')

    @mock.patch('ci_helper.datetime')
    def test_multiple_version_changes_must_itemize(self, mock_datetime):
        self.mock_utcnow(mock_datetime)
        mock_file_open = mock.mock_open(read_data='old_content')
        with mock.patch('ci_helper.open', mock_file_open, create=True):
            generate_changelog('version', ['change1', 'change2', 'change3'], 'file')
        handle = mock_file_open()
        handle.write.assert_called_once_with(
            'version\n\n  - change1\n  - change2\n  - change3\n\nWed, Feb 15 2017 13:05:12  \n\nold_content')

    @mock.patch('ci_helper.datetime')
    def test_empty_file_must_append_entry(self, mock_datetime):
        self.mock_utcnow(mock_datetime)
        mock_file_open = mock.mock_open(read_data='')
        with mock.patch('ci_helper.open', mock_file_open, create=True):
            generate_changelog('version', ['version_changes'], 'file')
        handle = mock_file_open()
        handle.write.assert_called_once_with('version\n\n  - version_changes\n\nWed, Feb 15 2017 13:05:12  \n\n')

    @mock.patch('ci_helper.datetime')
    def test_file_has_content_must_prepend_entry(self, mock_datetime):
        self.mock_utcnow(mock_datetime)
        mock_file_open = mock.mock_open(read_data='old_content')
        with mock.patch('ci_helper.open', mock_file_open, create=True):
            generate_changelog('version', ['version_changes'], 'file')
        handle = mock_file_open()
        handle.write.assert_called_once_with(
            'version\n\n  - version_changes\n\nWed, Feb 15 2017 13:05:12  \n\nold_content')


if __name__ == '__main__':
    unittest.main()
