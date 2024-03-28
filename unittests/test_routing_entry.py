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
from spinn_machine import RoutingEntry
from spinn_machine.config_setup import unittest_setup
from spinn_machine.exceptions import SpinnMachineInvalidParameterException


class TestRoutingEntry(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_creating_new_routing_entry(self):
        link_ids = list()
        proc_ids = list()
        for i in range(6):
            link_ids.append(i)
        for i in range(18):
            proc_ids.append(i)
        a_multicast = RoutingEntry(
            processor_ids=proc_ids, link_ids=link_ids,
            defaultable=True)

        self.assertEqual(a_multicast.link_ids, set(link_ids))
        self.assertEqual(a_multicast.processor_ids, set(proc_ids))
        # While we're here, let's check a few other basic operations
        self.assertEqual(str(a_multicast),
                         "{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, "
                         "15, 16, 17}:{0, 1, 2, 3, 4, 5}(defaultable)")
        self.assertEqual(
            a_multicast,
            pickle.loads(pickle.dumps(a_multicast, pickle.HIGHEST_PROTOCOL)))
        hash(a_multicast)

    def test_spinnaker_route(self):
        multicast1 = RoutingEntry(processor_ids=[1, 3, 4, 16],
                                  link_ids=[2, 3, 5])
        self.assertEqual(4196012, multicast1.spinnaker_route)
        multicast2 = RoutingEntry(spinnaker_route=4196012)
        self.assertEqual(multicast2.processor_ids, {1, 3, 4, 16})
        # Third test getting the link_ids first
        multicast3 = RoutingEntry(spinnaker_route=4196012)
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
        a_multicast = RoutingEntry(
            processor_ids=proc_ids, link_ids=link_ids,
            defaultable=True)
        b_multicast = RoutingEntry(
            processor_ids=proc_ids2, link_ids=link_ids2,
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

        self.assertEqual(result_multicast.link_ids, set(comparison_link_ids))
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
        a_multicast = RoutingEntry(
            processor_ids=proc_ids, link_ids=link_ids,
            defaultable=True)
        b_multicast = RoutingEntry(
            processor_ids=proc_ids2, link_ids=link_ids2,
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

        self.assertEqual(result_multicast.link_ids, set(comparison_link_ids))
        self.assertEqual(result_multicast.processor_ids,
                         set(comparison_proc_ids))
        self.assertNotEqual(result_multicast, a_multicast)
        self.assertNotEqual(result_multicast, b_multicast)

    """
    From FixedRouteEntry use or loose
    def test_fixed_route_errors(self):
        with self.assertRaises(SpinnMachineAlreadyExistsException) as e:
            FixedRouteEntry([1, 2, 2], [2, 3, 4])
        self.assertEqual(e.exception.item, "processor ID")
        self.assertEqual(e.exception.value, "2")
        with self.assertRaises(SpinnMachineAlreadyExistsException) as e:
            FixedRouteEntry([1, 2, 3], [2, 3, 2])
        self.assertEqual(e.exception.item, "link ID")
        self.assertEqual(e.exception.value, "2")
    """


if __name__ == '__main__':
    unittest.main()
