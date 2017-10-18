# Gitlab changelog 

[![Build Status](https://travis-ci.org/brunabxs/gitlab-changelog.svg?branch=master)](https://travis-ci.org/brunabxs/gitlab-changelog)

This project aims to help developers to generate incremental versions for a project automatically by Gitlab CI.

## Requirements

It is very important to notice that your project CI must be written in Python 3.5+, otherwise the script will fail.

You will also need a [Personal Access Token](https://docs.gitlab.com/ee/api/README.html#personal-access-tokens) to retrieve information from your commits to generate the changelog. [This article](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) shows how to create a Personal Access Token.

## Usage

1. Copy `ci_helper.py` file to the root of your project.
2. [Generate a SSH key](https://docs.gitlab.com/ee/ssh/README.html).
3. Create environment variables:
    - *GITLAB_API_ENDPOINT* (optional): Must contain the Gitlab endpoint. Do not use / at the end. (e.g.: _https://gitlab.com_).
    - *GITLAB_PERSONAL_ACCESS_TOKEN* (optional): Must contain your Personal Access Token.
    - *SSH_PRIVATE_KEY*: Must contain the [SSH private key](https://docs.gitlab.com/ee/ci/ssh_keys/README.html#ssh-keys-when-using-the-docker-executor) if you are using GitLab shared runners.
3. Add a [Deploy key](https://docs.gitlab.com/ee/ssh/README.html#deploy-keys) with the SSH public key.
4. Update your `.gitlab-ci.yml` to execute `ci_helper.py` when a commit is made:
```yml
...
script:
  - python ci_helper.py "${GITLAB_API_ENDPOINT}" "${GITLAB_PERSONAL_ACCESS_TOKEN}" "${CI_PROJECT_ID}" "${CI_COMMIT_SHA}"
...
```

**Note**: You can use `.gitlab-ci.example.yml` as an example.
