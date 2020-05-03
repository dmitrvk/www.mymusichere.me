#!/usr/bin/env python

from datetime import datetime
from shutil import rmtree
from time import sleep
import logging
import os
import requests
import subprocess
import sys

import git
from git.exc import InvalidGitRepositoryError, NoSuchPathError


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MYMUSICHERE_REPO_DIR = os.path.join(BASE_DIR, 'scores', 'lilypond')

MYMUSICHERE_REMOTE = os.environ['MYMUSICHERE_REMOTE']

TOKEN = 'Token %s' % os.environ['PUBLISH_TOKEN']

LOGGING_FORMAT = '%(levelname)s:%(asctime)s:%(module)s:%(message)s'

logger = logging.getLogger(__name__)

def main():
    logger.setLevel(logging.INFO)
    fileHandler = logging.FileHandler(os.path.join(BASE_DIR, 'mymusichere.log'))
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    logger.addHandler(fileHandler)

    logger.info('Check for update')

    try:
        repo = git.Repo(MYMUSICHERE_REPO_DIR)

        if len(sys.argv) > 1 and sys.argv[1] == '--force':
            publish_scores(repo)
        elif updates_available(repo):
            logger.info('Changes detected')
            publish_scores(repo)
        else:
            logger.info('No changes detected')

    except InvalidGitRepositoryError:
        logger.warning('Invalid git repo at %s. Cloning...' % MYMUSICHERE_REPO_DIR)
        rmtree(MYMUSICHERE_REPO_DIR)
        repo = git.Repo.clone_from(MYMUSICHERE_REMOTE, MYMUSICHERE_REPO_DIR, branch='master')
        publish_scores(repo)

    except NoSuchPathError:
        logger.warning('No such path %s. Cloning remote repo...' % MYMUSICHERE_REPO_DIR)
        repo = git.Repo.clone_from(MYMUSICHERE_REMOTE, MYMUSICHERE_REPO_DIR, branch='master')
        publish_scores(repo)

    except Exception as e:
        logger.error('Error: %s' % e)
        sys.exit(1)


def updates_available(repo: git.Repo) -> bool:
    logger.info('git fetch...')
    fetchinfo = repo.remotes.origin.fetch()
    return repo.heads[0].commit != fetchinfo[0].commit


def publish_scores(repo: git.Repo) -> None:
    clean_repo(repo)

    logger.info('git pull...')
    repo.remotes.origin.pull()

    logger.info('make')
    completed_make = subprocess.run(['make'], cwd=MYMUSICHERE_REPO_DIR)

    if completed_make.returncode == 0:
        logger.info('Scores built successfully')
    else:
        logger.error('Scores build failed')
        sys.exit(1)

    response = requests.post(
        'http://localhost:8000/scores/publish',
        headers={'Authorization': TOKEN},
        verify=True
    )

    if response.status_code == 200:
        logger.info(response.content)

        logger.info('make static')
        args = ['make', 'static']
        completed_make_static = subprocess.run(args, cwd=BASE_DIR)

        if completed_make_static.returncode == 0:
            logger.info('Statifiles updated')
        else:
            logger.error('Failed to update static files')
            sys.exit(1)

    else:
        logger.error('Got unexpected status code %d: %s' % (response.status_code, response.content))


def clean_repo(repo: git.Repo) -> None:
    logger.info('Clean repo')

    subprocess.run(['make', 'clean'], cwd=MYMUSICHERE_REPO_DIR)

    if repo.is_dirty():
        logger.info('Repo is dirty. All changes will be removed.')
        repo.git.reset('--hard')


if __name__ == "__main__":
    main()

