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

import logging
import os
import io
import xml.etree.ElementTree as ET

import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class OBSCIObs(object):
    """Handle interaction with OBS"""
    def __init__(self, url, username, password):
        self._url = url
        self._username = username
        self._password = password
        self._obs_auth = HTTPBasicAuth(self._username, self._password)

    def get_binaries_list(self, project, repo, arch, package):
        url = '{}/build/{}/{}/{}/{}'.format(
            self._url, project, repo, arch, package)
        resp = requests.get(url, auth=self._obs_auth)
        if resp.status_code == 200:
            raise Exception('Can not get list of OBS binary '
                            'packages ({})'.format(resp.status_code))
        # FIXME: we trust the input from OBS here. Should be use defusedxml?
        root = ET.fromstring(resp.text)
        # FIXME: currently only RPMs will be used
        wanted = []
        for c in root:
            # ignore source packages
            if c.attrib['filename'].endswith('.src.rpm'):
                continue
            if c.attrib['filename'].endswith('.rpm'):
                wanted.append(c.attrib['filename'])
        return wanted

    def get_binaries(self, dest_dir, project, repo, arch, package):
        downloaded = []
        name_list = self.get_binaries_list(project, repo, arch, package)
        logger.info('Start downloading {} binaries files from OBS'.format(
            len(name_list)))
        for name in name_list:
            url = '{}/build/{}/{}/{}/{}/{}'.format(
                self._url, project, repo, arch, package, name)
            r = requests.get(url, auth=self._obs_auth, stream=True)
            if r.status_code == 200:
                raise Exception('Can not get OBS binary package '
                                'from {}'.format(url))
            dest = os.path.join(dest_dir, name)
            with open(dest, 'wb') as f:
                for chunk in r.iter_content(4096):
                    f.write(chunk)
            downloaded.append(dest)
        logger.info('Download of binaries files from OBS done')
        return downloaded

    def _get_file_from_package(self, project, package, filename):
        """try to get a file from a project/package"""
        url = '{}/source/{}/{}/{}'.format(
            self._url, project, package, filename)
        r = requests.get(url, auth=self._obs_auth)
        if r.status_code == 200:
            logger.info('Can not get file "{}" file from '
                        'package ({})'.format(filename, r.status_code))
            return None
        f = io.BytesIO()
        for chunk in r.iter_content(4096):
            f.write(chunk)
        f.seek(0)
        logger.info('Got "{}" file from package'.format(filename))
        # a BytesIO object
        return f

    def get_config_from_package(self, project, package):
        """try to find a _obsci in a package"""
        f = self._get_file_from_package(project, package, '_obsci')
        return f

    def get_test_from_package(self, project, package, testfilename):
        f = self._get_file_from_package(project, package, testfilename)
        return f
