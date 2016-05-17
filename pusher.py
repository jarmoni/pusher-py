#!/usr/bin/python3
""" Automatically synchronization of local git-repositories with remotes """

import argparse
import logging
import yaml
import time
import threading
import subprocess


class PusherThread(threading.Thread):
    def __init__(self, repos):
        threading.Thread.__init__(self)
        self.Repos = repos

    def check_changes(self):
        if subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=self.Repos['path']):
            logging.debug('Repository=' + self.Repos['name'] + ', untracked files')
            return True
        if subprocess.check_output(['git', 'ls-files', '-m'], cwd=self.Repos['path']):
            logging.debug('Repository=' + self.Repos['name'] + ', modified files')
            return True
        return False

    def add_and_commit(self):
        if subprocess.check_output(['git', 'add', '-a'], cwd=self.Repos['path']):
            logging.debug('Repository=' + self.Repos['name'] + ', added files')
        if subprocess.check_output(['git', 'commit', '-m', self.Repos['msg']], cwd=self.Repos['path']):
            logging.debug('Repository=' + self.Repos['name'] + ', commited files')

    def pull(self):
        subprocess.check_output(['git', 'pull'], cwd=self.Repos['path'])

    def push(self):
        subprocess.check_output(['git', 'push'], cwd=self.Repos['path'])

    def run(self):
        logging.info('Starting Repository=' + str(self.Repos))
        while True:
            changed = self.check_changes()
            if changed or self.Repos['auto_pull']:
                if changed:
                    self.add_and_commit()
                pull()
                if changed:
                    push()
            time.sleep(5)


def update_repos_cfg(repos, globals, optional_params):
    for param in optional_params:
        if param not in repos:
            if param not in globals:
                raise Exception('Param must be set=' + param)
            repos[param] = globals[param]
            logging.debug('Repository=' + repos['name'] + ', Set prop "' + param + '" from globals')


def main(args):
    logging.info('Starting with args=' + str(args))
    with open(args.config_file, 'r') as cfg_file:
        cfg = yaml.load(cfg_file)

    logging.info('Starting with config=' + str(cfg))
    threads = []
    for repos in cfg['repositories']:
        update_repos_cfg(repos, cfg['globals'], ['auto_push', 'auto_pull', 'user', 'key', 'msg'])
        thread = PusherThread(repos)
        threads.append(thread)
        thread.daemon = True
        thread.start()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Synchronizes git-repositories with its remotess')
    parser.add_argument('-c', '--config-file', type=str, required=True, help='(yaml-) configuration-file')
    parser.add_argument('-l', '--log-level', type=str, default='INFO', help='log-level (DEBUG|INFO|WARNING|ERROR|CRITICAL)')
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s %(threadName)s %(levelname)s %(message)s', level=getattr(logging, args.log_level.upper()))

    main(args)
