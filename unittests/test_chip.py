__author__ = 'Petrut'

import unittest
import spinn_machine.processor as proc
import spinn_machine.link as link
import spinn_machine.sdram as sdram

class TestingChip(unittest.TestCase):
    def test_create_chip(self):
        #self.assertEqual(True, False)
        #new_chip = Chip(0,0,proc.Processor(0))
        processors = list()
        for i in range(18):
            processors.append(proc.Processor(i))

        links = list()
        for i in range(6):
            links.append(link.Link())

        SDRAM = sdram.SDRAM(128)



if __name__ == '__main__':
    unittest.main()
