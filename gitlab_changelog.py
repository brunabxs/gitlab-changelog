#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import re
import subprocess

from datetime import datetime
from urllib.request import Request, urlopen


class CommitError(Exception):
    """Commit error"""
    pass

class InvalidVersion(Exception):
    """Invalid version"""
    pass

class PushError(Exception):
    """Push error"""
    pass

class TagError(Exception):
    """Tag error"""
    pass


def publish_version(gitlab_endpoint, gitlab_token, project_id, commit_sha):
    new_version = generate_version(version=get_current_version('CHANGELOG.md'), version_type='patch')
    generate_changelog(version=new_version,
                       version_changes=get_version_changes(gitlab_endpoint, gitlab_token, project_id, commit_sha),
                       changelog_file_path='CHANGELOG.md')
    git_commit()
    git_tag(new_version)
    git_push()


def get_current_version(changelog_file_path):
    """It reads the file content and extracts the current version

    :param str changelog_file_path: The file path
    :rtype: str
    :return: The current version
    """
    with open(changelog_file_path, mode='r') as file:
        first_line = file.readline()
        version_search = re.search(r'(\d+\.\d+\.\d+(-rc\.\d+)?)', first_line, re.IGNORECASE)
        return version_search.group(0) if version_search else ''


def generate_version(version='', version_type='patch'):
    """It generates a version based on given version and version type

    :param str version: The actual version
    :param str version_type: The type of the version. Can be 'major', 'minor', 'patch' or 'rc'
    :rtype: str
    :return: The generated version
    :raise InvalidVersion: If no version could be found
    """
    if not version and version_type == 'rc':
        version = '0.0.1-rc.0'
    elif not version:
        version = '0.0.0'

    version_search = re.search(r'(\d+)\.(\d+)\.(\d+)', version, re.IGNORECASE)
    if version_search is None:
        raise InvalidVersion('Invalid version')
    major, minor, patch = version_search.groups()

    if version_type == 'patch':
        return '{}.{}.{}'.format(major, minor, int(patch) + 1)
    if version_type == 'minor':
        return '{}.{}.0'.format(major, int(minor) + 1)
    if version_type == 'major':
        return '{}.0.0'.format(int(major) + 1)
    if version_type == 'rc':
        version_search = re.search(r'-rc\.(\d+)', version, re.IGNORECASE)
        rc = version_search.group(1) if version_search else 0
        return '{}.{}.{}-rc.{}'.format(major, minor, patch, int(rc) + 1)


def get_version_changes(gitlab_endpoint, gitlab_token, project_id, commit_sha):
    """It retrieves the relevant changes since the last version

    Note: If the given SHA belongs to a commit (or merge), the returned changes will be the commit title.
    On the other hand, if the given SHA belongs to a merge request, the returned changes will be the MR description.

    :param str gitlab_endpoint: The gitlab api endpoint
    :param str gitlab_token: The gitlab api token
    :param str project_id: The project identifier
    :param str commit_sha: The commit SHA
    :rtype: list
    :return: A list containing the relevant changes since last version or None
    """
    merge_request_changes = get_merge_request_changes(
        gitlab_endpoint, gitlab_token, project_id, commit_sha)

    if merge_request_changes:
        return merge_request_changes

    return get_commit_changes(gitlab_endpoint, gitlab_token, project_id, commit_sha)


def get_merge_request_changes(gitlab_endpoint, gitlab_token, project_id, commit_sha):
    """It retrieves the merge request relevant changes

    :param str gitlab_endpoint: The gitlab api endpoint
    :param str gitlab_token: The gitlab api token
    :param str project_id: The project identifier
    :param str commit_sha: The commit SHA
    :rtype: list
    :return: A list containing the merge request relevant changes
    """
    request = Request('{}/api/v4/projects/{}/merge_requests'.format(gitlab_endpoint, project_id),
                      headers={
                          'PRIVATE-TOKEN': gitlab_token
                      })
    response = urlopen(request).read()
    merge_requests = json.loads(response)

    for merge_request in merge_requests:
        if merge_request.get('merge_commit_sha') == commit_sha:
            if merge_request.get('description'):
                return [merge_request.get('description')]
                # TODO: remove merge request title and other changes that should not compose the merge request description
            break
    return []


def get_commit_changes(gitlab_endpoint, gitlab_token, project_id, commit_sha):
    """It retrieves the commit relevant changes

    :param str gitlab_endpoint: The gitlab api endpoint
    :param str gitlab_token: The gitlab api token
    :param str project_id: The project identifier
    :param str commit_sha: The commit SHA
    :rtype: list
    :return: A list containing the commit relevant changes
    """
    request = Request('{}/api/v4/projects/{}/repository/commits/{}'.format(gitlab_endpoint, project_id, commit_sha),
                      headers={
                          'PRIVATE-TOKEN': gitlab_token
                      })
    response = urlopen(request).read()
    commit = json.loads(response)
    return [commit.get('title')] if commit.get('title') else []


def generate_changelog(version, version_changes, changelog_file_path):
    """It prepends a changelog entry to the given changelog file

    A changelog entry is composed by:
    - The version
    - The version changes
    - The current date

    :param str version: The version
    :param str version_changes: The version changes
    :param str changelog_file: The chagelog file path
    """
    # TODO: probably need to import pytz - uncomment test when finished
    now = datetime.strftime(datetime.now(), '%a, %b %d %Y %H:%M:%S %z %Z')
    with open(changelog_file_path, mode='wr') as file:
        content = file.read()
        entry_skeleton = '{}\n  {}\n{}\n\n{}'
        file.write(entry_skeleton.format(version, version_changes, now, content))


def git_commit():
    """It commits the changelog changes

    :raise CommitError: If any error happends during commit
    """
    process = subprocess.Popen(['git', 'commit', '-am', 'Update changelog'], stdout=subprocess.PIPE)
    return_code = process.wait()
    if return_code != 0:
        raise CommitError(return_code)


def git_tag(tag):
    """It generates a tag

    :param str tag: The tag name
    :raise TagError: If any error happends during tag
    """
    process = subprocess.Popen(['git', 'tag', tag], stdout=subprocess.PIPE)
    return_code = process.wait()
    if return_code != 0:
        raise TagError(return_code)


def git_push():
    """It pushes t=commits and tags to repository

    :raise PushError: If any error happends during push
    """
    process = subprocess.Popen(['git', 'push', 'origin', 'master'], stdout=subprocess.PIPE)
    return_code = process.wait()
    if return_code != 0:
        raise PushError(return_code)
    process = subprocess.Popen(['git', 'push', 'origin', 'master', '--tags'], stdout=subprocess.PIPE)
    return_code = process.wait()
    if return_code != 0:
        raise PushError(return_code)
