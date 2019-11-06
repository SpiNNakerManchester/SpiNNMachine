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

import logging
import json
from collections import defaultdict, namedtuple, OrderedDict
from .chip import Chip
from .router import Router
from .sdram import SDRAM
from .link import Link
from .machine_factory import machine_from_size


logger = logging.getLogger(__name__)

# A description of a standard set of resources possessed by a chip
_Desc = namedtuple("_Desc", [
    # The cores where the monitors are
    "monitors",
    # The entries on the router
    "router_entries",
    # The amount of SDRAM on the chip
    "sdram",
    # Whether this is a virtual chip
    "virtual",
    # What tags this chip has
    "tags"])

JAVA_MAX_INT = 2147483647
OPPOSITE_LINK_OFFSET = 3


def machine_from_json(j_machine):
    """
    :param j_machine: JSON description of the machine
    :type j_machine: dict in format returned by json.load or a
        str representing a path to the JSON file
    :rtype: Machine
    """
    if isinstance(j_machine, str):
        with open(j_machine) as j_file:
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
            nearest_ethernet[0], nearest_ethernet[1], ip_address, False,
            tag_ids)
        machine.add_chip(chip)

    machine.add_spinnaker_links()
    machine.add_fpga_links()

    return machine


def _int_value(value):
    if value < JAVA_MAX_INT:
        return value
    else:
        return JAVA_MAX_INT


def _find_virtual_links(machine):
    """ Find all the virtual links and their inverse.

    As these may well go to an unexpected source

    :param machine: Machine to convert
    :return: Map of Chip to list of virtual links
    """
    virtual_links_dict = defaultdict(list)
    for chip in machine._virtual_chips:
        # assume all links need special treatment
        for link in chip.router.links:
            virtual_links_dict[chip].append(link)
            # Find and save inverse link as well
            inverse_id = ((link.source_link_id + OPPOSITE_LINK_OFFSET) %
                          Router.MAX_LINKS_PER_ROUTER)
            destination = machine.get_chip_at(
                link.destination_x, link.destination_y)
            inverse_link = destination.router.get_link(inverse_id)
            assert(inverse_link.destination_x == chip.x)
            assert(inverse_link.destination_y == chip.y)
            virtual_links_dict[destination].append(inverse_link)
    return virtual_links_dict


def _describe_chip(chip, std, eth, virtual_links_dict):
    """ Produce a JSON-suitable description of a single chip.

    :param chip: The chip to describe.
    :param std: The standard chip resources.
    :param eth: The standard ethernet chip resources.
    :param virtual_links_dict: Where the virtual links are.
    :return: Description of chip that is trivial to serialize as JSON.
    """
    details = OrderedDict()
    details["cores"] = chip.n_processors
    if chip.nearest_ethernet_x is not None:
        details["ethernet"] =\
            [chip.nearest_ethernet_x, chip.nearest_ethernet_y]

    dead_links = []
    for link_id in range(0, Router.MAX_LINKS_PER_ROUTER):
        if not chip.router.is_link(link_id):
            dead_links.append(link_id)
    if dead_links:
        details["deadLinks"] = dead_links

    if chip in virtual_links_dict:
        links = []
        for link in virtual_links_dict[chip]:
            link_details = OrderedDict()
            link_details["sourceLinkId"] = link.source_link_id
            link_details["destinationX"] = link.destination_x
            link_details["destinationY"] = link.destination_y
            links.append(link_details)
        details["links"] = links

    exceptions = OrderedDict()
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
        if chip.virtual != eth.virtual:
            exceptions["virtual"] = chip.virtual
        if chip.tag_ids != eth.tags:
            details["tags"] = list(chip.tag_ids)
    else:
        # Write the Resources ONLY if different from the s_values
        if (chip.n_processors - chip.n_user_processors) != std.monitors:
            exceptions["monitors"] = \
                chip.n_processors - chip.n_user_processors
        if router_entries != std.router_entries:
            exceptions["routerEntries"] = router_entries
        if chip.sdram.size != std.sdram:
            exceptions["sdram"] = chip.sdram.size
        if chip.virtual != std.virtual:
            exceptions["virtual"] = chip.virtual
        if chip.tag_ids != std.tags:
            details["tags"] = list(chip.tag_ids)

    if exceptions:
        return [chip.x, chip.y, details, exceptions]
    else:
        return [chip.x, chip.y, details]


def to_json(machine):
    """ Runs the code to write the machine in Java readable JSON.

    :param machine: Machine to convert
    :type machine: Machine
    :rtype: dict
    """

    # Find the std values for one non-ethernet chip to use as standard
    std = None
    for chip in machine.chips:
        if chip.ip_address is None:
            std = _Desc(
                monitors=chip.n_processors - chip.n_user_processors,
                router_entries=_int_value(
                    chip.router.n_available_multicast_entries),
                sdram=chip.sdram.size,
                virtual=chip.virtual,
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
        virtual=chip.virtual,
        tags=chip.tag_ids)

    # Save the standard data to be used as defaults to none ethernet chips
    standard_resources = OrderedDict()
    standard_resources["monitors"] = std.monitors
    standard_resources["routerEntries"] = std.router_entries
    standard_resources["sdram"] = std.sdram
    standard_resources["virtual"] = std.virtual
    standard_resources["tags"] = list(std.tags)

    # Save the standard data to be used as defaults to none ethernet chips
    ethernet_resources = OrderedDict()
    ethernet_resources["monitors"] = eth.monitors
    ethernet_resources["routerEntries"] = eth.router_entries
    ethernet_resources["sdram"] = eth.sdram
    ethernet_resources["virtual"] = eth.virtual
    ethernet_resources["tags"] = list(eth.tags)

    # write basic stuff
    json_obj = OrderedDict()
    json_obj["height"] = machine.height
    json_obj["width"] = machine.width
    # Could be removed but need to check all use case
    json_obj["root"] = [0, 0]
    json_obj["standardResources"] = standard_resources
    json_obj["ethernetResources"] = ethernet_resources
    json_obj["chips"] = []

    virtual_links_dict = _find_virtual_links(machine)

    # handle chips
    for chip in machine.chips:
        json_obj["chips"].append(_describe_chip(
            chip, std, eth, virtual_links_dict))

    return json_obj


def to_json_path(machine, file_path):
    """ Runs the code to write the machine in Java readable JSON.

    :param machine: Machine to convert
    :type machine: Machine
    :param file_path: Location to write file to. Warning will overwrite!
    :type file_path: str
    :rtype: None
    """
    json_obj = to_json(machine)

    # dump to json file
    with open(file_path, "w") as f:
        json.dump(json_obj, f)
