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

"""
Testing Versions
"""
import unittest
from spinn_machine.config_setup import unittest_setup
from spinn_machine.exceptions import SpinnMachineException
from spinn_machine.version.version_strings import VersionStrings


class TestVersionString(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_names(self):
        vs = VersionStrings.from_String("any")
        self.assertEqual(vs.value, "Any")
        vs = VersionStrings.from_String("FourPlus")
        self.assertEqual(vs.value, "Four plus")
        with self.assertRaises(SpinnMachineException):
            vs = VersionStrings.from_String("Foo")


if __name__ == '__main__':
    unittest.main()
