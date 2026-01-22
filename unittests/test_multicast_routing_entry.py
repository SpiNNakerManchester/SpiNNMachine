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
from typing import List
import unittest
from spinn_machine import MulticastRoutingEntry, RoutingEntry
from spinn_machine.config_setup import unittest_setup
from spinn_machine.exceptions import SpinnMachineInvalidParameterException


class TestMulticastRoutingEntry(unittest.TestCase):

    def setUp(self) -> None:
        unittest_setup()

    def test_creating_new_multicast_routing_entry(self) -> None:
        link_ids = list()
        proc_ids = list()
        for i in range(6):
            link_ids.append(i)
        for i in range(18):
            proc_ids.append(i)
        key = 1
        mask = 1
        a_multicast = MulticastRoutingEntry(
            key, mask, RoutingEntry(processor_ids=proc_ids, link_ids=link_ids))

        self.assertEqual(a_multicast.key, key)
        self.assertEqual(a_multicast.link_ids, set(link_ids))
        self.assertEqual(a_multicast.mask, mask)
        self.assertEqual(a_multicast.processor_ids, set(proc_ids))
        # While we're here, let's check a few other basic operations
        self.assertEqual(
            str(a_multicast),
            "0x00000001:0x00000001:"
            "{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17}:"
            "{0, 1, 2, 3, 4, 5}")
        self.assertEqual(
            a_multicast,
            pickle.loads(pickle.dumps(a_multicast, pickle.HIGHEST_PROTOCOL)))
        hash(a_multicast)

    def test_creating_defaulatble_multicast_routing_entry(self) -> None:
        link_ids = list()
        proc_ids: List[int] = list()
        link_ids.append(2)
        key = 1
        mask = 1
        a_multicast = MulticastRoutingEntry(
            key, mask, RoutingEntry(
                processor_ids=proc_ids, link_ids=link_ids, incoming_link=5))

        self.assertEqual(a_multicast.key, key)
        self.assertEqual(a_multicast.link_ids, set(link_ids))
        self.assertEqual(a_multicast.mask, mask)
        self.assertEqual(a_multicast.processor_ids, set(proc_ids))
        # While we're here, let's check a few other basic operations
        self.assertEqual(
            str(a_multicast),
            "0x00000001:0x00000001:{}:{2}(defaultable)")
        self.assertEqual(
            a_multicast,
            pickle.loads(pickle.dumps(a_multicast, pickle.HIGHEST_PROTOCOL)))
        hash(a_multicast)

    def test_bad_key_mask(self) -> None:
        with self.assertRaises(SpinnMachineInvalidParameterException):
            MulticastRoutingEntry(1, 2, None)  # type: ignore[arg-type]

    def test_spinnaker_route(self) -> None:
        multicast1 = MulticastRoutingEntry(1, 1, RoutingEntry(
            processor_ids=[1, 3, 4, 16], link_ids=[2, 3, 5]))
        self.assertEqual(4196012, multicast1.spinnaker_route)
        multicast2 = MulticastRoutingEntry(
            1, 1, RoutingEntry(spinnaker_route=4196012))
        self.assertEqual(multicast2.processor_ids, {1, 3, 4, 16})
        # Third test getting the link_ids first
        multicast3 = MulticastRoutingEntry(1, 1, RoutingEntry(
            spinnaker_route=4196012))
        self.assertEqual(multicast3.link_ids, {2, 3, 5})
        self.assertEqual(multicast3.processor_ids, {1, 3, 4, 16})

    def test_merger(self) -> None:
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
            key, mask, RoutingEntry(
                processor_ids=proc_ids, link_ids=link_ids))
        b_multicast = MulticastRoutingEntry(key, mask, RoutingEntry(
            processor_ids=proc_ids2, link_ids=link_ids2))

        result_multicast = a_multicast.merge(b_multicast)
        comparison_link_ids = list()
        comparison_proc_ids = list()
        for i in range(6):
            comparison_link_ids.append(i)
        self.assertEqual(link_ids + link_ids2, comparison_link_ids)
        for i in range(18):
            comparison_proc_ids.append(i)
        self.assertEqual(proc_ids + proc_ids2, comparison_proc_ids)

        self.assertEqual(result_multicast.key, key)
        self.assertEqual(result_multicast.link_ids,
                         set(comparison_link_ids))
        self.assertEqual(result_multicast.mask, mask)
        self.assertEqual(result_multicast.processor_ids,
                         set(comparison_proc_ids))

    def test_merger_with_different_defaultable(self) -> None:
        key = 1
        mask = 1
        a_multicast = MulticastRoutingEntry(key, mask, RoutingEntry(
            processor_ids=[], link_ids=[3], incoming_link=6))
        assert a_multicast.defaultable
        b_multicast = MulticastRoutingEntry(key, mask, RoutingEntry(
            processor_ids=[], link_ids=[3], incoming_link=4))
        assert not b_multicast.defaultable

        result_multicast = a_multicast.merge(b_multicast)

        self.assertEqual(result_multicast.key, key)
        self.assertEqual(result_multicast.link_ids, set([3]))
        self.assertEqual(result_multicast.mask, mask)
        self.assertEqual(result_multicast.processor_ids, set())
        assert not result_multicast.defaultable

    def test_merger_with_invalid_parameter_key(self) -> None:
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
        entry = RoutingEntry(
            processor_ids=proc_ids, link_ids=link_ids)
        a_multicast = MulticastRoutingEntry(key_combo, mask, entry)
        b_multicast = MulticastRoutingEntry(key_combo + 1, mask + 1, entry)
        with self.assertRaises(SpinnMachineInvalidParameterException) as e:
            a_multicast.merge(b_multicast)
        self.assertEqual(e.exception.parameter, "other.key")
        self.assertEqual(e.exception.value, "0x2")
        self.assertEqual(e.exception.problem, "The key does not match 0x1")

    def test_merger_with_invalid_parameter_mask(self) -> None:
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
        a_multicast = MulticastRoutingEntry(key, mask, RoutingEntry(
            processor_ids=proc_ids, link_ids=link_ids))
        b_multicast = MulticastRoutingEntry(key, 4, RoutingEntry(
            processor_ids=proc_ids2, link_ids=link_ids2))
        self.assertNotEqual(a_multicast, b_multicast)
        self.assertNotEqual(a_multicast, "foo")
        with self.assertRaises(SpinnMachineInvalidParameterException):
            a_multicast.merge(b_multicast)

    def test_double_incoming(self) -> None:
        with self.assertRaises(SpinnMachineInvalidParameterException):
            RoutingEntry(link_ids=range(6), processor_ids=range(18),
                         incoming_processor=4, incoming_link=3)


if __name__ == '__main__':
    unittest.main()
