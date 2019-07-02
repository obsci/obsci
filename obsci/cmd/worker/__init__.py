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
from obsci.worker.config_project import OBSCIConfigProject

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


def get_config_from_packages(obs, project, package):
    packages_candidates = []
    obsci_configs = []
    config_project_str = obs.get_config_from_project(project)
    if config_project_str:
        logger.info('Found "_obsci" key in project config')
        config_project = OBSCIConfigProject(config_project_str)
        packages_candidates = config_project.conf.get('test_packages', [])

    # the package itself (if not already defined in the project config)
    if {'project': project, 'package': package} not in packages_candidates:
        packages_candidates.append({'project': project, 'package': package})

    for pkg in packages_candidates:
        obsci_config_package_str = obs.get_config_from_package(
            pkg['project'], pkg['package'])
        if obsci_config_package_str:
            obsci_configs.append(OBSCIConfigPackage(obsci_config_package_str))
    return obsci_configs


def main():
    # TODO: make logging configurable
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.INFO)

    args = process_args()

    # handle OBS interaction
    obs = OBSCIObs(args['obs_url'], args['obs_username'], args['obs_password'])

    # tempdir to store files that will be used later
    with tempfile.TemporaryDirectory(prefix='obsci_') as tempdir:
        # a directory where the test files are stored
        test_srcdir = os.path.join(tempdir, 'tests')
        os.mkdir(test_srcdir)

        # get project config
        obsci_configs = get_config_from_packages(
            obs, args['obs-project'], args['obs-package'])

        # get testfiles for all the given obsci configs
        for obsci_config in obsci_configs:
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

        # get the defined repos from the OBS project metadata
        testenv_repos = obs.get_project_repositories(args['obs-project'],
                                                     args['obs-repository'],
                                                     args['obs-architecture'])

        # collect the test names from all obsci_configs
        testnames = []
        for conf in obsci_configs:
            testnames += conf.test_names
        # do the actual work
        te.run(testenv_repos, testsubject_srcdir, test_srcdir, testnames)


# for debugging
if __name__ == '__main__':
    sys.exit(main())
