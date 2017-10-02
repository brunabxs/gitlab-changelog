#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from unittest import mock
from urllib.error import HTTPError

from gitlab_changelog import git_merge_request


@mock.patch('gitlab_changelog.git_accept_merge_request')
@mock.patch('gitlab_changelog.git_create_merge_request')
class TestGitMergeRequest(unittest.TestCase):
    """This class tests the git_merge_request method"""

    def mock_process(self, return_value):
        mock_process = mock.Mock()
        mock_process.wait.return_value = return_value
        return mock_process

    def test_branch_master_must_call_git_create_merge_request(self, mock_git_create_merge_request,
                                                              mock_git_accept_merge_request):
        git_merge_request('gitlab_endpoint', 'gitlab_token', 'project_id', 'master', ['version_changes'])
        mock_git_create_merge_request.assert_called_once_with('gitlab_endpoint', 'gitlab_token', 'project_id',
                                                              ['version_changes'])

    def test_branch_not_master_must_not_call_git_create_merge_request(self, mock_git_create_merge_request,
                                                                      mock_git_accept_merge_request):
        self.assertFalse(mock_git_create_merge_request.called, git_merge_request('gitlab_endpoint', 'gitlab_token',
                                                                                 'project_id', 'branch',
                                                                                 ['version_changes']))

    def test_branch_master_must_call_git_accept_merge_request(self, mock_git_create_merge_request,
                                                              mock_git_accept_merge_request):
        mock_git_create_merge_request.return_value = 'merge_request_iid'
        git_merge_request('gitlab_endpoint', 'gitlab_token', 'project_id', 'master', ['version_changes'])
        mock_git_accept_merge_request.assert_called_once_with('gitlab_endpoint', 'gitlab_token', 'project_id',
                                                              'merge_request_iid')

    def test_branch_not_master_must_not_call_git_accept_merge_request(self, mock_git_create_merge_request,
                                                                      mock_git_accept_merge_request):
        mock_git_create_merge_request.return_value = 'merge_request_iid'
        self.assertFalse(mock_git_accept_merge_request.called, git_merge_request('gitlab_endpoint', 'gitlab_token',
                                                                                 'project_id', 'branch',
                                                                                 ['version_changes']))

    def test_git_create_merge_request_succeeds_must_call_git_accept_merge_request(self, mock_git_create_merge_request,
                                                                                  mock_git_accept_merge_request):
        mock_git_create_merge_request.return_value = 'merge_request_iid'
        git_merge_request('gitlab_endpoint', 'gitlab_token', 'project_id', 'master', ['version_changes'])
        mock_git_accept_merge_request.assert_called_once_with('gitlab_endpoint', 'gitlab_token', 'project_id',
                                                              'merge_request_iid')

    def test_git_create_merge_request_fails_must_raise_http_error(self, mock_git_create_merge_request,
                                                                  mock_git_accept_merge_request):
        mock_git_create_merge_request.side_effect = HTTPError('url', 'cde', 'msg', 'hdrs', 'fp')
        with self.assertRaises(HTTPError):
            git_merge_request('gitlab_endpoint', 'gitlab_token', 'project_id', 'master', ['version_changes'])

    def test_git_create_merge_request_fails_must_not_call_git_accept_merge_request(self, mock_git_create_merge_request,
                                                                                   mock_git_accept_merge_request):
        mock_git_create_merge_request.side_effect = HTTPError('url', 'cde', 'msg', 'hdrs', 'fp')
        with self.assertRaises(HTTPError):
            self.assertFalse(mock_git_accept_merge_request.called, git_merge_request('gitlab_endpoint', 'gitlab_token',
                                                                                     'project_id', 'master',
                                                                                     ['version_changes']))

    def test_git_accept_merge_request_fails_must_raise_http_error(self, mock_git_create_merge_request,
                                                                  mock_git_accept_merge_request):
        mock_git_create_merge_request.return_value = 'merge_request_iid'
        mock_git_accept_merge_request.side_effect = HTTPError('url', 'cde', 'msg', 'hdrs', 'fp')
        with self.assertRaises(HTTPError):
            git_merge_request('gitlab_endpoint', 'gitlab_token', 'project_id', 'master', ['version_changes'])


if __name__ == '__main__':
    unittest.main()
