# -*- encoding: utf-8 -*-

from __future__ import with_statement, print_function

import os.path
from time import sleep
from contextlib import nested

from fabric.api import run, settings, cd, env, prefix
from fabric.contrib.console import confirm

proj_name = 'confapplet'
code_dir = '/data/repos/%s' % proj_name
dest_dir = '/data/app/%s' % proj_name
venv_dir = '%s/env' % dest_dir


def init():
    with settings(warn_only=True):
        if run('test -d %s' % code_dir).failed:
            if confirm('克隆版本库到 %s？' % code_dir):
                run('git clone https://github.com/tanbro/democonfapplet.git %s' % code_dir)
        if run('test -d %s' % dest_dir).failed:
            run('mkdir -p %s' % dest_dir)
        if run('test -d %s' % venv_dir).failed:
            run('python3.5 -m venv %s' % venv_dir)


def deploy(branch='master', restarting=True):
    with cd(code_dir):
        run('git fetch')
        run('git checkout --force %s' % branch)
        run('git reset --hard origin/%s' % branch)
        export_file = '%s-%s.tar' % (proj_name, branch)
        run('git archive --format=tar --output=%s HEAD' % export_file)
        run('mkdir -p %s' % dest_dir)
        run('tar -xf %s -C %s' % (export_file, dest_dir))
        run('rm -f %s' % export_file)
    with nested(cd(dest_dir), prefix('source %s/bin/activate' % venv_dir)):
        with settings(warn_only=True):
            print('install pip pacakges')
            run('pip install --upgrade -r requirements.txt')
    with cd(dest_dir):
        with settings(warn_only=True):
            print('install npm pacakges')
            run('npm install')
            print('bower npm pacakges')
            env['CI'] = 'true'
            run('bower install --allow-root')
    if restarting:
        restart()


def start():
    with nested(cd('%s/webservice' % dest_dir), prefix('source %s/bin/activate' % venv_dir)):
        run('$(nohup python -m confapplet >& /dev/null < /dev/null &) && sleep 1')


def stop():
    with nested(cd('%s/webservice' % dest_dir), prefix('source %s/bin/activate' % venv_dir)):
        with settings(warn_only=True):
            run('pkill -f confapplet')
            run('sleep 5')


def restart():
    stop()
    start()
