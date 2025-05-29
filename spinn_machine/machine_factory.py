# Copyright (c) 2019 The University of Manchester
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

from collections import defaultdict
import logging
from typing import Collection, Iterable, Set, Tuple
from spinn_utilities.config_holder import get_config_bool
from spinn_utilities.log import FormatAdapter
from spinn_utilities.typing.coords import XY
from spinn_machine import Chip, Router, Machine
from spinn_machine.data import MachineDataView
from .exceptions import SpinnMachineException

logger = FormatAdapter(logging.getLogger(__name__))


def _machine_ignore(
        original: Machine, dead_chips: Collection[XY],
        dead_links: Set[Tuple[int, int, int, int]]) -> Machine:
    """
    Creates a near copy of the machine without the dead bits.

    Creates a new Machine with the the Chips that where in the original
    machine but are not listed as dead.

    Each Chip will only have the links that already existed and are not listed
    as dead.

    Spinnaker_links and fpga_links are re-added so removing a wrap around link
    could results in and extra spiNNaker or FPGA link.

    Dead Chips or links not in the original machine are ignored.

    Does not change the original machine!

    :param original: Machine to make a near copy of
    :param dead_chips: Collection of dead chips' (x, y) coordinates
    :param dead_links: Collection of dead links' (x, y, direction) coordinates
    :return: A New Machine object
    """
    new_machine = MachineDataView.get_machine_version().create_machine(
        original.width, original.height, "Fixed")
    links_map = defaultdict(set)
    for x, y, d, _ in dead_links:
        links_map[(x, y)].add(d)
    for chip in original.chips:
        if chip in dead_chips:
            continue
        if chip in links_map:
            links = []
            for link in chip.router.links:
                if link.source_link_id not in links_map[chip]:
                    links.append(link)
            router = Router(links, chip.router.n_available_multicast_entries)
            chip = Chip(
                chip.x, chip.y, chip.scamp_processors_ids,
                chip.placable_processors_ids, router, chip.sdram,
                chip.nearest_ethernet_x, chip.nearest_ethernet_y,
                chip.ip_address, chip.tag_ids)
        new_machine.add_chip(chip)
    new_machine.add_spinnaker_links()
    new_machine.add_fpga_links()
    new_machine.validate()
    return new_machine


def _generate_uni_direction_link_error(
        dest_x: int, dest_y: int, src_x: int, src_y: int, out: int, back: int,
        original: Machine) -> str:
    # get the chips so we can find Ethernet's and local ids
    dest_chip = original.get_chip_at(dest_x, dest_y)
    src_chip = original[src_x, src_y]
    src_ethernet = original[
        src_chip.nearest_ethernet_x, src_chip.nearest_ethernet_y].ip_address

    # if the dest chip is dead. Only report src chip IP address.
    if dest_chip is None:
        return f"Link {out} from {src_chip} to {dest_x}:{dest_y} points to " \
               f"a dead chip. Chip {src_x}:{src_y} resides on board with ip " \
               f"address {src_ethernet}. " \
               f"Please report this to spinnakerusers@googlegroups.com \n\n"

    # got working chips, so get the separate Ethernet's
    dest_ethernet = original[
        dest_chip.nearest_ethernet_x, dest_chip.nearest_ethernet_y].ip_address

    # get board local ids
    (local_src_chip_x, local_src_chip_y) = original.get_local_xy(src_chip)
    (local_dest_chip_x, local_dest_chip_y) = original.get_local_xy(dest_chip)

    # generate bespoke error message based off if they both reside on same
    # board.
    if src_ethernet == dest_ethernet:
        return f"Link {back} from {dest_chip} to {src_chip} does not exist, " \
               f"but the opposite does. Both chips live on the same board " \
               f"under ip address {src_ethernet} and are local chip " \
               f"ids {local_dest_chip_x}:{local_dest_chip_y} and " \
               f"{local_src_chip_x}:{local_src_chip_y}. " \
               f"Please report this to spinnakerusers@googlegroups.com \n\n"
    else:
        return f"Link {back} from {dest_chip} to {src_chip} does not exist, " \
               f"but the opposite does. The chips live on different boards. " \
               f"chip {dest_x}:{dest_y} resides on board with ip address " \
               f"{dest_ethernet} with local id {local_dest_chip_x}:" \
               f"{local_dest_chip_y} and chip {src_x}:{src_y} resides on " \
               f"board with ip address {src_ethernet} with local id " \
               f"{local_src_chip_x}:{local_src_chip_y}. " \
               f"Please report this to spinnakerusers@googlegroups.com \n\n"


def machine_repair(
        original: Machine, removed_chips: Iterable[XY] = ()) -> Machine:
    """
    Remove chips that can't be reached or that can't reach other chips
    due to missing links.

    Also remove any one way links.

    :param original: the original machine
    :param removed_chips: List of chips (x and y coordinates) that have been
        removed while the machine was being created.
        One-way links to these chip are expected repairs so always done and
        never logged
    :raises SpinnMachineException: if repair_machine is false and an unexpected
        repair is needed.
    :return: Either the original machine or a repaired replacement
    """
    repair_machine = get_config_bool("Machine", "repair_machine")
    dead_chips: Set[XY] = set()
    dead_links: Set[Tuple[int, int, int, int]] = set()

    # holder for error message
    error_message = ""

    for xy in original.unreachable_incoming_local_chips():
        chip = original[xy[0], xy[1]]
        error_xy = original.get_local_xy(chip)
        ethernet = original[chip.nearest_ethernet_x, chip.nearest_ethernet_y]
        msg = f"Your machine has unreachable incoming chips at {error_xy} " \
              f"on board {ethernet} which will cause algorithms to fail. " \
              f"Please report this to spinnakerusers@googlegroups.com \n\n"
        if repair_machine:
            dead_chips.add(xy)
            logger.warning(msg)
        else:
            logger.error(msg)
            error_message += msg
    for xy in original.unreachable_outgoing_local_chips():
        chip = original[xy[0], xy[1]]
        error_xy = original.get_local_xy(chip)
        ethernet = original[chip.nearest_ethernet_x, chip.nearest_ethernet_y]
        msg = f"Your machine has unreachable outgoing chips at {error_xy} " \
              f"on board {ethernet} which will cause algorithms to fail. " \
              f"Please report this to spinnakerusers@googlegroups.com \n\n"
        if repair_machine:
            dead_chips.add(xy)
            logger.warning(msg)
        else:
            logger.error(msg)
            error_message += msg
    for (source_x, source_y, out, back) in original.one_way_links():
        (dest_x, dest_y) = original.xy_over_link(source_x, source_y, out)
        if (dest_x, dest_y) in removed_chips:
            dead_links.add((source_x, source_y, out, back))
        else:
            uni_direction_link_message = _generate_uni_direction_link_error(
                dest_x, dest_y, source_x, source_y, out, back, original)
            if repair_machine:
                dead_links.add((source_x, source_y, out, back))
                logger.warning(uni_direction_link_message)
            else:
                logger.error(uni_direction_link_message)
                error_message += uni_direction_link_message

    for chip in original.chips:
        if chip.parent_link is not None:
            parent_x, parent_y = original.xy_over_link(
                chip.x, chip.y, chip.parent_link)
            if not original.is_chip_at(parent_x, parent_y):
                ethernet = original[chip.nearest_ethernet_x,
                                    chip.nearest_ethernet_y]
                msg = f"The source: {Chip} will fail to receive signals " \
                      f"because its parent {parent_x}:{parent_y} in the " \
                      f"signal tree has disappeared from the machine since " \
                      f"it was booted. This occurred on board with " \
                      f"ip address {ethernet.ip_address} " \
                      f"Please report this to " \
                      f"spinnakerusers@googlegroups.com \n\n"
                if repair_machine:
                    dead_chips.add(chip)
                    logger.warning(msg)
                else:
                    logger.error(msg)
                    error_message += msg

    if not repair_machine and error_message != "":
        raise SpinnMachineException(error_message)

    if not dead_chips and not dead_links:
        return original

    new_machine = _machine_ignore(original, dead_chips, dead_links)
    return machine_repair(new_machine)
