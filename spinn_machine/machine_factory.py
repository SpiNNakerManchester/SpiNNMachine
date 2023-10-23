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
    :type dead_chips: Collection (int, int)
    :param dead_links: Collection of dead links' (x, y, direction) coordinates
    :type dead_links: Collection of (int, int, int)
    :return: A New Machine object
    """
    new_machine = MachineDataView.get_machine_version().create_machine(
        original.width, original.height, "Fixed")
    links_map = defaultdict(set)
    for x, y, d, _ in dead_links:
        links_map[(x, y)].add(d)
    for chip in original.chips:
        if (chip.x, chip.y) in dead_chips:
            continue
        if (chip.x, chip.y) in links_map:
            links = []
            for link in chip.router.links:
                if link.source_link_id not in links_map[(chip.x, chip.y)]:
                    links.append(link)
            router = Router(links, chip.router.n_available_multicast_entries)
            chip = Chip(
                chip.x, chip.y, chip.n_processors, router, chip.sdram,
                chip.nearest_ethernet_x, chip.nearest_ethernet_y,
                chip.ip_address, chip.tag_ids)
        new_machine.add_chip(chip)
    new_machine.add_spinnaker_links()
    new_machine.add_fpga_links()
    new_machine.validate()
    return new_machine


def _generate_uni_direction_link_error(
        dest_x: int, dest_y: int, src_x: int, src_y: int, back: int,
        original: Machine) -> str:
    # get the chips so we can find ethernet's and local ids
    dest_chip = original.get_chip_at(dest_x, dest_y)
    src_chip = original[src_x, src_y]
    src_ethernet = original[
        src_chip.nearest_ethernet_x, src_chip.nearest_ethernet_y].ip_address

    # if the dest chip is dead. Only report src chip ip address.
    if dest_chip is None:
        return __link_dead_chip(back, src_chip, dest_x, dest_y, src_ethernet)

    # got working chips, so get the separate ethernet's
    dest_ethernet = original[
        dest_chip.nearest_ethernet_x, dest_chip.nearest_ethernet_y].ip_address

    # get board local ids
    (local_src_chip_x, local_src_chip_y) = original.get_local_xy(src_chip)
    (local_dest_chip_x, local_dest_chip_y) = original.get_local_xy(dest_chip)

    # generate bespoke error message based off if they both reside on same
    # board.
    if src_ethernet == dest_ethernet:
        return __one_link_same_board_msg(
            back, dest_chip, src_chip, src_ethernet, local_dest_chip_x,
            local_dest_chip_y, local_src_chip_x, local_src_chip_y)
    else:
        return one_link_different_boards_msg(
            back, dest_chip, src_chip,  dest_ethernet, local_dest_chip_x,
            local_dest_chip_y,   src_ethernet, local_src_chip_x,
            local_src_chip_y)


def machine_repair(original: Machine, removed_chips: Iterable[XY] = ()):
    """
    Remove chips that can't be reached or that can't reach other chips
    due to missing links.

    Also remove any one way links.

    :param original: the original machine
    :type original: Machine
    :param removed_chips: List of chips (x and y coordinates) that have been
        removed while the machine was being created.
        One-way links to these chip are expected repairs so always done and
        never logged
    :type removed_chips: list(tuple(int,int))
    :raises SpinnMachineException: if repair_machine is false and an unexpected
        repair is needed.
    :return: Either the original machine or a repaired replacement
    :rtype: Machine
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
        msg = __bad_message(
            "unreachable incoming chips", error_xy, ethernet.ip_address)
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
        msg = __bad_message(
            "unreachable outgoing chips", error_xy, ethernet.ip_address)
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
                dest_x, dest_y, source_x, source_y, back, original)
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
                ethernet_chip = original[
                    chip.nearest_ethernet_x, chip.nearest_ethernet_y]
                msg = __chip_dead_parent_msg(
                    chip, parent_x, parent_y, ethernet_chip.ip_address)
                if repair_machine:
                    dead_chips.add((chip.x, chip.y))
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


def __bad_message(issue: str, xp: XY, address: str) -> str:
    return f"Your machine has {issue} at {xp} on board {address} " \
           f"which will cause algorithms to fail. " \
           f"Please report this to spinnakerusers@googlegroups.com \n\n"


def __one_link_same_board_msg(
        link: int, source: Chip, target: Chip, address: str,
        source_x: int, source_y: int, target_x: int, target_y: int) -> str:
    return f"Link {link} from {source} to {target} does not exist, " \
           f"but the opposite does. Both chips live on the same board under " \
           f"ip address {address} and are local chip ids " \
           f"{source_x}:{source_y} and {target_x}:{target_y}. " \
           f"Please report this to spinnakerusers@googlegroups.com \n\n"


def one_link_different_boards_msg(
        link: int, source: Chip, target: Chip, source_x: int, source_y: int,
        source_address: str, target_x: int, target_y: int,
        target_address: str) -> str:
    return f"Link {link} from {source} to {target} does not exist, " \
           f"but the opposite does. The chips live on different boards. " \
           f"chip {source.x}:{source.y} resides on board with ip address " \
           f"{source_address} with local id {source_x}:{source_y} and " \
           f"chip {target.x}:{target.y} resides on board with ip address " \
           f"{target_address} with local id {target_x}:{target_y}. " \
           f"Please report this to spinnakerusers@googlegroups.com \n\n"


def __link_dead_chip(link: int, source: Chip, target_x: int, target_y: int,
                      address: str) -> str:
    return f"Link {link} from {source} to {target_x}:{target_y} " \
           f"points to a dead chip. Chip {source.x}:" \
           f"{source.y} resides on board with ip address {address}. " \
           f"Please report this to spinnakerusers@googlegroups.com \n\n"


def __chip_dead_parent_msg(
        source: Chip, parent_x: int, parent_y: int, address : str) -> str:
    return f"The {source: Chip} will fail to receive signals because its " \
           f"parent {parent_x}:{parent_y} in the signal tree has " \
           f"disappeared from the machine since it was booted. " \
           f"This occurred on board with ip address {address} " \
           f"Please report this to spinnakerusers@googlegroups.com \n\n"
