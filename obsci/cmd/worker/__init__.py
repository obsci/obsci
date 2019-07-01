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

"""
obsci-worker is the component that does the actual work
"""

import logging
import argparse
import sys
import os
import tempfile

from obsci.worker.obs import OBSCIObs
from obsci.worker.config_package import OBSCIConfigPackage

logger = logging.getLogger(__name__)


def process_args():
    parser = argparse.ArgumentParser(
        description='OBS CI worker')
    parser.add_argument('--obs-url',
                        default='https://api.opensuse.org',
                        help='The url of the OBS instance. '
                        'Default: "%(default)s".')
    parser.add_argument('--obs-username',
                        help='The username to use to access the OBS API')
    parser.add_argument('--obs-password',
                        help='The password to use to access the OBS API')
    parser.add_argument('--testenv-type',
                        choices=['container'],
                        default='container',
                        help='The test environment type where the tests '
                        'are executed in. Default: "%(default)s".')
    parser.add_argument('--testenv',
                        default='opensuse-leap-15.1',
                        help='The test environment where the tests '
                        'are executed in. Default: %(default)s.')

    parser.add_argument('obs-project',
                        help='The OBS project name.')
    parser.add_argument('obs-repository',
                        help='The OBS repository name.')
    parser.add_argument('obs-architecture',
                        help='The OBS architecture.')
    parser.add_argument('obs-package',
                        help='The OBS package name.')
    return vars(parser.parse_args())


def main():
    # TODO: make logging configurable
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.INFO)

    args = process_args()

    # handle OBS interaction
    obs = OBSCIObs(args['obs_url'], args['obs_username'], args['obs_password'])

    # check if there are some tests defined in the package
    obsci_config_str = obs.get_config_from_package(
        args['obs-project'], args['obs-package'])

    if not obsci_config_str:
        logger.info('Stopping here. No _obsci test config found')
        return 0

    obsci_config = OBSCIConfigPackage(obsci_config_str.getvalue())
    if not len(obsci_config.test_names):
        logger.info('Stopping here. No tests defined in _obsci config')
        return 0

    # tempdir to store files that will be used later
    with tempfile.TemporaryDirectory(prefix='obsci_') as tempdir:
        # a directory where the test files are stored
        test_srcdir = os.path.join(tempdir, 'tests')
        os.mkdir(test_srcdir)
        for testfilename in obsci_config.test_names:
            testfile = obs.get_test_from_package(
                args['obs-project'], args['obs-package'], testfilename)
            if not testfile:
                logger.info(
                    'File for test "{}" not found'.format(testfilename))
                continue
            testfilepath = os.path.join(test_srcdir, testfilename)
            with open(testfilepath, 'wb') as tf:
                tf.write(testfile.read())
            # test files should be accessable/executable
            os.chmod(testfilepath, 0o777)

        # a directory where the testsubject files are stored
        testsubject_srcdir = os.path.join(tempdir, 'testsubject')
        os.mkdir(testsubject_srcdir)
        obs.get_binaries(
            testsubject_srcdir, args['obs-project'], args['obs-repository'],
            args['obs-architecture'], args['obs-package'])

        # get the class which can handle the selected testenv type
        if args['testenv_type'] == 'container':
            from obsci.worker import testenv_container
            te = testenv_container.OBSCITestEnvContainer(args['testenv'])
        else:
            raise ValueError('Invalid testenv type "{}"'.format(
                args['testenv_type']))

        # do the actual work
        te.run(testsubject_srcdir, test_srcdir, obsci_config.test_names)


# for debugging
if __name__ == '__main__':
    sys.exit(main())
