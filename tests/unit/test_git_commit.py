#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import unittest

from unittest import mock

from gitlab_changelog import git_commit, CommitError


@mock.patch('gitlab_changelog.subprocess.Popen')
class TestGitCommit(unittest.TestCase):
    """This class tests the git_commit method"""

    def mock_process(self, return_value):
        mock_process = mock.Mock()
        mock_process.wait.return_value = return_value
        mock_process.stdout.readlines.return_value = [b'commit_sha\n']
        return mock_process

    def test_must_call_git_commit(self, mock_popen):
        mock_popen.return_value = self.mock_process(0)
        git_commit('branch', 'file')
        mock_popen.assert_any_call(['git', 'add', 'file'], stdout=subprocess.PIPE)
        mock_popen.assert_any_call(['git', 'commit', '-m', 'Update changelog (branch)'], stdout=subprocess.PIPE)
        mock_popen.assert_any_call(['git', 'log', '--format=%H', '-n', '1'], stdout=subprocess.PIPE)
        assert mock_popen.call_count == 3

    def test_process_return_code_not_zero_must_raise_commit_error(self, mock_popen):
        mock_popen.return_value = self.mock_process(123)
        with self.assertRaises(CommitError):
            git_commit('branch', 'file')


if __name__ == '__main__':
    unittest.main()
