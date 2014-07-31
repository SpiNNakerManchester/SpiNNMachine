import unittest
import spinn_machine.sdram as sdram
import spinn_machine.exceptions as exc


class TestingSDRAM(unittest.TestCase):
    def test_creating_new_sdram_object(self):
        ram = sdram.SDRAM(128)
        self.assertEqual(ram.size, 128)

    def test_creating_new_sdram_with_zero_size(self):
        ram = sdram.SDRAM(0)
        self.assertEqual(ram.size, 0)

    def test_creating_sdram_with_negative_size(self):
        with self.assertRaises(exc.SpinnMachineInvalidParameterException):
            sdram.SDRAM(-64)


if __name__ == '__main__':
    unittest.main()
