import os
import re
import subprocess
import glob
import os.path
from queue import Queue
from threading import Thread
import logging

from subprocess import Popen, PIPE

from functools import partial
from multiprocessing.pool import Pool
from time import time

REPO_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DOCKERFILES_DIR = f'{REPO_DIR}/dockerfiles'

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logging.getLogger('requests').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)


def all_dockerfiles():
    return [
        filename.split(f'{REPO_DIR}/')[-1] for filename in glob.iglob(f'{DOCKERFILES_DIR}/**', recursive=True)
        if "Dockerfile" in filename
    ]


def changed_dockerfiles():
    """Return a list of Dockerfiles that have been changed since last commit."""
    logging.info('Fetching list of changed Dockerfiles')
    return subprocess.check_output(
        'git --no-pager diff --name-only HEAD^ HEAD | grep "Dockerfile" | sort | uniq || true',
        stderr=subprocess.DEVNULL,  shell=True
    ).decode('utf8').strip().split('\n')


def get_tag(dockerfile):
    return dockerfile.split('dockerfiles/')[-1].split('/Dockerfile')[0]


def run(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE, encoding="utf-8", stderr=PIPE)
    return p.communicate()



def build(dockerfile, logs=[], errs=[]):
    logs.append(f'Building {dockerfile}')
    tag = get_tag(dockerfile)
    output, err = run(f'docker build --tag {tag} {DOCKERFILES_DIR}/{tag}')
    logs.append(output)
    errs.append(err)
    if not err:
        logs.append(f'Successfully built {dockerfile}')
    else:
        errs.append(err)
        logs.append(f'Unable to build {dockerfile}')
    return logs, errs

        


def push(dockerfile, logs=[], errs=[]):
    logs.append(f'Pushing {dockerfile}')
    output, err = run(f'docker push {get_tag(dockerfile)}')
    logs.append(output)
    if not err:
        logs.append(f'Successfully pushed {dockerfile}')
    else:
        errs.append(err)
        logs.append(f'Unable to push {dockerfile}')
    return logs, errs
        
    

def update(dockerfile):
    logs, errs = build(dockerfile)
    if not errs:
        output, errs_b = push(dockerfile)
        logs.extend(output)
        if errs_b:
            errs.extend(errs_b)
    for log in logs:
        logging.info(log)
    for err in errs:
        logging.info(err)



def main():
    ts = time()
    try:
        logging.info('trying')
        dockerfiles = changed_dockerfiles()
    except:
        logging.warn('Unable to find changed dockerfiles. Updating all.')
        dockerfiles = all_dockerfiles()
    # queue = Queue()
    logging.info('got dockerfiles')
    updater = partial(update)
    with Pool(len(dockerfiles)) as p:
        p.map(updater, dockerfiles)
    logging.info('all done')
    logging.info('Took %s seconds', time() - ts)


if __name__ == '__main__':
    main()

# update(changed_dockerfiles()[1])
# logging.info('why')

# update_changed()