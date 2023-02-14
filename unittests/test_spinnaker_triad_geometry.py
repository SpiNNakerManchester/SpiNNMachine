# Copyright (c) 2017 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from spinn_machine import SpiNNakerTriadGeometry
from spinn_machine.config_setup import unittest_setup


class TestingGeometry(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_geom(self):
        # This table was produced using the code in Rig
        delta_table = [
            [(0, 0), (-1, 0), (-2, 0), (-3, 0), (-4, 0), (-1, -4),
             (-2, -4), (-3, -4), (-4, -4), (-5, -4), (-6, -4), (-7, -4)],
            [(0, -1), (-1, -1), (-2, -1), (-3, -1), (-4, -1), (-5, -1),
             (-2, -5), (-3, -5), (-4, -5), (-5, -5), (-6, -5), (-7, -5)],
            [(0, -2), (-1, -2), (-2, -2), (-3, -2), (-4, -2), (-5, -2),
             (-6, -2), (-3, -6), (-4, -6), (-5, -6), (-6, -6), (-7, -6)],
            [(0, -3), (-1, -3), (-2, -3), (-3, -3), (-4, -3), (-5, -3),
             (-6, -3), (-7, -3), (-4, -7), (-5, -7), (-6, -7), (-7, -7)],
            [(-4, 0), (-1, -4), (-2, -4), (-3, -4), (-4, -4), (-5, -4),
             (-6, -4), (-7, -4), (0, 0), (-1, 0), (-2, 0), (-3, 0)],
            [(-4, -1), (-5, -1), (-2, -5), (-3, -5), (-4, -5), (-5, -5),
             (-6, -5), (-7, -5), (0, -1), (-1, -1), (-2, -1), (-3, -1)],
            [(-4, -2), (-5, -2), (-6, -2), (-3, -6), (-4, -6), (-5, -6),
             (-6, -6), (-7, -6), (0, -2), (-1, -2), (-2, -2), (-3, -2)],
            [(-4, -3), (-5, -3), (-6, -3), (-7, -3), (-4, -7), (-5, -7),
             (-6, -7), (-7, -7), (0, -3), (-1, -3), (-2, -3), (-3, -3)],
            [(-4, -4), (-5, -4), (-6, -4), (-7, -4), (0, 0), (-1, 0),
             (-2, 0), (-3, 0), (-4, 0), (-1, -4), (-2, -4), (-3, -4)],
            [(-4, -5), (-5, -5), (-6, -5), (-7, -5), (0, -1), (-1, -1),
             (-2, -1), (-3, -1), (-4, -1), (-5, -1), (-2, -5), (-3, -5)],
            [(-4, -6), (-5, -6), (-6, -6), (-7, -6), (0, -2), (-1, -2),
             (-2, -2), (-3, -2), (-4, -2), (-5, -2), (-6, -2), (-3, -6)],
            [(-4, -7), (-5, -7), (-6, -7), (-7, -7), (0, -3), (-1, -3),
             (-2, -3), (-3, -3), (-4, -3), (-5, -3), (-6, -3), (-7, -3)]]
        g = SpiNNakerTriadGeometry.get_spinn5_geometry()
        for x in range(12):
            for y in range(12):
                px, py = delta_table[y][x]
                q = g.get_local_chip_coordinate(x, y)
                qx, qy = q
                self.assertEqual(
                    (-px, -py), q,
                    "x at ({},{}): expected ({},{}) but got ({},{})".format(
                        x, y, -px, -py, qx, qy))

    def test_get_potential_ethernet_chips(self):
        g = SpiNNakerTriadGeometry.get_spinn5_geometry()
        self.assertEqual(1, len(g.get_potential_ethernet_chips(2, 2)))
        self.assertEqual(1, len(g.get_potential_ethernet_chips(8, 8)))
        self.assertEqual(3, len(g.get_potential_ethernet_chips(12, 12)))
        self.assertEqual(3, len(g.get_potential_ethernet_chips(16, 16)))
        self.assertEqual(6, len(g.get_potential_ethernet_chips(20, 20)))
        self.assertEqual(12, len(g.get_potential_ethernet_chips(24, 24)))
        self.assertIn((0, 12), g.get_potential_ethernet_chips(20, 20))
        self.assertEqual(3, len(g.get_potential_ethernet_chips(16, 12)))


if __name__ == '__main__':
    unittest.main()
