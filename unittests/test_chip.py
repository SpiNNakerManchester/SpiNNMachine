__author__ = 'Petrut'

import unittest
from spinn_machine import processor as proc , link as link , sdram as sdram, router as router, chip as chip
import spinn_machine.exceptions as exc
from collections import OrderedDict
class TestingChip(unittest.TestCase):
    def test_create_chip(self):
        flops = 1000
        (E, NE, N, W, SW, S) = range(6)

        processors = list()
        for i in range(18):
            processors.append(proc.Processor(i, flops))

        links = list()
        links.append(link.Link(0,0,0,0,1,S,S))

        SDRAM = sdram.SDRAM(128)
        x= 0
        y= 1

        links = list()

        links.append(link.Link(0,0,0,1,1,N,N))
        links.append(link.Link(0,1,1,1,0,S,S))
        links.append(link.Link(1,1,2,0,0,E,E))
        links.append(link.Link(1,0,3,0,1,W,W))
        r = router.Router(links,False,100,1024)

        ip = "192.162.240.253"

        new_chip = chip.Chip(x,y,processors,r, SDRAM,ip)

        self.assertEqual(new_chip.x,x)
        self.assertEqual(new_chip.y,y)
        self.assertEqual(new_chip.ip_address,ip)
        self.assertEqual(new_chip.sdram,SDRAM)
        self.assertEqual(new_chip.router,r)
        for p in processors:
            self.assertTrue(p in new_chip.processors)

    def test_create_chip_with_duplicate_processors(self):
        with self.assertRaises(exc.SpinnMachineAlreadyExistsException):
            flops = 1000
            (E, NE, N, W, SW, S) = range(6)

            processors = list()
            for i in range(18):
                processors.append(proc.Processor(i, flops))
            processors.append(proc.Processor(10,flops+1))

            links = list()
            links.append(link.Link(0,0,0,0,1,S,S))

            SDRAM = sdram.SDRAM(128)
            x= 0
            y= 1

            links = list()

            links.append(link.Link(0,0,0,1,1,N,N))
            links.append(link.Link(0,1,1,1,0,S,S))
            links.append(link.Link(1,1,2,0,0,E,E))
            links.append(link.Link(1,0,3,0,1,W,W))
            r = router.Router(links,False,100,1024)

            ip = "192.162.240.253"

            new_chip = chip.Chip(x,y,processors,r, SDRAM,ip)


if __name__ == '__main__':
    unittest.main()
