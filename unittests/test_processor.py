# Copyright (c) 2017-2023 The University of Manchester
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
from spinn_machine import Processor
from spinn_machine.config_setup import unittest_setup


class TestingProcessor(unittest.TestCase):

    def setUp(self):
        unittest_setup()

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
