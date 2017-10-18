#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import unittest
from unittest import mock
from urllib.error import HTTPError

from gitlab_changelog import git_create_tag
from tests.unit import BaseTest


@mock.patch('gitlab_changelog.urlopen')
class TestGitCreateTag(BaseTest):
    """This class tests the git_create_tag method"""

    def test_error_on_request_must_raise_http_error(self, mock_urlopen):
        mock_urlopen.side_effect = HTTPError('url', 'cde', 'msg', 'hdrs', 'fp')
        with self.assertRaises(HTTPError):
            git_create_tag('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha',
                           ['version_changes'], 'tag_name')

    def test_must_request_api(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"iid": "iid"}')
        git_create_tag('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha',
                       ['version_changes'], 'tag_name')
        self.assertEqual(mock_urlopen.call_args[0][0].full_url,
                         'https://gitlab.com/api/v4/projects/project_id/repository/tags')

    def test_request_must_contain_header_private_token(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"iid": "iid"}')
        git_create_tag('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha',
                       ['version_changes'], 'tag_name')
        self.assertEqual(mock_urlopen.call_args[0][0].headers['Private-token'], 'gitlab_token')

    def test_request_must_contain_header_content_type(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"iid": "iid"}')
        git_create_tag('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha',
                       ['version_changes'], 'tag_name')
        self.assertEqual(mock_urlopen.call_args[0][0].headers['Content-type'], 'application/json')

    def test_request_must_contain_method_post(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"iid": "iid"}')
        git_create_tag('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha',
                       ['version_changes'], 'tag_name')
        self.assertEqual(mock_urlopen.call_args[0][0].method, 'POST')

    def test_request_must_contain_body_with_tag_name(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"iid": "iid"}')
        git_create_tag('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha',
                       ['version_changes'], 'tag_name')
        decoded_data = mock_urlopen.call_args[0][0].data.decode('utf-8')
        self.assertEqual(json.loads(decoded_data).get('tag_name'), 'tag_name')

    def test_request_must_contain_body_with_ref(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"iid": "iid"}')
        git_create_tag('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha',
                       ['version_changes'], 'tag_name')
        decoded_data = mock_urlopen.call_args[0][0].data.decode('utf-8')
        self.assertEqual(json.loads(decoded_data).get('ref'), 'commit_sha')

    def test_request_must_contain_body_with_release_description(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"iid": "iid"}')
        git_create_tag('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha', ['version_changes'],
                       'tag_name')
        decoded_data = mock_urlopen.call_args[0][0].data.decode('utf-8')
        self.assertEqual(json.loads(decoded_data).get('release_description'),
                         '- version_changes')

    def test_multiple_changes_request_must_contain_body_with_release_description(self, mock_urlopen):
        mock_urlopen.return_value = self.mock_read(b'{"iid": "iid"}')
        git_create_tag('https://gitlab.com', 'gitlab_token', 'project_id', 'commit_sha', ['chng1', 'chng2'], 'tag_name')
        decoded_data = mock_urlopen.call_args[0][0].data.decode('utf-8')
        self.assertEqual(json.loads(decoded_data).get('release_description'), '- chng1\n- chng2')


if __name__ == '__main__':
    unittest.main()
