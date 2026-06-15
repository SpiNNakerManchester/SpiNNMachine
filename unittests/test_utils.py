# Copyright (c) 2026 The University of Manchester
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
from spinn_machine.machine_utils import (
    contact_email, SPINNAKERTEAM, SPINNCLOUD)
from spinn_machine.version import Spin1Gen, Spin2Gen


class TestingUtils(unittest.TestCase):

    def setUp(self) -> None:
        unittest_setup()
        # overwrite users cfg
        set_config("Machine", "spalloc_server", "None")
        set_config("Machine", "remote_spinnaker_url", "None")
        set_config("Machine", "version", "None")

    def test_no_info(self) -> None:
        email = contact_email()
        self.assertIn(SPINNAKERTEAM, email)
        self.assertIn(SPINNCLOUD, email)

    def test_no_version(self) -> None:
        email = contact_email()
        set_config("Machine", "spalloc_server", "unknown.example.com")
        self.assertIn(SPINNAKERTEAM, email)
        self.assertIn(SPINNCLOUD, email)

    def test_manchester_spalloc(self) -> None:
        set_config("Machine", "spalloc_server", "spinnaker.cs.man.ac.uk")
        set_config("Machine", "version", str(Spin2Gen.SPIN2_1CHIP.value))
        self.assertEqual(SPINNAKERTEAM, contact_email())

    def test_manchester_remote(self) -> None:
        set_config("Machine", "remote_spinnaker_url", "somewhere.manchester.ac.uk")
        set_config("Machine", "version", str(Spin2Gen.SPIN2_1CHIP.value))
        self.assertEqual(SPINNAKERTEAM, contact_email())

    def test_spin1_version(self) -> None:
        set_config("Machine", "version", str(Spin1Gen.THREE.value))
        self.assertEqual(SPINNAKERTEAM, contact_email())

    def test_spin2_version(self) -> None:
        set_config("Machine", "version", str(Spin2Gen.SPIN2_1CHIP.value))
        self.assertEqual(SPINNCLOUD, contact_email())


if __name__ == '__main__':
    unittest.main()
