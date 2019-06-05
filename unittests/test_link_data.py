import unittest
from spinn_machine.link_data_objects import FPGALinkData, SpinnakerLinkData


class TestingLinks(unittest.TestCase):
    def test_fpga_link_data(self):
        ld = FPGALinkData(1, 2, 3, 4, 5, "somehost")
        ld2 = FPGALinkData(1, 2, 3, 4, 5, "somehost")
        ld3 = FPGALinkData(1, 2, 3, 4, 6, "somehost")
        self.assertEquals(ld.board_address, "somehost")
        self.assertEquals(ld.connected_chip_x, 3)
        self.assertEquals(ld.connected_chip_y, 4)
        self.assertEquals(ld.connected_link, 5)
        self.assertEquals(ld.fpga_id, 2)
        self.assertEquals(ld.fpga_link_id, 1)
        self.assertEquals(ld, ld2)
        self.assertNotEqual(ld, ld3)
        d = dict()
        d[ld] = 1
        d[ld2] = 2
        d[ld3] = 3
        self.assertEquals(len(d), 2)

    def test_spinnaker_link_data(self):
        ld = SpinnakerLinkData(2, 3, 4, 5, "somehost")
        ld2 = SpinnakerLinkData(2, 3, 4, 5, "somehost")
        ld3 = SpinnakerLinkData(2, 3, 4, 6, "somehost")
        self.assertEquals(ld.board_address, "somehost")
        self.assertEquals(ld.connected_chip_x, 3)
        self.assertEquals(ld.connected_chip_y, 4)
        self.assertEquals(ld.connected_link, 5)
        self.assertEquals(ld.spinnaker_link_id, 2)
        self.assertEquals(ld, ld2)
        self.assertNotEqual(ld, ld3)
        d = dict()
        d[ld] = 1
        d[ld2] = 2
        d[ld3] = 3
        self.assertEquals(len(d), 2)


if __name__ == '__main__':
    unittest.main()
