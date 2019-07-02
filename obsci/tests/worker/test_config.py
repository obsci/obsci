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

import pytest

from obsci.tests.test_base import TestOBSCIBase
from obsci.worker import config_project
from obsci.worker import config_package


class TestOBSCIConfigProject(TestOBSCIBase):
    @pytest.mark.parametrize('test_input,expected', [
        (
            '{"test_packages": [{"project": "pro", "package": "pac"}]}',
            {
                "test_packages": [{"project": "pro", "package": "pac"}]
            }
        ),
        (
            '{"test_packages": [{"project": "pro", "package": "pac"},{"project": "pro2", "package": "pac2"}]}',  # noqa
            {
                "test_packages": [{"project": "pro", "package": "pac"},
                                  {"project": "pro2", "package": "pac2"}]
            }
        ),
    ])
    def test_config_project_valid(self, test_input, expected):
        conf = config_project.OBSCIConfigProject(test_input)
        assert conf.conf == expected


class TestOBSCIConfigPackage(TestOBSCIBase):
    @pytest.mark.parametrize('test_input,expected_names', [
        (
            """---
tests:
  - name: foo
        """,
         ['foo']
        ),
    ])
    def test_config_package_valid(self, test_input, expected_names):
        conf = config_package.OBSCIConfigPackage(test_input)
        assert conf.test_names == expected_names
