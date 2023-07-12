# Copyright (c) 2015 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Testing Version5
"""
import unittest
from spinn_machine.version.version_5 import Version5
from spinn_machine.config_setup import unittest_setup


class TestVersion5(unittest.TestCase):
    """ Tests of IPTag
    """
    def setUp(self):
        unittest_setup()

    def test_version(self):
        version = Version5()
        a = version.max_cores_per_chip
        self.assertEqual(18, version.max_cores_per_chip)


if __name__ == '__main__':
    unittest.main()
