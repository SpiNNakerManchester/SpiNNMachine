# Copyright (c) 2014 The University of Manchester
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
from spinn_machine.exceptions import (
    SpinnMachineException)
from spinn_machine.version.version_5 import Version5
from spinn_machine.version.version_factory import version_factory


class TestVersionFactory(unittest.TestCase):

    def setUp(self) -> None:
        unittest_setup()

    def test_no_info(self) -> None:
        with self.assertRaises(SpinnMachineException):
            version_factory()

    def test_bad_spalloc_3(self) -> None:
        set_config("Machine", "version", "3")
        set_config("Machine", "spalloc_server", "Somewhere")
        with self.assertRaises(SpinnMachineException):
            version_factory()

    def test_ok_spalloc_4(self) -> None:
        set_config("Machine", "version", "4")
        set_config("Machine", "spalloc_server", "Somewhere")
        version = version_factory()
        self.assertEqual(Version5(), version)

    def test_ok_spalloc(self) -> None:
        # warning this behaviour may break if spalloc ever support spin2
        set_config("Machine", "spalloc_server", "Somewhere")
        version = version_factory()
        self.assertEqual(Version5(), version)

    def test_ok_remote_5(self) -> None:
        set_config("Machine", "version", "4")
        set_config("Machine", "remote_spinnaker_url", "Somewhere")
        version = version_factory()
        self.assertEqual(Version5(), version)

    def test_bad_spalloc_and_remote(self) -> None:
        set_config("Machine", "spalloc_server", "Somewhere")
        set_config("Machine", "remote_spinnaker_url", "Somewhere")
        with self.assertRaises(SpinnMachineException):
            version_factory()

    def test_bad_spalloc_and_name(self) -> None:
        set_config("Machine", "spalloc_server", "Somewhere")
        set_config("Machine", "machine_name", "Somewhere")
        with self.assertRaises(SpinnMachineException):
            version_factory()

    def test_bad_spalloc_and_virtual(self) -> None:
        set_config("Machine", "spalloc_server", "Somewhere")
        set_config("Machine", "virtual_board", "True")
        with self.assertRaises(SpinnMachineException):
            version_factory()

    def test_bad_remote_and_name(self) -> None:
        set_config("Machine", "remote_spinnaker_url", "Somewhere")
        set_config("Machine", "machine_name", "Somewhere")
        with self.assertRaises(SpinnMachineException):
            version_factory()

    def test_bad_remote_and_virtual(self) -> None:
        set_config("Machine", "remote_spinnaker_url", "Somewhere")
        set_config("Machine", "virtual_board", "True")
        with self.assertRaises(SpinnMachineException):
            version_factory()

    def test_bad_name_and_virtual(self) -> None:
        set_config("Machine", "machine_name", "Somewhere")
        set_config("Machine", "virtual_board", "True")
        with self.assertRaises(SpinnMachineException):
            version_factory()


if __name__ == '__main__':
    unittest.main()
