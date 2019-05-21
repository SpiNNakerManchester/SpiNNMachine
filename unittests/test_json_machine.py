from tempfile import mktemp
import unittest
from spinn_machine import (SDRAM, VirtualMachine)
from spinn_machine.json_machine import (machine_from_json, to_json_path)


class TestJsonMachine(unittest.TestCase):

    def test_json_version_5_hole(self):
        hole = [(3, 3)]
        vm = VirtualMachine(version=5, down_chips=hole).machine
        jpath = mktemp("json")
        to_json_path(vm, jpath)
        jm = machine_from_json(jpath)
        vstr = str(vm).replace("VirtualMachine", "Machine")
        jstr = str(jm).replace("JsonMachine", "Machine")
        self.assertEquals(vstr, jstr)
        for vchip, jchip in zip(vm, jm):
            self.assertEqual(str(vchip), str(jchip))

    def test_exceptions(self):
        vm = VirtualMachine(version=5).machine
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
        vstr = str(vm).replace("VirtualMachine", "Machine")
        jstr = str(jm).replace("JsonMachine", "Machine")
        self.assertEqual(vstr, jstr)
        for vchip, jchip in zip(vm, jm):
            print(vchip)
            print(jchip)
            self.assertEqual(str(vchip), str(jchip))


if __name__ == '__main__':
    unittest.main()
