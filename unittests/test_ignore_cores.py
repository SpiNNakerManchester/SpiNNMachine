# Copyright (c) 2024 The University of Manchester
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

import unittest
from spinn_utilities.config_holder import set_config
from spinn_machine.config_setup import unittest_setup
from spinn_machine.ignores import IgnoreChip, IgnoreCore, IgnoreLink
from spinn_machine.version.version_strings import VersionStrings

class TestDownCores(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_bad_ignores(self):
        set_config("Machine", "versions", VersionStrings.BIG.text)

        try:
            IgnoreChip.parse_string("4,4,3,4:6,6,ignored_ip")
        except Exception as ex:
            self.assertTrue("downed_chip" in str(ex))

        try:
            IgnoreCore.parse_string("3,3,3,4: 5,5,-5:7,7,7,ignored_ip")
        except Exception as ex:
            self.assertTrue("downed_core" in str(ex))

        empty = IgnoreCore.parse_string(None)
        self.assertEqual(len(empty), 0)

        try:
            IgnoreLink.parse_string("1,3:5,3,3,ignored_ip")
        except Exception as ex:
            self.assertTrue("downed_link" in str(ex))

