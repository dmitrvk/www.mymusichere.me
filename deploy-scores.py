#!/usr/bin/env python

import mymusichere.settings as settings
from git import Repo
from time import sleep
import subprocess
import logging
import os
from datetime import datetime
import requests

logfile = os.path.join(settings.BASE_DIR, 'deploy-scores.log')
logging.basicConfig(filename=logfile, level=logging.INFO)

repo = Repo(settings.MYMUSICHERE_REPO_DIR)

while True:
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info('%s:Check for update' % time)

    logging.info('git fetch...')
    fetchinfo = repo.remotes.origin.fetch()

    is_up_to_date = fetchinfo[0].flags & fetchinfo[0].HEAD_UPTODATE

    if repo.heads[0].commit == fetchinfo[0].commit:
        logging.info('No changes detected')
    else:
        logging.info('Changes detected')

        logging.info('Clean repo')

        working_dir = repo.working_tree_dir
        subprocess.run(['make', 'clean'], cwd=working_dir)

        if repo.is_dirty():
            logging.info('Repo is dirty. All changes will be removed.')
            repo.git.reset('--hard')

        logging.info('git pull...')
        repo.remotes.origin.pull()

        logging.info('make')
        completed_make = subprocess.run(['make'], cwd=repo.working_dir)

        if completed_make.returncode == 0:
            logging.info('Scores built successfully')
        else:
            logging.info('Scores build failed')
            #continue

        token = 'Token %s' % settings.DEPLOY_TOKEN

        response = requests.post(
            'http://localhost:8000/scores/deploy',
            headers={'Authorization': token}
        )

        if response.status_code == 200:
            logging.info(response.content)

            logging.info('make static')
            args = ['make', 'static']
            completed_make_static = subprocess.run(args, cwd=working_dir)

            if completed_make_static.returncode == 0:
                logging.info('Statifiles updated')
            else:
                logging.info('Failed to update static files')

        else:
          logging.info('Got unexpected status code {}: {!r}'.format(response.status_code, response.content))

    sleep(30)
