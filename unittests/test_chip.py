# Copyright (c) 2014 The University of Manchester
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

import unittest
from spinn_utilities.config_holder import set_config
from spinn_utilities.ordered_set import OrderedSet
from spinn_machine import Link, Router, Chip
from spinn_machine.config_setup import unittest_setup


class TestingChip(unittest.TestCase):

    def setUp(self):
        unittest_setup()
        set_config("Machine", "version", 5)
        self._x = 0
        self._y = 1

        # create processor
        self.n_processors = 18

        # create router
        links = list()
        links.append(Link(0, 0, 0, 1, 1))
        links.append(Link(0, 1, 1, 1, 0))
        links.append(Link(1, 1, 2, 0, 0))
        links.append(Link(1, 0, 3, 0, 1))
        self._router = Router(links, 1024)

        self._sdram = 128
        self._ip = "192.162.240.253"

    def _create_chip(self, x, y, processors, r, sdram, ip):
        return Chip(x, y, processors, r, sdram, 0, 0, ip)

    def test_create_chip(self):
        new_chip = self._create_chip(self._x, self._y, self.n_processors,
                                     self._router, self._sdram, self._ip)

        self.assertEqual(new_chip.x, self._x)
        self.assertEqual(new_chip.y, self._y)
        self.assertEqual(new_chip.ip_address, self._ip)
        self.assertEqual(new_chip.sdram, self._sdram)
        self.assertEqual(new_chip.router, self._router)
        self.assertEqual(new_chip.n_placable_processors, self.n_processors - 1)
        self.assertEqual(new_chip.n_placable_processors, self.n_processors - 1)
        print(new_chip.__repr__())
        self.assertEqual(
            "[Chip: x=0, y=1, ip_address=192.162.240.253 "
            "n_cores=18, mon=None]",
            new_chip.__repr__(),)
        self.assertEqual(new_chip.tag_ids, OrderedSet([1, 2, 3, 4, 5, 6, 7]))
        self.assertTrue(new_chip.is_processor_with_id(3))
        self.assertEqual(5, new_chip.get_processor_with_id(5).processor_id)
        self.assertIsNone(new_chip.get_processor_with_id(-1))

    def test_get_first_none_monitor_processor(self):
        """ test the get_first_none_monitor_processor

        NOTE: Not sure if method being tested is required.
        """
        new_chip = self._create_chip(self._x, self._y, self.n_processors,
                                     self._router, self._sdram, self._ip)
        non_monitor = new_chip.get_first_none_monitor_processor()
        self.assertFalse(non_monitor.is_monitor)

    def test_0_down(self):
        # Chip where 0 the monitor is down
        with self.assertRaises(NotImplementedError):
            Chip(1, 1, self.n_processors, self._router, self._sdram, 0, 0,
                 self._ip, down_cores=[0])

    def test_1_chip(self):
        # Chip with just 1 processor
        new_chip = Chip(1, 1, 1, self._router, self._sdram, 0, 0, self._ip)
        with self.assertRaises(Exception):
            new_chip.get_first_none_monitor_processor()

    def test_processors(self):
        new_chip = self._create_chip(self._x, self._y, self.n_processors,
                                     self._router, self._sdram, self._ip)
        all_p = set(new_chip.processors)
        self.assertEqual(len(all_p), new_chip.n_processors)
        self.assertEqual(len(all_p), len(set(new_chip.all_processor_ids)))
        users = set(new_chip.placeable_processors)
        self.assertEqual(len(users), new_chip.n_placable_processors)
        self.assertEqual(len(users),
                         len(set(new_chip.placable_processors_ids)))
        monitors = set(new_chip.scamp_processors)
        self.assertEqual(users.union(monitors), all_p)
        self.assertEqual(len(monitors),
                         len(set(new_chip.scamp_processors_ids)))

    def test_is_xy(self):
        chip24 = self._create_chip(
            2, 4, self.n_processors, self._router, self._sdram, None)
        chip36 = self._create_chip(
            3, 6, self.n_processors, self._router, self._sdram, None)
        chip00 = self._create_chip(
            0, 0, self.n_processors, self._router, self._sdram, self._ip)
        xy00 = (0, 0)
        xy36 = (3, 6)
        self.assertEqual(chip24, (2, 4))
        self.assertEqual((2, 4), chip24)
        self.assertEqual(chip00, xy00)
        self.assertEqual(xy00, chip00)
        self.assertNotEqual(chip00, (0, 0, 0))
        self.assertNotEqual((0, 0, 0), chip00)
        self.assertNotEqual(chip00, (0, 1))
        self.assertNotEqual((0, 1), chip00)
        self.assertEqual([chip24, chip00, chip36], [(2, 4), xy00, xy36])
        self.assertEqual([(2, 4), xy00, xy36], [chip24, chip00, chip36])
        self.assertEqual([chip24, xy00, chip36], [(2, 4), chip00, xy36])


if __name__ == '__main__':
    unittest.main()
