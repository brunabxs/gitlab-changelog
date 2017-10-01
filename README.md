# Gitlab changelog 

[![Build Status](https://travis-ci.org/brunabxs/gitlab-changelog.svg?branch=master)](https://travis-ci.org/brunabxs/gitlab-changelog)

This project aims to help developers to generate incremental versions for a project automatically by Gitlab CI.

## Requirements

It is very important to notice that your project CI must be written in Python 3.5+, otherwise the script will fail.

You will also need a [Personal Access Token](https://docs.gitlab.com/ee/api/README.html#personal-access-tokens) to retrieve information from your commits to generate the changelog. [This article](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) shows how to create a Personal Access Token.



## Usage

1. Copy `gitlab_changelog.py` file to the root of your project.
2. Create two environment variables (optional):
    - *GITLAB_API_ENDPOINT*: Must contain the Gitlab API endpoint (e.g.: _https://gitlab.com/api/v4_)
    - *GITLAB_PERSONAL_ACCESS_TOKEN*: Must contain your Personal Access Token
3. Update your `.gitlab-ci.yml` to execute `gitlab_changelog.py` when a commit is made:
```yml
...
script:
  - python gitlab_changelog.py "${GITLAB_API_ENDPOINT}" "${GITLAB_PERSONAL_ACCESS_TOKEN}" "${CI_PROJECT_ID}" "${CI_COMMIT_SHA}"
...
```
