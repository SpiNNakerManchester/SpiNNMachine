# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from tempfile import mktemp
import unittest
from spinn_machine import (SDRAM, virtual_machine)
from spinn_machine.json_machine import (machine_from_json, to_json_path)


class TestJsonMachine(unittest.TestCase):

    def test_json_version_5_hole(self):
        hole = [(3, 3)]
        vm = virtual_machine(version=5, down_chips=hole)
        jpath = mktemp("json")
        to_json_path(vm, jpath)
        jm = machine_from_json(jpath)
        vstr = str(vm).replace("Virtual", "")
        jstr = str(jm).replace("Json", "")
        self.assertEqual(vstr, jstr)
        for vchip, jchip in zip(vm, jm):
            self.assertEqual(str(vchip), str(jchip))

    def test_exceptions(self):
        vm = virtual_machine(version=5)
        chip22 = vm.get_chip_at(2, 2)
        router22 = chip22.router
        router22._clock_speed = router22._clock_speed - 10
        router22._n_available_multicast_entries =  \
            router22._n_available_multicast_entries - 20
        chip33 = vm.get_chip_at(3, 3)
        chip33._sdram = SDRAM(50000000)
        chip33._tag_ids = [2, 3]
        chip03 = vm.get_chip_at(0, 3)
        chip03._virtual = True
        jpath = mktemp("json")
        jpath = "temp.json"
        to_json_path(vm, jpath)
        jm = machine_from_json(jpath)
        vstr = str(vm).replace("Virtual", "")
        jstr = str(jm).replace("Json", "")
        self.assertEqual(vstr, jstr)
        for vchip, jchip in zip(vm, jm):
            print(vchip)
            print(jchip)
            self.assertEqual(str(vchip), str(jchip))


if __name__ == '__main__':
    unittest.main()
