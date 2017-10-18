#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from unittest import mock
from urllib.error import HTTPError

from ci_helper import git_get_tag_release_description
from tests.unit import BaseTest


@mock.patch('ci_helper.urlopen')
class TestGitGetTagReleaseDescription(BaseTest):
    """This class tests the git_get_tag_release_description method"""

    def test_error_on_request_must_raise_http_error(self, mock_urlopen):
        mock_urlopen.side_effect = HTTPError('url', 'cde', 'msg', 'hdrs', 'fp')
        with self.assertRaises(HTTPError):
            git_get_tag_release_description('https://gitlab.com', 'gitlab_token', 'project_id', 'tag_name')

    def test_must_return_release_description(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"release": {"description": "- release_desc"}}')
        actual = git_get_tag_release_description('https://gitlab.com', 'gitlab_token', 'project_id', 'tag_name')
        self.assertEqual(actual, ['release_desc'])

    def test_no_release_description_must_return_empty_list(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"release": null}')
        actual = git_get_tag_release_description('https://gitlab.com', 'gitlab_token', 'project_id', 'tag_name')
        self.assertEqual(actual, [])

    def test_must_request_api(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"release": {"description": "release_desc"}}')
        git_get_tag_release_description('https://gitlab.com', 'gitlab_token', 'project_id', 'tag_name')
        self.assertEqual(mock_urlopen.call_args[0][0].full_url,
                         'https://gitlab.com/api/v4/projects/project_id/repository/tags/tag_name')

    def test_request_must_contain_header_private_token(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"release": {"description": "release_desc"}}')
        git_get_tag_release_description('https://gitlab.com', 'gitlab_token', 'project_id', 'tag_name')
        self.assertEqual(mock_urlopen.call_args[0][0].headers['Private-token'], 'gitlab_token')

    def test_request_must_contain_header_content_type(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"release": {"description": "release_desc"}}')
        git_get_tag_release_description('https://gitlab.com', 'gitlab_token', 'project_id', 'tag_name')
        self.assertEqual(mock_urlopen.call_args[0][0].headers['Content-type'], 'application/json')

    def test_request_must_contain_method_get(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"release": {"description": "release_desc"}}')
        git_get_tag_release_description('https://gitlab.com', 'gitlab_token', 'project_id', 'tag_name')
        self.assertEqual(mock_urlopen.call_args[0][0].method, 'GET')


if __name__ == '__main__':
    unittest.main()
