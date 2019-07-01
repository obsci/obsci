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

    def _get_project_meta(self, project):
        """get the OBS metadata for the given project"""
        url = '{}/source/{}/_meta'.format(
            self._url, project)
        resp = requests.get(url, auth=self._obs_auth)
        if not resp.status_code == 200:
            raise Exception('Can not get _meta ({})'.format(resp.status_code))

        # FIXME: we trust the input from OBS here. Should be use defusedxml?
        root = ET.fromstring(resp.text)
        return root

    def _get_download_url(self):
        # FIXME: This is a hack. There is no way to get the download
        # url via the OBS API
        if 'opensuse.org' in self._url:
            return 'https://download.opensuse.org/repositories/'
        elif 'suse.de' in self._url:
            return 'http://download.suse.de/ibs/'
        else:
            raise Exception('Can not guess download url for "{}"'.format(
                self._url))

    def get_project_repositories(self, project, repo, arch):
        """get the defined repositories from the project metadata"""
        repos = []
        root = self._get_project_meta(project)
        for r in root.findall('./repository/[@name=\'{}\']'.format(repo)):
            # we are only interested in repos with the given arch
            # FIXME: I guess this can be done better with xpath
            found_arch = r.findall('[arch=\'{}\']'.format(arch))
            if not found_arch:
                continue
            # get the repo project and repo name
            for found_path in r.findall('path'):
                publish_url = '{}{}/{}'.format(
                    self._get_download_url(),
                    found_path.get('project').replace(':', ':/'),
                    found_path.get('repository'),
                )
                repos.append({'project': found_path.get('project'),
                              'repository': found_path.get('repository'),
                              'publish_repo_url': publish_url})
        return repos

    def get_binaries_list(self, project, repo, arch, package):
        url = '{}/build/{}/{}/{}/{}'.format(
            self._url, project, repo, arch, package)
        resp = requests.get(url, auth=self._obs_auth)
        if not resp.status_code == 200:
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
            if not r.status_code == 200:
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
        if not r.status_code == 200:
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
