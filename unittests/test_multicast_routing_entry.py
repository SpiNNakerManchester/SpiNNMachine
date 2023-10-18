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

import pickle
import unittest
from spinn_machine import MulticastRoutingEntry
from spinn_machine.config_setup import unittest_setup
from spinn_machine.exceptions import SpinnMachineInvalidParameterException


class TestMulticastRoutingEntry(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_creating_new_multicast_routing_entry(self):
        link_ids = list()
        proc_ids = list()
        for i in range(6):
            link_ids.append(i)
        for i in range(18):
            proc_ids.append(i)
        key = 1
        mask = 1
        a_multicast = MulticastRoutingEntry(
            key, mask, processor_ids=proc_ids, link_ids=link_ids,
            defaultable=True)

        self.assertEqual(a_multicast.routing_entry_key, key)
        self.assertEqual(a_multicast.link_ids, set(link_ids))
        self.assertEqual(a_multicast.mask, mask)
        self.assertEqual(a_multicast.processor_ids, set(proc_ids))
        # While we're here, let's check a few other basic operations
        self.assertEqual(str(a_multicast),
                         "1:1:True:{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,"
                         " 12, 13, 14, 15, 16, 17}:{0, 1, 2, 3, 4, 5}")
        self.assertEqual(
            a_multicast,
            pickle.loads(pickle.dumps(a_multicast, pickle.HIGHEST_PROTOCOL)))
        hash(a_multicast)

    def test_bad_key_mask(self):
        with self.assertRaises(SpinnMachineInvalidParameterException):
            MulticastRoutingEntry(1, 2)

    def test_spinnaker_route(self):
        multicast1 = MulticastRoutingEntry(1, 1, processor_ids=[1, 3, 4, 16],
                                           link_ids=[2, 3, 5])
        self.assertEqual(4196012, multicast1.spinnaker_route)
        multicast2 = MulticastRoutingEntry(1, 1, spinnaker_route=4196012)
        self.assertEqual(multicast2.processor_ids, {1, 3, 4, 16})
        # Third test getting the link_ids first
        multicast3 = MulticastRoutingEntry(1, 1, spinnaker_route=4196012)
        self.assertEqual(multicast3.link_ids, {2, 3, 5})
        self.assertEqual(multicast3.processor_ids, {1, 3, 4, 16})

    def test_merger(self):
        link_ids = list()
        link_ids2 = list()
        proc_ids = list()
        proc_ids2 = list()
        for i in range(3):
            link_ids.append(i)
        for i in range(3, 6):
            link_ids2.append(i)
        for i in range(9):
            proc_ids.append(i)
        for i in range(9, 18):
            proc_ids2.append(i)
        key = 1
        mask = 1
        a_multicast = MulticastRoutingEntry(
            key, mask, processor_ids=proc_ids, link_ids=link_ids,
            defaultable=True)
        b_multicast = MulticastRoutingEntry(
            key, mask, processor_ids=proc_ids2, link_ids=link_ids2,
            defaultable=True)

        result_multicast = a_multicast.merge(b_multicast)
        comparison_link_ids = list()
        comparison_proc_ids = list()
        for i in range(6):
            comparison_link_ids.append(i)
        self.assertEqual(link_ids + link_ids2, comparison_link_ids)
        for i in range(18):
            comparison_proc_ids.append(i)
        self.assertEqual(proc_ids + proc_ids2, comparison_proc_ids)

        self.assertEqual(result_multicast.routing_entry_key, key)
        self.assertEqual(result_multicast.link_ids, set(comparison_link_ids))
        self.assertEqual(result_multicast.mask, mask)
        self.assertEqual(result_multicast.processor_ids,
                         set(comparison_proc_ids))

    def test_merger_with_different_defaultable(self):
        link_ids = list()
        link_ids2 = list()
        proc_ids = list()
        proc_ids2 = list()
        for i in range(3):
            link_ids.append(i)
        for i in range(3, 6):
            link_ids2.append(i)
        for i in range(9):
            proc_ids.append(i)
        for i in range(9, 18):
            proc_ids2.append(i)
        key = 1
        mask = 1
        a_multicast = MulticastRoutingEntry(
            key, mask, processor_ids=proc_ids, link_ids=link_ids,
            defaultable=True)
        b_multicast = MulticastRoutingEntry(
            key, mask, processor_ids=proc_ids2, link_ids=link_ids2,
            defaultable=False)

        result_multicast = a_multicast.merge(b_multicast)
        comparison_link_ids = list()
        comparison_proc_ids = list()
        for i in range(6):
            comparison_link_ids.append(i)
        self.assertEqual(link_ids + link_ids2, comparison_link_ids)
        for i in range(18):
            comparison_proc_ids.append(i)
        self.assertEqual(proc_ids + proc_ids2, comparison_proc_ids)

        self.assertEqual(result_multicast.routing_entry_key, key)
        self.assertEqual(result_multicast.link_ids, set(comparison_link_ids))
        self.assertEqual(result_multicast.mask, mask)
        self.assertEqual(result_multicast.processor_ids,
                         set(comparison_proc_ids))
        self.assertEqual(result_multicast, a_multicast + b_multicast)
        self.assertEqual(result_multicast, a_multicast | b_multicast)
        self.assertNotEqual(result_multicast, a_multicast)
        self.assertNotEqual(result_multicast, b_multicast)

    def test_merger_with_invalid_parameter_key(self):
        link_ids = list()
        link_ids2 = list()
        proc_ids = list()
        proc_ids2 = list()
        for i in range(3):
            link_ids.append(i)
        for i in range(3, 6):
            link_ids2.append(i)
        for i in range(9):
            proc_ids.append(i)
        for i in range(9, 18):
            proc_ids2.append(i)
        key_combo = 1
        mask = 1
        a_multicast = MulticastRoutingEntry(
            key_combo, mask, processor_ids=proc_ids, link_ids=link_ids,
            defaultable=True)
        b_multicast = MulticastRoutingEntry(
            key_combo + 1, mask + 1, processor_ids=proc_ids2,
            link_ids=link_ids2, defaultable=True)
        with self.assertRaises(SpinnMachineInvalidParameterException) as e:
            a_multicast.merge(b_multicast)
        self.assertEqual(e.exception.parameter, "other.key")
        self.assertEqual(e.exception.value, "0x2")
        self.assertEqual(e.exception.problem, "The key does not match 0x1")

    def test_merger_with_invalid_parameter_mask(self):
        link_ids = list()
        link_ids2 = list()
        proc_ids = list()
        proc_ids2 = list()
        for i in range(3):
            link_ids.append(i)
        for i in range(3, 6):
            link_ids2.append(i)
        for i in range(9):
            proc_ids.append(i)
        for i in range(9, 18):
            proc_ids2.append(i)
        key = 0
        mask = 2
        a_multicast = MulticastRoutingEntry(
            key, mask, processor_ids=proc_ids, link_ids=link_ids,
            defaultable=True)
        b_multicast = MulticastRoutingEntry(
            key, 4, processor_ids=proc_ids2, link_ids=link_ids2,
            defaultable=True)
        self.assertNotEqual(a_multicast, b_multicast)
        self.assertNotEqual(a_multicast, "foo")
        with self.assertRaises(SpinnMachineInvalidParameterException):
            a_multicast.merge(b_multicast)


if __name__ == '__main__':
    unittest.main()
