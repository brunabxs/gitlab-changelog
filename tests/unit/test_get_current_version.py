#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from unittest import mock

from gitlab_changelog import get_current_version
from tests.unit import BaseTest


class TestGetCurrentVersion(BaseTest):
    """This class tests the get_current_version method"""

    def test_must_read_file(self):
        mock_file_open = mock.mock_open(read_data='')
        with mock.patch('gitlab_changelog.open', mock_file_open, create=True):
            get_current_version('file')

        mock_file_open.assert_called_once_with('file', mode='r')

    @mock.patch('gitlab_changelog.open', mock.mock_open(read_data=''), create=True)
    def test_empty_file_must_return_empty_string(self):
        actual = get_current_version('file')
        self.assertEqual(actual, '')

    @mock.patch('gitlab_changelog.open', mock.mock_open(read_data='1.2.3'), create=True)
    def test_file_with_one_non_rc_version_must_extract_version(self):
        actual = get_current_version('file')
        self.assertEqual(actual, '1.2.3')

    @mock.patch('gitlab_changelog.open', mock.mock_open(read_data='1.2.3-rc.1'), create=True)
    def test_file_with_one_rc_version_must_extract_version(self):
        actual = get_current_version('file')
        self.assertEqual(actual, '1.2.3-rc.1')

    @mock.patch('gitlab_changelog.open', mock.mock_open(read_data='1.2.3\n1.2.2\n1.2.1\n'), create=True)
    def test_file_with_multiple_non_rc_version_must_extract_first_version(self):
        actual = get_current_version('file')
        self.assertEqual(actual, '1.2.3')

    @mock.patch('gitlab_changelog.open', mock.mock_open(read_data='1.2.3-rc.3\n1.2.3-rc.2\n1.2.3-rc.1\n'), create=True)
    def test_file_with_multiple_rc_version_must_extract_first_version(self):
        actual = get_current_version('file')
        self.assertEqual(actual, '1.2.3-rc.3')


if __name__ == '__main__':
    unittest.main()
