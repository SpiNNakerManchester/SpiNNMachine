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
from spinn_utilities.exceptions import ConfigException
from spinn_machine.config_setup import unittest_setup
from spinn_machine.ignores import IgnoreChip, IgnoreCore, IgnoreLink
from spinn_machine.version import SPIN2_1CHIP
from spinn_machine.version.version_201 import Version201
from spinn_machine.version.version_5 import Version5
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

    def test_down_cores_bad_string(self):
        set_config("Machine", "versions", VersionStrings.BIG.text)
        with self.assertRaises(ConfigException):
            IgnoreCore.parse_string("4,4,bacon")

    def test_qx_qy_qp_to_id_spin2(self):
        version = Version201()
        self.assertEqual(75, version.qx_qy_qp_to_id(3, 4, 2))
        self.assertEqual((3, 4, 2), version.id_to_qx_qy_qp(75))

    def test_qx_qy_qp_to_spin1(self):
        version = Version5()
        with self.assertRaises(NotImplementedError):
            self.assertEqual(75, version.qx_qy_qp_to_id(3, 4, 2))
        with self.assertRaises(NotImplementedError):
            self.assertEqual((3, 4, 2), version.id_to_qx_qy_qp(75))

    def test_version_401(self):
        set_config("Machine", "version", SPIN2_1CHIP)
        ignores = IgnoreCore.parse_string("3,3,3.4.2,4")
        self.assertEqual(1, len(ignores))
        for ignore in ignores:
            self.assertEqual(75, ignore.p)
            self.assertEqual(75, ignore.virtual_p)
