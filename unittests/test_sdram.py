import unittest
from spinn_machine import SDRAM
from spinn_machine.exceptions import SpinnMachineInvalidParameterException


class TestingSDRAM(unittest.TestCase):
    def test_creating_new_sdram_object(self):
        ram = SDRAM(128)
        self.assertEquals(ram.size, 128)

    def test_creating_new_sdram_with_zero_size(self):
        ram = SDRAM(0)
        self.assertEquals(ram.size, 0)

    def test_creating_sdram_with_negative_size(self):
        with self.assertRaises(SpinnMachineInvalidParameterException):
            SDRAM(-64)


if __name__ == '__main__':
    unittest.main()
