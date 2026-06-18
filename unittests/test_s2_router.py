# Copyright (c) 2026 SpiNNcloud
# Copyright (c) 2026 The University of Manchester
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

from parameterized import parameterized

from spinn_machine.link import Link
from spinn_machine.router import Router
from spinn_machine.config_setup import unittest_setup
from spinn_utilities.config_holder import set_config
from spinn_machine.version import GEN1_BOARD_TYPES, GEN2_BOARD_TYPES
from spinn_machine import MulticastRoutingEntry, RoutingEntry
from spinn_machine.exceptions import (SpinnMachineException,
                                      SpinnMachineInvalidParameterException)


class TestingS2Router(unittest.TestCase):

    def setUp(self) -> None:
        unittest_setup()

    def test_default_max_cores_in_router(self) -> None:
        """If no version is specified error
        """
        links: list[Link] = list()
        r = Router(links, 1024)
        with self.assertRaises(SpinnMachineException):
            r.max_cores_per_router()

    @parameterized.expand(GEN1_BOARD_TYPES)
    def test_max_cores_s1_router(self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
        links: list[Link] = list()
        r = Router(links, 1024)
        n_cores = r.max_cores_per_router()

        self.assertEqual(n_cores, 18)

    @parameterized.expand(GEN2_BOARD_TYPES)
    def test_max_cores_s2_router(self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
        # use defalut config to get machine with s2 chip
        links: list[Link] = list()
        r = Router(links, 1024)
        n_cores = r.max_cores_per_router()

        self.assertEqual(n_cores, 152, "spinnaker2 chip has only 152 cores")

    @parameterized.expand(GEN1_BOARD_TYPES)
    def test_convert_spinnaker1_route_to_routing_ids(
            self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
        links: list[Link] = list()
        r = Router(links, 1024)

        route1 = 1398101
        proc_ids1 = [0, 2, 4, 6, 8, 10, 12, 14]
        link_ids1 = [0, 2, 4]
        proc_ids, link_ids = r.convert_spinnaker_route_to_routing_ids(route1)

        self.assertEqual(proc_ids1, proc_ids)
        self.assertEqual(link_ids1, link_ids)

        route2 = 1431655765
        proc_ids2 = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
        link_ids2 = [0, 2, 4]
        proc_ids, link_ids = r.convert_spinnaker_route_to_routing_ids(route2)

        self.assertNotEqual(proc_ids2, proc_ids)
        self.assertEqual(link_ids2, link_ids)

    @parameterized.expand(GEN2_BOARD_TYPES)
    def test_convert_spinnaker2_route_to_routing_ids(
            self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
        links: list[Link] = list()
        r = Router(links, 1024)

        # consider route that requires 152 cores and
        # 6 link which will have 158 values in binary representation
        route1 = (2 ** 158) - 1
        len_proc_ids1 = 152
        len_link_ids1 = 6
        proc_ids, link_ids = r.convert_spinnaker_route_to_routing_ids(route1)

        self.assertEqual(len_proc_ids1, len(proc_ids))
        self.assertEqual(len_link_ids1, len(link_ids))

        route2 = 1431655765
        proc_ids2 = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
        link_ids2 = [0, 2, 4]
        proc_ids, link_ids = r.convert_spinnaker_route_to_routing_ids(route2)

        self.assertEqual(proc_ids2, proc_ids)
        self.assertEqual(link_ids2, link_ids)

    @parameterized.expand(GEN1_BOARD_TYPES)
    def test_routing_table_entry_to_spinnaker1_route(
            self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
        links: list[Link] = list()
        r = Router(links, 1024)
        proc_ids = list()
        link_ids = list()

        for i in range(6):
            link_ids.append(i)
        for i in range(18):
            proc_ids.append(i)

        key = 1
        mask = 1
        multicast1 = MulticastRoutingEntry(
            key, mask, RoutingEntry(processor_ids=proc_ids, link_ids=link_ids))
        route1 = 16777215

        route = r.convert_routing_table_entry_to_spinnaker_route(multicast1)
        self.assertEqual(route1, route)

        proc_ids = list()
        link_ids = list()

        for i in range(6):
            link_ids.append(i)
        for i in range(36):
            proc_ids.append(i)

        key = 1
        mask = 1
        multicast1 = MulticastRoutingEntry(
            key, mask, RoutingEntry(processor_ids=proc_ids, link_ids=link_ids))

        with self.assertRaises(
                SpinnMachineInvalidParameterException) as context:
            r.convert_routing_table_entry_to_spinnaker_route(multicast1)

        actual_error = context.exception
        error = ("It is invalid to set route.processor_ids to frozenset("
                 "{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, "
                 "17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, "
                 "32, 33, 34, 35}): Processor IDs must be between 0 and 17")
        self.assertEqual(
            str(actual_error),
            error
        )

    @parameterized.expand(GEN2_BOARD_TYPES)
    def test_routing_table_entry_to_spinnaker2_route(
            self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
        links: list[Link] = list()
        r = Router(links, 1024)
        proc_ids = list()
        link_ids = list()

        for i in range(6):
            link_ids.append(i)
        for i in range(50):
            proc_ids.append(i)

        key = 1
        mask = 1
        multicast1 = MulticastRoutingEntry(
            key, mask, RoutingEntry(processor_ids=proc_ids, link_ids=link_ids))
        route1 = 72057594037927935

        route = r.convert_routing_table_entry_to_spinnaker_route(multicast1)
        self.assertEqual(route1, route)

        proc_ids = list()
        link_ids = list()

        for i in range(6):
            link_ids.append(i)
        for i in range(153):
            proc_ids.append(i)

        key = 1
        mask = 1
        multicast1 = MulticastRoutingEntry(
            key, mask, RoutingEntry(processor_ids=proc_ids, link_ids=link_ids))

        with self.assertRaises(
                SpinnMachineInvalidParameterException) as context:
            r.convert_routing_table_entry_to_spinnaker_route(multicast1)

        actual_error = context.exception
        error = ("It is invalid to set route.processor_ids to frozenset("
                 "{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, "
                 "17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, "
                 "32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, "
                 "47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, "
                 "62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, "
                 "77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, "
                 "92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, "
                 "105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, "
                 "117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, "
                 "129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, "
                 "141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152}"
                 "): Processor IDs must be between 0 and 151")
        self.assertEqual(
            str(actual_error),
            error
        )
