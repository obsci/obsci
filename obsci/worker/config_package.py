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
import json

from obsci.worker.config_base import OBSCIConfigBase


# the jsonschema to validate the _obsci config which is in packages
curdir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(os.path.join(curdir, 'config_package_schema.json'), 'r') as f:
    SCHEMA = json.loads(f.read())


class OBSCIConfigPackage(OBSCIConfigBase):
    @property
    def schemapath(self):
        curdir = os.path.realpath(os.path.join(
            os.getcwd(), os.path.dirname(__file__)))
        return os.path.join(curdir, 'config_package_schema.json')

    @property
    def test_names(self):
        return [el['name'] for el in self.conf['tests']]
