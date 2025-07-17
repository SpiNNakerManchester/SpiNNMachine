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
from typing import NamedTuple, Union
from spinn_utilities.log import FormatAdapter
from spinn_utilities.typing.json import JsonArray, JsonObject, JsonValue
from spinn_machine.data import MachineDataView
from .chip import Chip
from .router import Router
from .link import Link
from .machine import Machine

logger = FormatAdapter(logging.getLogger(__name__))
JAVA_MAX_INT = 2147483647
OPPOSITE_LINK_OFFSET = 3


class _Desc(NamedTuple):
    """
    A description of a standard set of resources possessed by a chip.
    """

    #: The cores where the monitors are
    monitors: int
    #: The entries on the router
    router_entries: int
    #: The amount of SDRAM on the chip
    sdram: int
    #: What tags this chip has
    tags: JsonArray


def _int(value: JsonValue) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value)
    raise ValueError(
        f"unsupported value type for integer field: {type(value)}")


def _str(value: JsonValue) -> str:
    if isinstance(value, str):
        return value
    raise ValueError(
        f"unsupported value type for string field: {type(value)}")


def _ary(value: JsonValue) -> JsonArray:
    if isinstance(value, list):
        return value
    raise ValueError(
        f"unsupported value type for array field: {type(value)}")


def _obj(value: JsonValue) -> JsonObject:
    if isinstance(value, dict):
        return value
    raise ValueError(
        f"unsupported value type for object field: {type(value)}")


def machine_from_json(j_machine: Union[JsonObject, str]) -> Machine:
    """
    Generate a model of a machine from a JSON description of that machine.

    :param j_machine: JSON description of the machine
    :return: The machine model.
    """
    if isinstance(j_machine, str):
        with open(j_machine, encoding="utf-8") as j_file:
            j_machine = _obj(json.load(j_file))

    # get the default values
    width = _int(j_machine["width"])
    height = _int(j_machine["height"])

    machine = MachineDataView.get_machine_version().create_machine(
        width, height, origin="Json")
    s_monitors = _obj(j_machine["standardResources"])["monitors"]
    s_router_entries = _int(_obj(
        j_machine["standardResources"])["routerEntries"])
    s_sdram = _int(_obj(j_machine["standardResources"])["sdram"])
    s_tag_ids = _ary(_obj(j_machine["standardResources"])["tags"])

    eth_res = _obj(j_machine["ethernetResources"])
    e_monitors = eth_res["monitors"]
    e_router_entries = _int(eth_res["routerEntries"])
    e_sdram = _int(eth_res["sdram"])
    e_tag_ids = _ary(eth_res["tags"])

    for aj_chip in _ary(j_machine["chips"]):
        j_chip = _ary(aj_chip)
        details = _obj(j_chip[2])
        source_x = _int(j_chip[0])
        source_y = _int(j_chip[1])
        board_x, board_y = _ary(details["ethernet"])

        # get the details
        if "ipAddress" in details:
            ip_address = _str(details["ipAddress"])
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
            exceptions = _obj(j_chip[3])
            if "monitors" in exceptions:
                monitors = exceptions["monitors"]
            if "routerEntries" in exceptions:
                router_entries = _int(exceptions["routerEntries"])
            if "sdram" in exceptions:
                sdram = _int(exceptions["sdram"])
            if "tags" in exceptions:
                tag_ids = _ary(exceptions["tags"])
        if monitors != 1:
            raise NotImplementedError(
                "We currently only support exactly 1 monitor per core")

        # create a router based on the details
        if "deadLinks" in details:
            dead_links = _ary(details["deadLinks"])
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
        router = Router(links, router_entries)

        # Create and add a chip with this router
        n_cores = _int(details["cores"])
        chip = Chip(
            source_x, source_y, [0], range(1, n_cores), router, sdram,
            _int(board_x), _int(board_y), ip_address, [
                _int(tag) for tag in tag_ids])
        machine.add_chip(chip)

    machine.add_spinnaker_links()
    machine.add_fpga_links()

    return machine


def _int_value(value: int) -> int:
    if value < JAVA_MAX_INT:
        return value
    else:
        return JAVA_MAX_INT


# pylint: disable=wrong-spelling-in-docstring
def _describe_chip(chip: Chip, standard: _Desc, ethernet: _Desc) -> JsonArray:
    """
    Produce a JSON-suitable description of a single chip.

    :param chip: The chip to describe.
    :param standard: The standard chip resources.
    :param ethernet: The standard Ethernet-enabled chip resources.
    :return: Description of chip that is trivial to serialize as JSON.
    """
    details: JsonObject = {
        "cores": chip.n_processors}
    if chip.nearest_ethernet_x is not None:
        details["ethernet"] = \
            [chip.nearest_ethernet_x, chip.nearest_ethernet_y]

    dead_links: JsonArray = [
        link_id
        for link_id in range(Router.MAX_LINKS_PER_ROUTER)
        if not chip.router.is_link(link_id)]
    if dead_links:
        details["deadLinks"] = dead_links

    exceptions: JsonObject = dict()
    router_entries = _int_value(
        chip.router.n_available_multicast_entries)
    tags: JsonArray = list(chip.tag_ids)
    if chip.ip_address is not None:
        details['ipAddress'] = chip.ip_address
        # Write the Resources ONLY if different from the e_values
        if (chip.n_scamp_processors) != ethernet.monitors:
            exceptions["monitors"] = chip.n_scamp_processors
        if router_entries != ethernet.router_entries:
            exceptions["routerEntries"] = router_entries
        if chip.sdram != ethernet.sdram:
            exceptions["sdram"] = chip.sdram
        if tags != ethernet.tags:
            exceptions["tags"] = tags
    else:
        # Write the Resources ONLY if different from the s_values
        if (chip.n_scamp_processors) != standard.monitors:
            exceptions["monitors"] = chip.n_scamp_processors
        if router_entries != standard.router_entries:
            exceptions["routerEntries"] = router_entries
        if chip.sdram != standard.sdram:
            exceptions["sdram"] = chip.sdram
        if tags != standard.tags:
            exceptions["tags"] = tags

    if exceptions:
        return [chip.x, chip.y, details, exceptions]
    else:
        return [chip.x, chip.y, details]


def to_json() -> JsonObject:
    """
    Runs the code to write the machine in Java readable JSON.

    :returns: The Machine as a json readable dict.
    """
    machine = MachineDataView.get_machine()
    # find the standard values to use for Ethernet chips
    chip = machine.boot_chip
    eth = _Desc(
        monitors=chip.n_processors - chip.n_placable_processors,
        router_entries=_int_value(
            chip.router.n_available_multicast_entries),
        sdram=chip.sdram,
        tags=list(chip.tag_ids))

    # Find the standard values for any non-Ethernet chip to use by default
    if machine.n_chips > 1:
        for chip in machine.chips:
            if chip.ip_address is None:
                std = _Desc(
                    monitors=chip.n_processors - chip.n_placable_processors,
                    router_entries=_int_value(
                        chip.router.n_available_multicast_entries),
                    sdram=chip.sdram,
                    tags=list(chip.tag_ids))
                break
        else:
            raise ValueError("could not compute standard resources")
    else:
        std = eth

    # write basic stuff
    return {
        "height": machine.height,
        "width": machine.width,
        # Could be removed but need to check all use case
        "root": [0, 0],
        # Save the standard data to be used as defaults to none Ethernet chips
        "standardResources": {
            "monitors": std.monitors,
            "routerEntries": std.router_entries,
            "sdram": std.sdram,
            "tags": std.tags},
        # Save the standard data to be used as defaults to Ethernet chips
        "ethernetResources": {
            "monitors": eth.monitors,
            "routerEntries": eth.router_entries,
            "sdram": eth.sdram,
            "tags": eth.tags},
        # handle chips
        "chips": [
            _describe_chip(chip, std, eth)
            for chip in machine.chips]}


def to_json_path(file_path: str) -> None:
    """
    Runs the code to write the machine in Java readable JSON.

    :param file_path: Location to write file to. Warning will overwrite!
    """
    json_obj = to_json()

    # dump to json file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(json_obj, f)
