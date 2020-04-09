#!/usr/bin/env python

from datetime import datetime
from shutil import rmtree
from time import sleep
import logging
import os
import subprocess
import sys

from git import Repo
from git.exc import InvalidGitRepositoryError, NoSuchPathError
import requests


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MYMUSICHERE_REPO_DIR = os.path.join(BASE_DIR, 'scores', 'lilypond')

MYMUSICHERE_REMOTE = os.environ['MYMUSICHERE_REMOTE']

TOKEN = 'Token %s' % os.environ['DEPLOY_TOKEN']


def main():
    logfile = os.path.join(BASE_DIR, 'deploy-scores.log')
    logging.basicConfig(filename=logfile, level=logging.INFO)

    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info('%s:Check for update' % time)

    try:
        repo = Repo(MYMUSICHERE_REPO_DIR)

        if len(sys.argv) > 1 and sys.argv[1] == '--force':
            deploy_scores(repo)
        elif updates_available(repo):
            logging.info('Changes detected')
            deploy_scores(repo)
        else:
            logging.info('No changes detected')

    except InvalidGitRepositoryError:
        logging.warning('Invalid git repo at %s. Cloning...' % MYMUSICHERE_REPO_DIR)
        rmtree(MYMUSICHERE_REPO_DIR)
        repo = Repo.clone_from(MYMUSICHERE_REMOTE, MYMUSICHERE_REPO_DIR, branch='master')
        deploy_scores(repo)

    except NoSuchPathError:
        logging.warning('No such path %s. Cloning remote repo...' % MYMUSICHERE_REPO_DIR)
        repo = Repo.clone_from(MYMUSICHERE_REMOTE, MYMUSICHERE_REPO_DIR, branch='master')
        deploy_scores(repo)

    except Exception as e:
        logging.error('Error: %s' % e)
        sys.exit(1)


def updates_available(repo):
    logging.info('git fetch...')
    fetchinfo = repo.remotes.origin.fetch()
    return repo.heads[0].commit != fetchinfo[0].commit


def deploy_scores(repo):
    clean_repo(repo)

    logging.info('git pull...')
    repo.remotes.origin.pull()

    logging.info('make')
    completed_make = subprocess.run(['make'], cwd=MYMUSICHERE_REPO_DIR)

    if completed_make.returncode == 0:
        logging.info('Scores built successfully')
    else:
        logging.error('Scores build failed')
        sys.exit(1)

    response = requests.post(
        'http://localhost:8000/scores/deploy',
        headers={'Authorization': TOKEN},
        verify=True
    )

    if response.status_code == 200:
        logging.info(response.content)

        logging.info('make static')
        args = ['make', 'static']
        completed_make_static = subprocess.run(args, cwd=BASE_DIR)

        if completed_make_static.returncode == 0:
            logging.info('Statifiles updated')
        else:
            logging.error('Failed to update static files')
            sys.exit(1)

    else:
        logging.error('Got unexpected status code %d: %s' % (response.status_code, response.content))


def clean_repo(repo):
    logging.info('Clean repo')

    subprocess.run(['make', 'clean'], cwd=MYMUSICHERE_REPO_DIR)

    if repo.is_dirty():
        logging.info('Repo is dirty. All changes will be removed.')
        repo.git.reset('--hard')


if __name__ == "__main__":
    main()

