#!/usr/bin/python3
# Copyright (c) 2019 SUSE Linux GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
import docker

from obsci import utils
from obsci.worker.testenv_base import OBSCITestEnvBase

logger = logging.getLogger(__name__)


class OBSCITestEnvContainer(OBSCITestEnvBase):
    def __init__(self, testenv):
        super().__init__(testenv)
        # docker client
        self._client = docker.from_env()
        # check that docker is running
        self._client.ping()
        logger.debug('docker version: {}'.format(self._client.version()))
        # container object
        self._container = None

    @classmethod
    def testenvs_available(cls):
        return [
            'opensuse-leap-15.1',
            'sles-12sp4',
        ]

    @property
    def testsubject_destdir(self):
        return '/tmp/obsci/testsubject/'

    @property
    def test_destdir(self):
        return '/tmp/obsci/test/'

    @property
    def url(self):
        if self._testenv == 'opensuse-leap-15.1':
            return 'registry.hub.docker.com/opensuse/leap:15.1'
        if self._testenv == 'sles-12sp4':
            return 'registry.suse.de/suse/containers/sle-server/12-sp4/containers/suse/sles12sp4'  # noqa
        else:
            raise ValueError('testenv "{}" does not provide an url'.format(
                self._testenv))

    @property
    def envtype(self):
        return 'container'

    def _run_command(self, cmd, log_output=False, **kwargs):
        """run a command in the current container"""
        logger.info('{}: calling "{}"'.format(self._container.short_id, cmd))
        rc, output = self._container.exec_run(cmd, **kwargs)
        if not rc == 0:
            msg = 'Can not call command "{}" (rc: {}): {}'.format(
                cmd, rc, output)
            raise Exception(msg)
        else:
            if log_output:
                msg = '{}: call done "{}": {}'.format(
                    self._container.short_id, cmd, output)
            else:
                msg = '{}: call done "{}"'.format(
                    self._container.short_id, cmd)
            logger.info(msg)

    def prepare(self):
        client = docker.from_env()
        image = client.images.pull(self.url)
        # FIXME: the sleep prevents the container from stopping for the sleep
        # time. ugly hack
        self._container = client.containers.run(image, '/usr/bin/sleep 600',
                                                detach=True)
        # update base container
        # FIXME: enable the updates
        # self._run_command('zypper -n ref')
        # self._run_command('zypper -n dup')
        logger.info('{}: container started'.format(self._container.short_id))

    def prepare_testsubject_destdir(self):
        self._run_command('mkdir -p {}'.format(self.testsubject_destdir))

    def copy_testsubject(self, testsubject_srcdir):
        # create a tar archive that can be used with the docker API
        logger.info('{}: Start copying testsubject to container'.format(
            self._container.short_id))
        tar_stream = utils.create_tarfile(testsubject_srcdir)
        # we have a tar archive now - copy to container
        if self._container.put_archive(self.testsubject_destdir, tar_stream):
            logger.info('{}: Copied testsubject to {}'.format(
                self._container.short_id, self.testsubject_destdir))
        else:
            logger.error('{}: Failed to copy testsubject archive to '
                         'container'.format(self._container.short_id))

    def install_testsubject(self):
        # ignore zypper gpgcheck
        self._run_command('sh -c "echo gpgcheck=off >> /etc/zypp/zypp.conf"')
        # do a try run to get the output to see what is needed
        self._run_command(
            'sh -c "zypper -n --no-refresh install --dry-run {}/*.rpm"'.format(
                self.testsubject_destdir), log_output=True)
        # do the actual installation
        self._run_command(
            'sh -c "zypper -n --no-refresh install {}/*.rpm"'.format(
                self.testsubject_destdir))

    def prepare_test_destdir(self):
        self._run_command('mkdir -p {}'.format(self.test_destdir))

    def copy_test(self, test_srcdir):
        logger.info('{}: Start copying test to container'.format(
            self._container.short_id))
        tar_stream = utils.create_tarfile(test_srcdir)
        # we have a tar archive now - copy to container
        if self._container.put_archive(self.test_destdir, tar_stream):
            logger.info('{}: Copied test to {}'.format(
                self._container.short_id, self.test_destdir))
        else:
            logger.error('{}: Failed to copy test archive to '
                         'container'.format(self._container.short_id))

    def run_test(self, test_names):
        for name in test_names:
            testfilepath = os.path.join(self.test_destdir, name)
            logger.info('{}: Running test "{}"'.format(
                self._container.short_id, testfilepath))
            # run the actual test
            rc, output = self._container.exec_run(testfilepath)
            if rc == 0:
                msg = '{}": test {} SUCEEEDED'.format(
                    name, self._container.short_id)
            else:
                msg = '{}": test {} FAILED (rc: {})'.format(
                    name, self._container.short_id, rc)
            logger.info(msg)
