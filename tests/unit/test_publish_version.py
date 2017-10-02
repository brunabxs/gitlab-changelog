#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from unittest import mock
from urllib.error import HTTPError

from gitlab_changelog import publish_version, CommitError, PushError, TagError


@mock.patch('gitlab_changelog.git_merge_request')
@mock.patch('gitlab_changelog.git_push')
@mock.patch('gitlab_changelog.git_tag')
@mock.patch('gitlab_changelog.git_commit')
@mock.patch('gitlab_changelog.generate_changelog')
@mock.patch('gitlab_changelog.get_version_changes', return_value=['change'])
@mock.patch('gitlab_changelog.generate_version', return_value='1.2.3-rc.1')
@mock.patch('gitlab_changelog.get_current_version', return_value='1.2.3')
class TestPublishVersion(unittest.TestCase):
    """This class tests the publish_version method"""

    def test_must_call_get_current_version_once(self, mock_get_current_version, mock_generate_version,
                                                mock_get_version_changes, mock_generate_changelog,
                                                mock_git_commit, mock_git_tag, mock_git_push,
                                                mock_git_merge_request):
        publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha', 'branch', 'file')
        mock_get_current_version.assert_called_once_with('file')

    def test_branch_develop_must_call_generate_version_with_rc(self, mock_get_current_version,
                                                               mock_generate_version, mock_get_version_changes,
                                                               mock_generate_changelog, mock_git_commit,
                                                               mock_git_tag, mock_git_push,
                                                               mock_git_merge_request):
        publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha', 'develop', 'file')
        mock_generate_version.assert_called_once_with(version='1.2.3', version_type='rc')

    def test_branch_not_develop_must_call_generate_version_with_patch(self, mock_get_current_version,
                                                                      mock_generate_version, mock_get_version_changes,
                                                                      mock_generate_changelog, mock_git_commit,
                                                                      mock_git_tag, mock_git_push,
                                                                      mock_git_merge_request):
        publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha', 'branch', 'file')
        mock_generate_version.assert_called_once_with(version='1.2.3', version_type='patch')

    def test_must_call_get_version_changes_once(self, mock_get_current_version, mock_generate_version,
                                                mock_get_version_changes, mock_generate_changelog,
                                                mock_git_commit, mock_git_tag, mock_git_push,
                                                mock_git_merge_request):
        publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha', 'branch', 'file')
        mock_get_version_changes.assert_called_once_with('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha')

    def test_get_version_succeeds_must_call_generate_changelog_once(self, mock_get_current_version,
                                                                    mock_generate_version, mock_get_version_changes,
                                                                    mock_generate_changelog, mock_git_commit,
                                                                    mock_git_tag, mock_git_push,
                                                                    mock_git_merge_request):
        publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha', 'branch', 'file')
        mock_generate_changelog.assert_called_once_with(version='1.2.3-rc.1',
                                                        version_changes=['change'],
                                                        changelog_file_path='file')

    def test_get_version_fails_must_raise_http_error(self, mock_get_current_version,
                                                     mock_generate_version, mock_get_version_changes,
                                                     mock_generate_changelog, mock_git_commit,
                                                     mock_git_tag, mock_git_push,
                                                     mock_git_merge_request):
        mock_get_version_changes.side_effect = HTTPError('url', 'cde', 'msg', 'hdrs', 'fp')
        with self.assertRaises(HTTPError):
            publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha', 'branch', 'file')

    def test_get_version_fails_must_not_call_generate_changelog_once(self, mock_get_current_version,
                                                                     mock_generate_version, mock_get_version_changes,
                                                                     mock_generate_changelog, mock_git_commit,
                                                                     mock_git_tag, mock_git_push,
                                                                     mock_git_merge_request):
        mock_get_version_changes.side_effect = HTTPError('url', 'cde', 'msg', 'hdrs', 'fp')
        with self.assertRaises(HTTPError):
            self.assertFalse(mock_generate_changelog.called, publish_version(
                'gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha', 'branch', 'file'))

    def test_must_call_git_commit_once(self, mock_get_current_version, mock_generate_version,
                                       mock_get_version_changes, mock_generate_changelog,
                                       mock_git_commit, mock_git_tag, mock_git_push,
                                       mock_git_merge_request):
        publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha', 'branch', 'file')
        mock_git_commit.assert_called_once_with('branch', 'file')

    def test_git_commit_succeeds_must_call_git_tag_once(self, mock_get_current_version, mock_generate_version,
                                                        mock_get_version_changes, mock_generate_changelog,
                                                        mock_git_commit, mock_git_tag, mock_git_push,
                                                        mock_git_merge_request):
        publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha', 'branch', 'file')
        mock_git_tag.assert_called_once_with('1.2.3-rc.1')

    def test_git_commit_fails_must_raise_commit_error(self, mock_get_current_version, mock_generate_version,
                                                      mock_get_version_changes, mock_generate_changelog,
                                                      mock_git_commit, mock_git_tag, mock_git_push,
                                                      mock_git_merge_request):
        mock_git_commit.side_effect = CommitError
        with self.assertRaises(CommitError):
            publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha', 'branch', 'file')

    def test_git_commit_fails_must_not_call_git_tag(self, mock_get_current_version, mock_generate_version,
                                                    mock_get_version_changes, mock_generate_changelog,
                                                    mock_git_commit, mock_git_tag, mock_git_push,
                                                    mock_git_merge_request):
        mock_git_commit.side_effect = CommitError
        with self.assertRaises(CommitError):
            self.assertFalse(mock_git_tag.called, publish_version(
                'gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha', 'branch', 'file'))

    def test_git_commit_fails_must_not_call_git_push(self, mock_get_current_version, mock_generate_version,
                                                     mock_get_version_changes, mock_generate_changelog,
                                                     mock_git_commit, mock_git_tag, mock_git_push,
                                                     mock_git_merge_request):
        mock_git_commit.side_effect = CommitError
        with self.assertRaises(CommitError):
            self.assertFalse(mock_git_push.called, publish_version(
                'gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha', 'branch', 'file'))

    def test_git_tag_succeeds_must_call_git_push_once(self, mock_get_current_version, mock_generate_version,
                                                      mock_get_version_changes, mock_generate_changelog,
                                                      mock_git_commit, mock_git_tag, mock_git_push,
                                                      mock_git_merge_request):
        publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha', 'branch', 'file')
        mock_git_push.assert_called_once_with('branch')

    def test_git_tag_fails_must_raise_tag_error(self, mock_get_current_version, mock_generate_version,
                                                mock_get_version_changes, mock_generate_changelog,
                                                mock_git_commit, mock_git_tag, mock_git_push,
                                                mock_git_merge_request):
        mock_git_tag.side_effect = TagError
        with self.assertRaises(TagError):
            publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha', 'branch', 'file')

    def test_git_tag_fails_must_not_call_git_push(self, mock_get_current_version, mock_generate_version,
                                                  mock_get_version_changes, mock_generate_changelog,
                                                  mock_git_commit, mock_git_tag, mock_git_push,
                                                  mock_git_merge_request):
        mock_git_tag.side_effect = TagError
        with self.assertRaises(TagError):
            self.assertFalse(mock_git_push.called, publish_version(
                'gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha', 'branch', 'file'))

    def test_git_push_succeeds_must_call_git_merge_request_once(self, mock_get_current_version, mock_generate_version,
                                                                mock_get_version_changes, mock_generate_changelog,
                                                                mock_git_commit, mock_git_tag, mock_git_push,
                                                                mock_git_merge_request):
        publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha', 'branch', 'file')
        mock_git_merge_request.assert_called_once_with('gitlab_endpoint', 'gitlab_token', 'project_id', 'branch',
                                                       ['change'])

    def test_git_push_fails_must_raise_push_error(self, mock_get_current_version, mock_generate_version,
                                                  mock_get_version_changes, mock_generate_changelog,
                                                  mock_git_commit, mock_git_tag, mock_git_push,
                                                  mock_git_merge_request):
        mock_git_push.side_effect = PushError
        with self.assertRaises(PushError):
            publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha', 'branch', 'file')

    def test_git_push_fails_must_not_call_git_merge_request(self, mock_get_current_version, mock_generate_version,
                                                            mock_get_version_changes, mock_generate_changelog,
                                                            mock_git_commit, mock_git_tag, mock_git_push,
                                                            mock_git_merge_request):
        mock_git_push.side_effect = PushError
        with self.assertRaises(PushError):
            self.assertFalse(mock_git_merge_request.called, publish_version(
                'gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha', 'branch', 'file'))

    def test_git_merge_request_fails_must_raise_http_error(self, mock_get_current_version, mock_generate_version,
                                                           mock_get_version_changes, mock_generate_changelog,
                                                           mock_git_commit, mock_git_tag, mock_git_push,
                                                           mock_git_merge_request):
        mock_git_merge_request.side_effect = HTTPError('url', 'cde', 'msg', 'hdrs', 'fp')
        with self.assertRaises(HTTPError):
            publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha', 'branch', 'file')


if __name__ == '__main__':
    unittest.main()
