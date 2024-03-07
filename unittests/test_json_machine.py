# Copyright (c) 2017 The University of Manchester
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

from tempfile import mktemp
import unittest
from spinn_utilities.config_holder import set_config
from spinn_machine import virtual_machine
from spinn_machine.data.machine_data_writer import MachineDataWriter
from spinn_machine.config_setup import unittest_setup
from spinn_machine.json_machine import (machine_from_json, to_json_path)


class TestJsonMachine(unittest.TestCase):

    def setUp(self):
        unittest_setup()
        set_config("Machine", "version", 5)

    def test_json_version_5_hole(self):
        set_config("Machine", "down_chips", "3,3")
        vm = virtual_machine(width=8, height=8)
        MachineDataWriter.mock().set_machine(vm)
        jpath = mktemp("json")
        to_json_path(jpath)
        jm = machine_from_json(jpath)
        vstr = str(vm).replace("Virtual", "")
        jstr = str(jm).replace("Json", "")
        self.assertEqual(vstr, jstr)
        for vchip, jchip in zip(vm, jm):
            self.assertEqual(str(vchip), str(jchip))

    def test_exceptions(self):
        vm = virtual_machine(width=8, height=8)
        MachineDataWriter.mock().set_machine(vm)
        chip22 = vm[2, 2]
        router22 = chip22.router
        router22._n_available_multicast_entries =  \
            router22._n_available_multicast_entries - 20
        chip33 = vm[3, 3]
        chip33._sdram = 50000000
        chip33._tag_ids = [2, 3]
        jpath = mktemp("json")
        to_json_path(jpath)
        jm = machine_from_json(jpath)
        for vchip, jchip in zip(vm, jm):
            self.assertEqual(str(vchip), str(jchip))
        vchip33 = jm[3, 3]
        self.assertEqual(vchip33.tag_ids, chip33.tag_ids)

    def test_monitor_exceptions(self):
        vm = virtual_machine(width=8, height=8)
        MachineDataWriter.mock().set_machine(vm)
        chip02 = vm[0, 2]
        # Hack in an extra monitor
        users = dict(chip02._placable_processors)
        monitors = dict(chip02._scamp_processors)
        monitors[1] = users.pop(1)
        chip02._scamp_processors = monitors
        chip02._placable_processors = users
        jpath = mktemp("json")
        # Should still be able to write json even with more than one monitor
        to_json_path(jpath)
        # However we dont need to support reading back with more than 1 monitor
        with self.assertRaises(NotImplementedError):
            machine_from_json(jpath)

    def test_ethernet_exceptions(self):
        vm = virtual_machine(width=16, height=16)
        MachineDataWriter.mock().set_machine(vm)
        chip48 = vm[4, 8]
        router48 = chip48.router
        router48._n_available_multicast_entries =  \
            router48._n_available_multicast_entries - 20
        chip48._sdram = 50000000
        chip48._tag_ids = [2, 3]
        jpath = mktemp("json")
        to_json_path(jpath)
        jm = machine_from_json(jpath)
        for vchip, jchip in zip(vm, jm):
            self.assertEqual(str(vchip), str(jchip))
        vchip48 = jm[4, 8]
        self.assertEqual(vchip48.tag_ids, chip48.tag_ids)


if __name__ == '__main__':
    unittest.main()
