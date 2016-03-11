# -*- encoding: utf-8 -*-

from __future__ import with_statement, print_function

import os.path
from time import sleep
from contextlib import nested

from fabric.api import local, settings, lcd, env, prefix
from fabric.contrib.console import confirm

proj_name = 'confapplet'
code_dir = '/data/repos/%s' % proj_name
dest_dir = '/data/app/%s' % proj_name
venv_dir = '%s/env' % dest_dir


def init():
    with settings(warn_only=True):
        if local('test -d %s' % code_dir).failed:
            if confirm('克隆版本库到 %s？' % code_dir):
                local('git clone https://github.com/tanbro/democonfapplet.git %s' % code_dir)
        if local('test -d %s' % dest_dir).failed:
            local('mkdir -p %s' % dest_dir)
        if local('test -d %s' % venv_dir).failed:
            local('python3.5 -m venv %s' % venv_dir)


def deploy(branch='master'):
    with lcd(code_dir):
        local('git fetch')
        local('git checkout --force %s' % branch)
        local('git reset --hard origin/%s' % branch)
        githash = local('git log -n 1 --pretty=%h', capture=True).stdout
        gittag = local('git tag -l --contains HEAD', capture=True).stdout
        gitdate = local('git log -n 1 --pretty=%ai', capture=True).stdout
        tmpfile = '%s-%s-%s.tar' % (proj_name, branch, githash)
        tmpfile = tmpfile.replace('/', '_')
        local('git archive --format=tar --output=%s HEAD' % tmpfile)
        try:
            local('mkdir -p %s' % dest_dir)
            local('tar -xf %s -C %s' % (tmpfile, dest_dir))
        finally:
            local('rm -f %s' % tmpfile)
        with open(os.path.join(dest_dir, 'version.txt'), 'w') as f:
            f.write('branch: %s\n' % branch)
            f.write('hash: %s\n' % githash)
            f.write('date: %s\n' % gitdate)
            f.write('tag: %s\n' % gittag)
    with nested(lcd(dest_dir), prefix('source %s/bin/activate' % venv_dir)):
        with settings(warn_only=True):
            print('install pip pacakges')
            local('pip install --upgrade -r requirements.txt')
    with lcd(dest_dir):
        with settings(warn_only=True):
            print('install npm pacakges')
            local('npm install')
            print('bower npm pacakges')
            env['CI'] = 'true'
            local('bower install --allow-root')
    with nested(lcd('%s/webservice' % dest_dir), prefix('source %s/bin/activate' % venv_dir)):
        with settings(warn_only=True):
            local('pkill -f confapplet')
            sleep(5)
        print('start web service program')
        local('nohup python -m confapplet > /dev/null 2>&1 &')
