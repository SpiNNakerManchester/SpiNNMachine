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
from spinn_machine import Router, Link, MulticastRoutingEntry
from spinn_machine.config_setup import unittest_setup
from spinn_machine.exceptions import (
    SpinnMachineAlreadyExistsException, SpinnMachineInvalidParameterException)


class TestingRouter(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_creating_new_router(self):
        links = list()
        links.append(Link(0, 0, 0, 1, 1))
        links.append(Link(0, 1, 1, 1, 0))
        links.append(Link(1, 1, 2, 0, 0))
        links.append(Link(1, 0, 3, 0, 1))
        r = Router(links, False, 1024)

        self.assertEqual(len(r), 4)
        for i in range(4):
            self.assertTrue(r.is_link(i))
            self.assertTrue(i in r)
            self.assertEqual(r.get_link(i), links[i])
            self.assertEqual(r[i], links[i])
        self.assertEqual([link[0] for link in r], [0, 1, 2, 3])
        self.assertEqual([link[1].source_link_id for link in r], [0, 1, 2, 3])

        self.assertFalse(r.emergency_routing_enabled)
        self.assertEqual(r.n_available_multicast_entries, 1024)

        self.assertFalse(r.is_link(-1))
        self.assertFalse(r.is_link(links.__len__() + 1))
        self.assertEqual(r.get_link(-1), None)
        self.assertEqual(r.get_link(links.__len__() + 1), None)

        self.assertEqual(r.get_neighbouring_chips_coords(),
                         [{'x': 1, 'y': 1}, {'x': 1, 'y': 0},
                          {'x': 0, 'y': 0}, {'x': 0, 'y': 1}])
        self.assertEqual(
            r.__repr__(),
            "[Router: emergency_routing=False, "
            "available_entries=1024, links=["
            "[Link: source_x=0, source_y=0, source_link_id=0, "
            "destination_x=1, destination_y=1], "
            "[Link: source_x=0, source_y=1, source_link_id=1, "
            "destination_x=1, destination_y=0], "
            "[Link: source_x=1, source_y=1, source_link_id=2, "
            "destination_x=0, destination_y=0], "
            "[Link: source_x=1, source_y=0, source_link_id=3, "
            "destination_x=0, destination_y=1]]]")

    def test_creating_new_router_with_emergency_routing_on(self):
        links = list()
        (e, ne, n, w, sw, s) = range(6)
        links.append(Link(0, 0, 0, 0, 1))
        links.append(Link(0, 1, 1, 0, 1))
        r = Router(links, True, 1024)
        self.assertTrue(r.emergency_routing_enabled)

    def test_creating_new_router_with_duplicate_links(self):
        links = list()
        (e, ne, n, w, sw, s) = range(6)
        links.append(Link(0, 0, 0, 0, 1))
        links.append(Link(0, 1, 0, 0, 1))
        with self.assertRaises(SpinnMachineAlreadyExistsException):
            Router(links, False, 1024)

    def test_convert_to_route(self):
        e = MulticastRoutingEntry(28, 60, [4, 5, 7], [1, 3, 5], True)
        r = Router.convert_routing_table_entry_to_spinnaker_route(e)
        self.assertEqual(r, 11306)

    def test_bad_processor(self):
        e = MulticastRoutingEntry(28, 60, [4, 5, -1], [1, 3, 5], True)
        with self.assertRaises(SpinnMachineInvalidParameterException):
            Router.convert_routing_table_entry_to_spinnaker_route(e)

    def test_bad_link(self):
        e = MulticastRoutingEntry(28, 60, [4, 5, 7], [1, 3, 15], True)
        with self.assertRaises(SpinnMachineInvalidParameterException):
            Router.convert_routing_table_entry_to_spinnaker_route(e)


if __name__ == '__main__':
    unittest.main()
