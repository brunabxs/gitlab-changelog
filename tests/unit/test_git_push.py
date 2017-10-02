#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import unittest

from unittest import mock

from gitlab_changelog import git_push, PushError


@mock.patch('gitlab_changelog.subprocess.Popen')
class TestGitPush(unittest.TestCase):
    """This class tests the git_push method"""

    def mock_process(self, return_value):
        mock_process = mock.Mock()
        mock_process.wait.return_value = return_value
        return mock_process

    def test_must_call_git_push(self, mock_popen):
        mock_popen.return_value = self.mock_process(0)
        git_push('target_branch')
        mock_popen.assert_any_call(['git', 'push', 'origin', 'target_branch'], stdout=subprocess.PIPE)

    def test_must_call_git_push_tags(self, mock_popen):
        mock_popen.return_value = self.mock_process(0)
        git_push('target_branch')
        mock_popen.assert_any_call(['git', 'push', 'origin', 'target_branch', '--tags'], stdout=subprocess.PIPE)

    def test_process_return_code_not_zero_must_raise_push_error(self, mock_popen):
        mock_popen.return_value = self.mock_process(123)
        with self.assertRaises(PushError):
            git_push('target_branch')


if __name__ == '__main__':
    unittest.main()
