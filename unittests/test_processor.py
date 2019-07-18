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

import unittest
from spinn_machine import Processor


class TestingProcessor(unittest.TestCase):
    def test_creating_processors(self):
        processors = list()
        flops = 1000
        for i in range(18):
            processors.append(Processor(i, flops))

        for _id in range(18):
            self.assertEqual(processors[_id].processor_id, _id)
            self.assertEqual(processors[_id].clock_speed, flops)
            self.assertFalse(processors[_id].is_monitor)

    def test_creating_monitor_processors(self):
        processors = list()
        flops = 1000
        for i in range(18):
            processors.append(Processor(i, flops, is_monitor=True))

        for _id in range(18):
            self.assertEqual(processors[_id].processor_id, _id)
            self.assertEqual(processors[_id].clock_speed, flops)
            self.assertTrue(processors[_id].is_monitor)

    def test_creating_processors_with_negative_clock_speed(self):
        with self.assertRaises(Exception):
            Processor(processor_id=1, clock_speed=-5)


if __name__ == '__main__':
    unittest.main()
