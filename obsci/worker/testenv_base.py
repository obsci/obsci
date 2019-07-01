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

import abc


class OBSCITestEnvBase(abc.ABC):
    """Base class for test environments like containers for VMs"""
    def __init__(self, testenv):
        # check that the given testenv is a valid one
        if testenv not in self.testenvs_available():
            raise ValueError('testenv "{}" not available'.format(testenv))
        self._testenv = testenv

    @classmethod
    @abc.abstractmethod
    def testenvs_available(cls):
        """return a list of available testenv names"""

    @property
    def testsubject(self):
        """return testsubject. This is read-only"""
        return self._testsubject

    @property
    @abc.abstractmethod
    def url(self):
        """return the url for the given testenv. This is read-only"""

    @property
    @abc.abstractmethod
    def envtype(self):
        """return the testenv type. This is read-only"""

    @property
    @abc.abstractmethod
    def testsubject_destdir(self):
        """
        return a writable directory where the test subject(s) can be copied
        into
        """

    @property
    @abc.abstractmethod
    def test_destdir(self):
        """
        return a writable directory where the test(s) can be copied
        into
        """

    @abc.abstractmethod
    def copy_testsubject(self, testsubject_srcdir):
        """
        copy the testsubject files into the testenv's
        testsubject_destdir directory
        """

    @abc.abstractmethod
    def install_testsubject(self):
        """
        install the copied testsubjects
        """

    @abc.abstractmethod
    def copy_test(self, test_srcdir):
        """
        copy the test file(s) into the testenv's
        test_destdir directory
        """

    @abc.abstractmethod
    def prepare(self, testenv_repos):
        """Prepare the testenv"""

    @abc.abstractmethod
    def prepare_testsubject_destdir(self):
        """Prepare the testenv"""

    @abc.abstractmethod
    def prepare_test_destdir(self):
        """Prepare the testenv"""

    @abc.abstractmethod
    def run_test(self, test_names):
        """Run the test(s)"""

    def run(self, testenv_repos, testsubject_srcdir, test_srcdir, test_names):
        """Run the different steps"""
        self.prepare(testenv_repos)
        # prepare the testsubject(s)
        self.prepare_testsubject_destdir()
        self.copy_testsubject(testsubject_srcdir)
        self.install_testsubject()
        # prepare the test(s)
        self.prepare_test_destdir()
        self.copy_test(test_srcdir)
        self.run_test(test_names)
