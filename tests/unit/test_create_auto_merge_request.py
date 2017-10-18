#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from unittest import mock
from urllib.error import HTTPError

from ci_helper import create_auto_merge_request
from tests.unit import BaseTest


@mock.patch('ci_helper.git_accept_merge_request')
@mock.patch('ci_helper.git_create_merge_request')
@mock.patch('ci_helper.git_get_tag_release_description')
class TestCreateAutoMergeRequest(BaseTest):
    """This class tests the create_auto_merge_request method"""

    def test_must_call_git_get_tag_release_description(self, mock_git_get_tag_release_description,
                                                       mock_git_create_merge_request, mock_git_accept_merge_request):
        create_auto_merge_request('gitlab_endpoint', 'gitlab_token', 'project_id', 'source_branch', 'target_branch',
                                  ['user1'], 'tag_name')
        mock_git_get_tag_release_description.assert_called_once_with('gitlab_endpoint', 'gitlab_token', 'project_id',
                                                                     'tag_name')

    def test_git_get_tag_release_description_succeeds_must_call_git_create_merge_request_once(self,
                                                                                              mock_git_get_tag_release_description,  # NOQA
                                                                                              mock_git_create_merge_request,  # NOQA
                                                                                              mock_git_accept_merge_request):  # NOQA
        mock_git_get_tag_release_description.return_value = ['version_changes']
        create_auto_merge_request('gitlab_endpoint', 'gitlab_token', 'project_id', 'source_branch', 'target_branch',
                                  ['user1'], 'tag_name')
        mock_git_create_merge_request.assert_called_once_with('gitlab_endpoint', 'gitlab_token', 'project_id',
                                                              'source_branch', 'target_branch', ['user1'],
                                                              ['version_changes'])

    def test_git_get_tag_release_description_fails_must_raise_http_error(self,
                                                                         mock_git_get_tag_release_description,
                                                                         mock_git_create_merge_request,
                                                                         mock_git_accept_merge_request):
        mock_git_get_tag_release_description.side_effect = HTTPError('url', 'cde', 'msg', 'hdrs', 'fp')
        with self.assertRaises(HTTPError):
            create_auto_merge_request('gitlab_endpoint', 'gitlab_token', 'project_id', 'source_branch', 'target_branch',
                                      ['user1'], 'tag_name')

    def test_git_get_tag_release_description_fails_must_not_call_git_create_merge_request(self,
                                                                                          mock_git_get_tag_release_description,  # NOQA
                                                                                          mock_git_create_merge_request,  # NOQA
                                                                                          mock_git_accept_merge_request):  # NOQA
        mock_git_get_tag_release_description.side_effect = HTTPError('url', 'cde', 'msg', 'hdrs', 'fp')
        with self.assertRaises(HTTPError):
            self.assertFalse(mock_git_create_merge_request.called, create_auto_merge_request('gitlab_endpoint',
                                                                                             'gitlab_token',
                                                                                             'project_id',
                                                                                             'source_branch',
                                                                                             'target_branch',
                                                                                             ['user1'], 'tag_name'))

    def test_git_create_merge_request_succeeds_must_call_git_accept_merge_request_once(self,
                                                                                       mock_git_get_tag_release_description,  # NOQA
                                                                                       mock_git_create_merge_request,
                                                                                       mock_git_accept_merge_request):
        mock_git_get_tag_release_description.return_value = ['version_changes']
        mock_git_create_merge_request.return_value = 'merge_request_iid'
        create_auto_merge_request('gitlab_endpoint', 'gitlab_token', 'project_id', 'source_branch', 'target_branch',
                                  ['user1'], 'tag_name')
        mock_git_accept_merge_request.assert_called_once_with('gitlab_endpoint', 'gitlab_token', 'project_id',
                                                              'source_branch', 'target_branch', 'merge_request_iid')

    def test_git_create_merge_request_fails_must_raise_http_error(self,
                                                                  mock_git_get_tag_release_description,
                                                                  mock_git_create_merge_request,
                                                                  mock_git_accept_merge_request):
        mock_git_get_tag_release_description.return_value = ['version_changes']
        mock_git_create_merge_request.side_effect = HTTPError('url', 'cde', 'msg', 'hdrs', 'fp')
        with self.assertRaises(HTTPError):
            create_auto_merge_request('gitlab_endpoint', 'gitlab_token', 'project_id', 'source_branch', 'target_branch',
                                      ['user1'], 'tag_name')

    def test_git_create_merge_request_fails_must_not_call_git_accept_merge_request(self,
                                                                                   mock_git_get_tag_release_description,
                                                                                   mock_git_create_merge_request,
                                                                                   mock_git_accept_merge_request):
        mock_git_get_tag_release_description.return_value = ['version_changes']
        mock_git_create_merge_request.side_effect = HTTPError('url', 'cde', 'msg', 'hdrs', 'fp')
        with self.assertRaises(HTTPError):
            self.assertFalse(mock_git_accept_merge_request.called, create_auto_merge_request('gitlab_endpoint',
                                                                                             'gitlab_token',
                                                                                             'project_id',
                                                                                             'source_branch',
                                                                                             'target_branch',
                                                                                             ['user1'],
                                                                                             'tag_name'))

    def test_git_accept_merge_request_fails_must_raise_http_error(self, mock_git_get_tag_release_description,
                                                                  mock_git_create_merge_request,
                                                                  mock_git_accept_merge_request):
        mock_git_get_tag_release_description.return_value = ['version_changes']
        mock_git_create_merge_request.return_value = 'merge_request_iid'
        mock_git_accept_merge_request.side_effect = HTTPError('url', 'cde', 'msg', 'hdrs', 'fp')
        with self.assertRaises(HTTPError):
            create_auto_merge_request('gitlab_endpoint', 'gitlab_token', 'project_id', 'source_branch', 'target_branch',
                                      ['user1'], 'tag_name')


if __name__ == '__main__':
    unittest.main()
