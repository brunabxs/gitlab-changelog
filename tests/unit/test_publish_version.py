#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from unittest import mock

from gitlab_changelog import publish_version, CommitError, PushError, TagError


@mock.patch('gitlab_changelog.git_push')
@mock.patch('gitlab_changelog.git_tag')
@mock.patch('gitlab_changelog.git_commit')
@mock.patch('gitlab_changelog.generate_changelog')
@mock.patch('gitlab_changelog.get_version_changes', return_value=['change'])
@mock.patch('gitlab_changelog.generate_version', return_value='1.2.3-rc.1')
@mock.patch('gitlab_changelog.get_current_version', return_value='1.2.3')
class TestPublishVersion(unittest.TestCase):
    """This class tests the publish_version method"""

    def test_must_call_get_current_version_once(self, mock_get_current_version, mock_generate_version, mock_get_version_changes, mock_generate_changelog, mock_git_commit, mock_git_tag, mock_git_push):
        publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha')
        mock_get_current_version.assert_called_once()

    def test_must_call_generate_version_once(self, mock_get_current_version, mock_generate_version, mock_get_version_changes, mock_generate_changelog, mock_git_commit, mock_git_tag, mock_git_push):
        publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha')
        mock_generate_version.assert_called_once_with(version='1.2.3', version_type='patch')

    def test_must_call_get_version_changes_once(self, mock_get_current_version, mock_generate_version, mock_get_version_changes, mock_generate_changelog, mock_git_commit, mock_git_tag, mock_git_push):
        publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha')
        mock_get_version_changes.assert_called_once()

    def test_must_call_generate_changelog_once(self, mock_get_current_version, mock_generate_version, mock_get_version_changes, mock_generate_changelog, mock_git_commit, mock_git_tag, mock_git_push):
        publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha')
        mock_generate_changelog.assert_called_once_with(version='1.2.3-rc.1', version_changes=['change'], changelog_file_path='CHANGELOG.md')

    def test_must_call_git_commit_once(self, mock_get_current_version, mock_generate_version, mock_get_version_changes, mock_generate_changelog, mock_git_commit, mock_git_tag, mock_git_push):
        publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha')
        mock_git_commit.assert_called_once()

    def test_git_commit_succeeds_must_call_git_tag_once(self, mock_get_current_version, mock_generate_version, mock_get_version_changes, mock_generate_changelog, mock_git_commit, mock_git_tag, mock_git_push):
        publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha')
        mock_git_tag.assert_called_once_with('1.2.3-rc.1')

    def test_git_commit_fails_must_raise_commit_error(self, mock_get_current_version, mock_generate_version, mock_get_version_changes, mock_generate_changelog, mock_git_commit, mock_git_tag, mock_git_push):
        mock_git_commit.side_effect = CommitError
        with self.assertRaises(CommitError):
            publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha')

    def test_git_commit_fails_must_not_call_git_tag(self, mock_get_current_version, mock_generate_version, mock_get_version_changes, mock_generate_changelog, mock_git_commit, mock_git_tag, mock_git_push):
        mock_git_commit.side_effect = CommitError
        with self.assertRaises(CommitError):
            self.assertFalse(mock_git_tag.called, publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha'))

    def test_git_commit_fails_must_not_call_git_push(self, mock_get_current_version, mock_generate_version, mock_get_version_changes, mock_generate_changelog, mock_git_commit, mock_git_tag, mock_git_push):
        mock_git_commit.side_effect = CommitError
        with self.assertRaises(CommitError):
            self.assertFalse(mock_git_push.called, publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha'))

    def test_git_tag_succeeds_must_call_git_push_once(self, mock_get_current_version, mock_generate_version, mock_get_version_changes, mock_generate_changelog, mock_git_commit, mock_git_tag, mock_git_push):
        publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha')
        mock_git_push.assert_called_once()

    def test_git_tag_fails_must_raise_tag_error(self, mock_get_current_version, mock_generate_version, mock_get_version_changes, mock_generate_changelog, mock_git_commit, mock_git_tag, mock_git_push):
        mock_git_tag.side_effect = TagError
        with self.assertRaises(TagError):
            publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha')

    def test_git_tag_fails_must_not_call_git_push(self, mock_get_current_version, mock_generate_version, mock_get_version_changes, mock_generate_changelog, mock_git_commit, mock_git_tag, mock_git_push):
        mock_git_tag.side_effect = TagError
        with self.assertRaises(TagError):
            self.assertFalse(mock_git_push.called, publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha'))

    def test_git_push_fails_must_raise_push_error(self, mock_get_current_version, mock_generate_version, mock_get_version_changes, mock_generate_changelog, mock_git_commit, mock_git_tag, mock_git_push):
        mock_git_push.side_effect = PushError
        with self.assertRaises(PushError):
            publish_version('gitlab_endpoint', 'gitlab_token', 'project_id', 'commit_sha')


if __name__ == '__main__':
    unittest.main()
