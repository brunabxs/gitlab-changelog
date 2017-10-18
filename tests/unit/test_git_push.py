#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import unittest
from unittest import mock

from ci_helper import git_push, PushError
from tests.unit import BaseTest


@mock.patch('ci_helper.subprocess.Popen')
class TestGitPush(BaseTest):
    """This class tests the git_push method"""

    def test_must_call_git_push(self, mock_popen):
        mock_popen.return_value = self.mock_process(0)
        git_push('target_branch')
        mock_popen.assert_any_call(['git', 'push', 'origin', 'target_branch'], stdout=subprocess.PIPE)

    def test_process_return_code_not_zero_must_raise_push_error(self, mock_popen):
        mock_popen.return_value = self.mock_process(123)
        with self.assertRaises(PushError):
            git_push('target_branch')


if __name__ == '__main__':
    unittest.main()
