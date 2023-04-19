# Copyright (c) 2017 The University of Manchester
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

import logging
import json
from collections import namedtuple
from spinn_utilities.log import FormatAdapter
from spinn_machine.data import MachineDataView
from .chip import Chip
from .router import Router
from .sdram import SDRAM
from .link import Link
from .machine_factory import machine_from_size


logger = FormatAdapter(logging.getLogger(__name__))

# A description of a standard set of resources possessed by a chip
_Desc = namedtuple("_Desc", [
    # The cores where the monitors are
    "monitors",
    # The entries on the router
    "router_entries",
    # The amount of SDRAM on the chip
    "sdram",
    # What tags this chip has
    "tags"])

JAVA_MAX_INT = 2147483647
OPPOSITE_LINK_OFFSET = 3


def machine_from_json(j_machine):
    """
    Generate a model of a machine from a JSON description of that machine.

    :param j_machine: JSON description of the machine
    :type j_machine: dict in format returned by json.load or a
        str representing a path to the JSON file
    :return: The machine model.
    :rtype: Machine
    """
    if isinstance(j_machine, str):
        with open(j_machine, encoding="utf-8") as j_file:
            j_machine = json.load(j_file)

    # get the default values
    width = j_machine["width"]
    height = j_machine["height"]

    machine = machine_from_size(width, height, origin="Json")
    s_monitors = j_machine["standardResources"]["monitors"]
    s_router_entries = j_machine["standardResources"]["routerEntries"]
    s_sdram = SDRAM(j_machine["standardResources"]["sdram"])
    s_tag_ids = j_machine["standardResources"]["tags"]

    e_monitors = j_machine["ethernetResources"]["monitors"]
    e_router_entries = j_machine["ethernetResources"]["routerEntries"]
    e_sdram = SDRAM(j_machine["ethernetResources"]["sdram"])
    e_tag_ids = j_machine["ethernetResources"]["tags"]

    for j_chip in j_machine["chips"]:
        details = j_chip[2]
        source_x = j_chip[0]
        source_y = j_chip[1]
        nearest_ethernet = details["ethernet"]

        # get the details
        if "ipAddress" in details:
            ip_address = details["ipAddress"]
            router_entries = e_router_entries
            sdram = e_sdram
            tag_ids = e_tag_ids
            monitors = e_monitors
        else:
            ip_address = None
            router_entries = s_router_entries
            sdram = s_sdram
            tag_ids = s_tag_ids
            monitors = s_monitors
        if len(j_chip) > 3:
            exceptions = j_chip[3]
            if "monitors" in exceptions:
                monitors = exceptions["monitors"]
            if "routerEntries" in exceptions:
                router_entries = exceptions["routerEntries"]
            if "sdram" in exceptions:
                sdram = SDRAM(exceptions["sdram"])
            if "tags" in exceptions:
                tag_ids = exceptions["tags"]
        if monitors != 1:
            raise NotImplementedError(
                "We currently only support exactly 1 monitor per core")

        # create a router based on the details
        if "deadLinks" in details:
            dead_links = details["deadLinks"]
        else:
            dead_links = []
        links = []
        for source_link_id in range(6):
            if source_link_id not in dead_links:
                destination_x, destination_y = machine.xy_over_link(
                    source_x, source_y, source_link_id)
                links.append(Link(
                    source_x, source_y, source_link_id, destination_x,
                    destination_y))
        router = Router(links, False, router_entries)

        # Create and add a chip with this router
        chip = Chip(
            source_x, source_y, details["cores"], router, sdram,
            nearest_ethernet[0], nearest_ethernet[1], ip_address, tag_ids)
        machine.add_chip(chip)

    machine.add_spinnaker_links()
    machine.add_fpga_links()

    return machine


def _int_value(value):
    if value < JAVA_MAX_INT:
        return value
    else:
        return JAVA_MAX_INT


def _describe_chip(chip, std, eth):
    """
    Produce a JSON-suitable description of a single chip.

    :param chip: The chip to describe.
    :param std: The standard chip resources.
    :param eth: The standard Ethernet-enabled chip resources.
    :return: Description of chip that is trivial to serialize as JSON.
    """
    details = dict()
    details["cores"] = chip.n_processors
    if chip.nearest_ethernet_x is not None:
        details["ethernet"] = \
            [chip.nearest_ethernet_x, chip.nearest_ethernet_y]

    dead_links = []
    for link_id in range(0, Router.MAX_LINKS_PER_ROUTER):
        if not chip.router.is_link(link_id):
            dead_links.append(link_id)
    if dead_links:
        details["deadLinks"] = dead_links

    exceptions = dict()
    router_entries = _int_value(
        chip.router.n_available_multicast_entries)
    if chip.ip_address is not None:
        details['ipAddress'] = chip.ip_address
        # Write the Resources ONLY if different from the e_values
        if (chip.n_processors - chip.n_user_processors) != eth.monitors:
            exceptions["monitors"] = \
                chip.n_processors - chip.n_user_processors
        if router_entries != eth.router_entries:
            exceptions["routerEntries"] = router_entries
        if chip.sdram.size != eth.sdram:
            exceptions["sdram"] = chip.sdram.size
        if chip.tag_ids != eth.tags:
            exceptions["tags"] = list(chip.tag_ids)
    else:
        # Write the Resources ONLY if different from the s_values
        if (chip.n_processors - chip.n_user_processors) != std.monitors:
            exceptions["monitors"] = \
                chip.n_processors - chip.n_user_processors
        if router_entries != std.router_entries:
            exceptions["routerEntries"] = router_entries
        if chip.sdram.size != std.sdram:
            exceptions["sdram"] = chip.sdram.size
        if chip.tag_ids != std.tags:
            exceptions["tags"] = list(chip.tag_ids)

    if exceptions:
        return [chip.x, chip.y, details, exceptions]
    else:
        return [chip.x, chip.y, details]


def to_json():
    """
    Runs the code to write the machine in Java readable JSON.

    :rtype: dict
    """
    machine = MachineDataView.get_machine()
    # Find the std values for one non-ethernet chip to use as standard
    std = None
    for chip in machine.chips:
        if chip.ip_address is None:
            std = _Desc(
                monitors=chip.n_processors - chip.n_user_processors,
                router_entries=_int_value(
                    chip.router.n_available_multicast_entries),
                sdram=chip.sdram.size,
                tags=chip.tag_ids)
            break
    else:
        # Probably ought to warn if std is unpopulated
        pass

    # find the eth values to use for ethernet chips
    chip = machine.boot_chip
    eth = _Desc(
        monitors=chip.n_processors - chip.n_user_processors,
        router_entries=_int_value(
            chip.router.n_available_multicast_entries),
        sdram=chip.sdram.size,
        tags=chip.tag_ids)

    # Save the standard data to be used as defaults to none ethernet chips
    standard_resources = dict()
    standard_resources["monitors"] = std.monitors
    standard_resources["routerEntries"] = std.router_entries
    standard_resources["sdram"] = std.sdram
    standard_resources["tags"] = list(std.tags)

    # Save the standard data to be used as defaults to none ethernet chips
    ethernet_resources = dict()
    ethernet_resources["monitors"] = eth.monitors
    ethernet_resources["routerEntries"] = eth.router_entries
    ethernet_resources["sdram"] = eth.sdram
    ethernet_resources["tags"] = list(eth.tags)

    # write basic stuff
    json_obj = dict()
    json_obj["height"] = machine.height
    json_obj["width"] = machine.width
    # Could be removed but need to check all use case
    json_obj["root"] = [0, 0]
    json_obj["standardResources"] = standard_resources
    json_obj["ethernetResources"] = ethernet_resources
    json_obj["chips"] = []

    # handle chips
    for chip in machine.chips:
        json_obj["chips"].append(_describe_chip(chip, std, eth))

    return json_obj


def to_json_path(file_path):
    """
    Runs the code to write the machine in Java readable JSON.

    :param file_path: Location to write file to. Warning will overwrite!
    :type file_path: str
    :rtype: None
    """
    json_obj = to_json()

    # dump to json file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(json_obj, f)
