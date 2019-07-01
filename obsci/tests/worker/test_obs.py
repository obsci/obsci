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

import requests_mock

from obsci.tests.test_base import OBSCITestBase
from obsci.worker import obs

# a mock for OBS project metadata
OBS_PROJECT_META_MOCK = """<project name="home:tbechtold:branches:devel:languages:python">
  <title>Branch project for package python-Sphinx</title>
  <description>the project description</description>
  <person userid="tbechtold" role="maintainer"/>
  <publish>
    <disable/>
  </publish>
  <debuginfo>
    <enable/>
  </debuginfo>
  <repository name="openSUSE_Tumbleweed">
    <path project="devel:languages:python" repository="openSUSE_Tumbleweed"/>
    <arch>i586</arch>
    <arch>x86_64</arch>
  </repository>
  <repository name="openSUSE_Leap_15.1">
    <path project="devel:languages:python" repository="openSUSE_Leap_15.1"/>
    <arch>x86_64</arch>
  </repository>
  <repository name="SLE_15_SP1">
    <path project="devel:languages:python" repository="SLE_15_SP1"/>
    <arch>x86_64</arch>
  </repository>
  <repository name="SLE_12_SP4">
    <path project="devel:languages:python" repository="SLE_12_SP4"/>
    <arch>x86_64</arch>
  </repository>
</project>
"""


class OBSCITestOBS(OBSCITestBase):
    """Test OBS integration"""

    @requests_mock.Mocker()
    def test_get_project_repositories(self, rq_mock):
        rq_mock.get(requests_mock.ANY, text=OBS_PROJECT_META_MOCK)
        o = obs.OBSCIObs('http://build.opensuse.org', 'username', 'password')
        repos = o.get_project_repositories(
            'project', 'openSUSE_Leap_15.1', 'x86_64')
        assert repos == [
            {
                'project': 'devel:languages:python',
                'repository': 'openSUSE_Leap_15.1',
                'publish_repo_url': 'https://download.opensuse.org/repositories/devel:/languages:/python/openSUSE_Leap_15.1',  # noqa
            }
        ]

    def test__get_download_url(self):
        o = obs.OBSCIObs('http://build.opensuse.org', 'username', 'password')
        assert o._get_download_url() == \
            'https://download.opensuse.org/repositories/'
