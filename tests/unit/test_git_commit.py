#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import unittest
from unittest import mock

from gitlab_changelog import git_commit, CommitError
from tests.unit import BaseTest


@mock.patch('gitlab_changelog.subprocess.Popen')
class TestGitCommit(BaseTest):
    """This class tests the git_commit method"""

    def test_must_call_git_add_file(self, mock_popen):
        mock_popen.return_value = self.mock_process(0)
        git_commit('branch', 'file')
        mock_popen.assert_any_call(['git', 'add', 'file'], stdout=subprocess.PIPE)

    def test_must_call_git_commit(self, mock_popen):
        mock_popen.return_value = self.mock_process(0)
        git_commit('branch', 'file')
        mock_popen.assert_any_call(['git', 'commit', '-m', 'Update changelog (branch)'], stdout=subprocess.PIPE)

    def test_must_call_git_log(self, mock_popen):
        mock_popen.return_value = self.mock_process(0, [b'commit_sha\n'])
        git_commit('branch', 'file')
        mock_popen.assert_any_call(['git', 'log', '--format=%H', '-n', '1'], stdout=subprocess.PIPE)

    def test_must_return_commit_sha(self, mock_popen):
        mock_popen.return_value = self.mock_process(0, [b'commit_sha\n'])
        actual = git_commit('branch', 'file')
        self.assertEqual(actual, 'commit_sha')

    def test_process_return_code_not_zero_must_raise_commit_error(self, mock_popen):
        mock_popen.return_value = self.mock_process(123)
        with self.assertRaises(CommitError):
            git_commit('branch', 'file')


if __name__ == '__main__':
    unittest.main()
