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
from spinn_machine.virtual_machine import (
    virtual_machine_by_boards, virtual_machine_by_min_size)
from spinn_machine.data.machine_data_writer import MachineDataWriter
from spinn_machine.config_setup import unittest_setup
from spinn_machine.json_machine import (machine_from_json, to_json_path)


class TestJsonMachine(unittest.TestCase):

    def setUp(self):
        unittest_setup()
        set_config("Machine", "version", 5)

    def test_json_version_5_hole(self):
        set_config("Machine", "down_chips", "3,3")
        vm = virtual_machine_by_min_size(width=8, height=8)
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
        vm = virtual_machine_by_min_size(width=8, height=8)
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
        vm = virtual_machine_by_boards(1)
        MachineDataWriter.mock().set_machine(vm)
        for chip in vm.chips:
            if chip.ip_address is None:
                break
        # Hack in an extra monitor
        chip._scamp_processors = tuple([0, 1])
        chip._placable_processors = tuple([2, 3, 4, 5, 6, 7, 8, 9])
        jpath = mktemp("json")
        # Should still be able to write json even with more than one monitor
        to_json_path(jpath)
        # However we dont need to support reading back with more than 1 monitor
        with self.assertRaises(NotImplementedError):
            machine_from_json(jpath)

    def test_ethernet_exceptions(self):
        vm = virtual_machine_by_boards(2)
        MachineDataWriter.mock().set_machine(vm)
        eth2 = vm.ethernet_connected_chips[1]
        router2 = eth2.router
        router2._n_available_multicast_entries =  \
            router2._n_available_multicast_entries - 20
        eth2._sdram = 50000000
        eth2._tag_ids = [2, 3]
        jpath = mktemp("json")
        to_json_path(jpath)
        jm = machine_from_json(jpath)
        for vchip, jchip in zip(vm, jm):
            self.assertEqual(str(vchip), str(jchip))
        jeth2 = jm.ethernet_connected_chips[1]
        self.assertEqual(jeth2.tag_ids, eth2.tag_ids)


if __name__ == '__main__':
    unittest.main()
