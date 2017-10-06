#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import json
import re
import ssl
import subprocess

from datetime import datetime
from urllib.request import Request, urlopen


class CommitError(Exception):
    """Commit error"""
    pass


class InvalidVersion(Exception):
    """Invalid version"""
    pass


class NoChanges(Exception):
    """No Changes"""
    pass


class PushError(Exception):
    """Push error"""
    pass


class TagError(Exception):
    """Tag error"""
    pass


def main(args):
    """Main function"""
    publish_version(gitlab_endpoint=args['gitlab_endpoint'], gitlab_token=args['gitlab_token'],
                    project_id=args['project_id'], commit_sha=args['commit_sha'],
                    target_branch=args['target_branch'], changelog_file_path=args['changelog_file_path'])


def publish_version(gitlab_endpoint, gitlab_token, project_id, commit_sha, target_branch, changelog_file_path):
    """It generates a version for the given project

    :param str gitlab_endpoint: The gitlab api endpoint
    :param str gitlab_token: The gitlab api token
    :param str project_id: The project identifier
    :param str commit_sha: The commit SHA
    :param str target_branch: The target branch name
    :param str changelog_file_path: The changelog file path
    :raise HTTPError: If there is an error in HTTP request
    """
    # TODO: define when version type is major, minor or patch
    version_type = 'patch'
    if target_branch == 'develop':
        version_type = 'rc'

    new_version = generate_version(version=get_current_version(changelog_file_path), version_type=version_type)
    new_version_changes = get_version_changes(gitlab_endpoint, gitlab_token, project_id, commit_sha)
    generate_changelog(version=new_version, version_changes=new_version_changes,
                       changelog_file_path=changelog_file_path)
    git_commit(target_branch, changelog_file_path)
    git_tag(new_version)
    git_push(target_branch)
    git_merge_request(gitlab_endpoint, gitlab_token, project_id, target_branch, new_version_changes)


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
    :raise HTTPError: If there is an error in HTTP request
    """
    merge_request_changes = get_merge_request_changes(gitlab_endpoint, gitlab_token, project_id, commit_sha)
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
    :raise HTTPError: If there is an error in HTTP request
    """
    merge_requests = _request('{}/api/v4/projects/{}/merge_requests'.format(gitlab_endpoint, project_id),
                              gitlab_token=gitlab_token, method='GET')
    for merge_request in merge_requests:
        if merge_request.get('merge_commit_sha') == commit_sha:
            if merge_request.get('description'):
                return clean_content(merge_request.get('description'))
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
    :raise HTTPError: If there is an error in HTTP request
    """
    commit = _request('{}/api/v4/projects/{}/repository/commits/{}'.format(gitlab_endpoint, project_id, commit_sha),
                      gitlab_token=gitlab_token, method='GET')
    return clean_content(commit.get('title'))


def clean_content(text):
    """It split the given text into a list of items and keeps only those items that represents version changes

    :param str text: The text
    :rtype: list
    :return: A list containing relevant version changes
    """
    if not text:
        return []
    items = text.split('\n')
    # remove white spaces
    items = [item.strip() for item in items]
    # remove members reference
    items = [re.sub(r'^-\s*\[[xX\s]*\]\s*@\s*[a-zA-Z0-9\.\-]+', '', item).strip() for item in items]
    # remove starting '- - -', '* * *', '--', '-*', '**'
    items = [re.sub(r'^([-\*]\s*)+', '', item).strip() for item in items]
    # remove empty items
    return [item for item in items if item]


def generate_changelog(version, version_changes, changelog_file_path):
    """It prepends a changelog entry to the given changelog file

    A changelog entry is composed by:
    - The version
    - The version changes
    - The current date

    :param str version: The version
    :param list version_changes: The version changes
    :param str changelog_file_path: The changelog file path
    :raise NoChanges: If version changes is empty
    """
    if version_changes:
        now = datetime.strftime(datetime.now(), '%a, %b %d %Y %H:%M:%S %z %Z')
        with open(changelog_file_path, mode='r') as file:
            content = file.read()
        with open(changelog_file_path, mode='w') as file:
            entry_skeleton = '{}\n\n{}\n\n{}\n\n{}'
            changes = '  - {}'.format('\n  - '.join(version_changes))
            file.write(entry_skeleton.format(version, changes, now, content))
    else:
        raise NoChanges()


def git_commit(target_branch, changelog_file_path):
    """It commits the changelog changes

    :param str target_branch: The target branch name
    :param str changelog_file_path: The changelog file path
    :raise CommitError: If any error happends during commit
    """
    process = subprocess.Popen(['git', 'add', changelog_file_path], stdout=subprocess.PIPE)
    return_code = process.wait()
    if return_code != 0:
        raise CommitError(return_code)
    process = subprocess.Popen(['git', 'commit', '-m', 'Update changelog ({})'.format(target_branch)],
                               stdout=subprocess.PIPE)
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


def git_push(target_branch):
    """It pushes commits and tags to repository

    :param str target_branch: The target branch name
    :raise PushError: If any error happends during push
    """
    process = subprocess.Popen(['git', 'push', 'origin', target_branch], stdout=subprocess.PIPE)
    return_code = process.wait()
    if return_code != 0:
        raise PushError(return_code)
    process = subprocess.Popen(['git', 'push', 'origin', target_branch, '--tags'], stdout=subprocess.PIPE)
    return_code = process.wait()
    if return_code != 0:
        raise PushError(return_code)


def git_merge_request(gitlab_endpoint, gitlab_token, project_id, target_branch, version_changes):
    """It creates and approves a merge request depending on the target branch

    :param str gitlab_endpoint: The gitlab api endpoint
    :param str gitlab_token: The gitlab api token
    :param str project_id: The project identifier
    :param str target_branch: The target branch name
    :param list version_changes: The version changes
    :rtype: str
    :return: The created merge request iid
    :raise HTTPError: If there is an error in HTTP request
    """
    if target_branch != 'master':
        return
    merge_request_iid = git_create_merge_request(gitlab_endpoint, gitlab_token, project_id, version_changes)
    git_accept_merge_request(gitlab_endpoint, gitlab_token, project_id, merge_request_iid)


def git_create_merge_request(gitlab_endpoint, gitlab_token, project_id, version_changes):
    """It creates a merge request depending on the target branch

    :param str gitlab_endpoint: The gitlab api endpoint
    :param str gitlab_token: The gitlab api token
    :param str project_id: The project identifier
    :param list version_changes: The version changes
    :rtype: str
    :return: The created merge request iid
    :raise HTTPError: If there is an error in HTTP request
    """
    # TODO: Parameterize user info
    # TODO: Check if branch develop exists, otherwise skip this
    # TODO: If merge request cannot be created because there is one (status code = ???) the build fails
    merge_request = _request('{}/api/v4/projects/{}/merge_requests'.format(gitlab_endpoint, project_id),
                             gitlab_token=gitlab_token, method='POST',
                             data={'source_branch': 'master', 'target_branch': 'develop',
                                   'title': 'Automatic merge branch \'master\' into \'develop\'',
                                   'description': '- {}\n\n- - - \n\n- [ ] @brunabxs'
                                                  .format('\n- '.join(version_changes))})
    return merge_request['iid']


def git_accept_merge_request(gitlab_endpoint, gitlab_token, project_id, merge_request_iid):
    """It accepts a merge request

    :param str gitlab_endpoint: The gitlab api endpoint
    :param str gitlab_token: The gitlab api token
    :param str project_id: The project identifier
    :param str merge_request_iid: The merge request iid to approve
    :raise HTTPError: If there is an error in HTTP request
    """
    # TODO: Check if merge request exists otherwise skip this
    # TODO: If merge request cannot be accepted because there are conclicts (status code = 405) the build fails
    _request('{}/api/v4/projects/{}/merge_requests/{}/merge'.format(gitlab_endpoint, project_id, merge_request_iid),
             gitlab_token=gitlab_token, method='PUT',
             data={'merge_commit_message': 'Automatic merge branch \'master\' into \'develop\''})


def _request(url, gitlab_token, method='GET', data=None):
    request = Request(url, headers={'PRIVATE-TOKEN': gitlab_token, 'content-type': 'application/json'},
                      method=method, data=json.dumps(data).encode('utf-8') if data else None)
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    response = urlopen(request, context=context).read().decode('utf-8')
    return json.loads(response)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate changelog for a given commit')

    parser.add_argument('-ge', '--gitlab_endpoint', dest='gitlab_endpoint', type=str,
                        help='The gitlab api endpoint', required=True)
    parser.add_argument('-gt', '--gitlab_token', dest='gitlab_token', type=str,
                        help='The gitlab public access token', required=True)
    parser.add_argument('-proj', '--project_id', dest='project_id', type=str,
                        help='The gitlab project identifier', required=True)
    parser.add_argument('-sha', '--commit_sha', dest='commit_sha', type=str,
                        help='The commit SHA', required=True)
    parser.add_argument('-b', '--target_branch', dest='target_branch', type=str,
                        help='The commit target branch', required=True)
    parser.add_argument('-f', '--changelog_file', dest='changelog_file_path', type=str,
                        help='The changelog file path', default='CHANGELOG.md')
    main(vars(parser.parse_args()))
