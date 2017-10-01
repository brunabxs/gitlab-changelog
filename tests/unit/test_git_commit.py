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
        return mock_process

    def test_must_call_git_commit(self, mock_popen):
        mock_popen.return_value = self.mock_process(0)
        git_commit()
        mock_popen.assert_called_once_with(['git', 'commit', '-am', 'Update changelog'], stdout=subprocess.PIPE)

    def test_process_return_code_not_zero_must_raise_commit_error(self, mock_popen):
        mock_popen.return_value = self.mock_process(123)
        with self.assertRaises(CommitError):
            git_commit()


if __name__ == '__main__':
    unittest.main()
