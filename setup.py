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

from setuptools import setup

setup(
    name='obsci',
    description='A OpenBuildService CI',
    long_description='A OpenBuildService CI',
    keywords='OBS CI',
    url='https://github.com/obsci/obsci',
    author='Thomas Bechtold',
    author_email='tbechtold@suse.com',
    license='Apache-2.0',
    use_scm_version=True,
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python :: 3',
    ],
    setup_requires=['setuptools_scm'],
    extras_require={
        'docs': [
            'Sphinx',
            'sphinx_rtd_theme',
        ],
        'pep8': ['flake8'],
        'tests': [
            'pytest',
            'requests_mock',
        ],
        # requirements for the obsci-worker
        # NOTE: podman does currently not work so use docker for now
        'worker': [
            'docker',
            'pyyaml',  # for parsing the _obsci config file in packages
            'jsonschema',  # for validating the _obsci config
            'requests',
        ],
    },
    entry_points={
        'console_scripts': [
            'obsci-worker = obsci.cmd.worker:main',
        ]
    }
)
