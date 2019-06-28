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

import tarfile
import tempfile
import pathlib
import os

from obsci.tests.test_base import OBSCITestBase
from obsci import utils


class OBSCITestUtils(OBSCITestBase):
    """Test utils"""
    def test_create_tarfile(self):
        with tempfile.TemporaryDirectory() as td:
            pathlib.Path(os.path.join(td, "file1.txt")).touch()
            tar_stream = utils.create_tarfile(td)
            t = tarfile.open(fileobj=tar_stream)
            self.assertIn('file1.txt', [m.name for m in t.getmembers()])
