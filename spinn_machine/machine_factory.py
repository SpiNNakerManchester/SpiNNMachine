# Copyright (c) 2019 The University of Manchester
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
from collections import defaultdict
from spinn_utilities.log import FormatAdapter
from spinn_machine import (Chip, Router)
from .no_wrap_machine import NoWrapMachine
from .horizontal_wrap_machine import HorizontalWrapMachine
from .vertical_wrap_machine import VerticalWrapMachine
from .full_wrap_machine import FullWrapMachine
from .exceptions import SpinnMachineException

logger = FormatAdapter(logging.getLogger(__name__))

BAD_MSG = (
    "Your machine has {} at {} on board {} which will cause algorithms to "
    "fail. Please report this to spinnakerusers@googlegroups.com \n\n")
ONE_LINK_SAME_BOARD_MSG = (
    "Link {} from global chip id {}:{} to global chip id {}:{} does not "
    "exist, but the opposite does. Both chips live on the same board under "
    "ip address {} and are local chip ids {}:{} and {}:{}. "
    "Please report this to spinnakerusers@googlegroups.com \n\n")
ONE_LINK_DIFFERENT_BOARDS_MSG = (
    "Link {} from global chip id {}:{} to global chip id {}:{} does not "
    "exist, but the opposite does. The chips live on different boards. "
    "chip {}:{} resides on board with ip address {} with local id {}:{} and "
    "chip {}:{} resides on board with ip address {} with local id {}:{}. "
    "Please report this to spinnakerusers@googlegroups.com \n\n")
ONE_LINK_DEAD_CHIP = (
    "Link {} from global dead chip id {}:{} to global chip id {}:{} does not "
    "exist, but the opposite does. chip {}:{} resides on board with ip "
    "address {} but as chip {}:{} is dead, we cannot report its ip address. "
    "Please report this to spinnakerusers@googlegroups.com \n\n")
CHIP_REMOVED_BY_DEAD_PARENT = (
    "The chip {}:{} will fail to receive signals because its parent {}:{} in"
    " the signal tree has disappeared from the machine since it was booted. "
    "This occurred on board with ip address {} Please report this to "
    "spinnakerusers@googlegroups.com \n\n")


def machine_from_size(width, height, chips=None, origin=None):
    """
    Create a machine with the assumed wrap-around based on the sizes.

    This could include a machine with no wrap-arounds, only vertical ones,
    only horizontal ones or both.

    Note: If the sizes do not match the ones for a known wrap-around machine,
    no wrap-arounds is assumed.

    :param width: The width of the machine excluding any virtual chips
    :type width: int
    :param height: The height of the machine excluding any virtual chips
    :type height: int
    :param chips: Any chips to be added.
    :type chips: list(Chip) or None
    :param origin: Extra information about how this machine was created
        to be used in the str method. Example "Virtual" or "Json"
    :type origin: str or None
    :return: A subclass of Machine
    :rtype: Machine
    """
    if chips is None:
        chips = []
    if width == 2 and height == 2:
        return FullWrapMachine(width, height, chips, origin)
    if width % 12 == 0:
        if height % 12 == 0:
            return FullWrapMachine(width, height, chips, origin)
        else:
            return HorizontalWrapMachine(width, height, chips, origin)
    else:
        if height % 12 == 0:
            return VerticalWrapMachine(width, height, chips, origin)
        else:
            return NoWrapMachine(width, height, chips, origin)


def machine_from_chips(chips):
    """
    Create a machine with the assumed wrap-around based on the sizes.

    The size of the machine is calculated from the list of chips.

    :param chips: Full list of all chips on this machine.
        Or at least a list which includes a chip with the highest X and
        one with the highest Y (excluding any virtual chips)
    :type chips: list(Chip)
    :return: A subclass of Machine
    :rtype: Machine
    """
    max_x = 0
    max_y = 0
    for chip in chips:
        if chip.x > max_x:
            max_x = chip.x
        if chip.y > max_y:
            max_y = chip.y
    return machine_from_size(max_x + 1, max_y + 1, chips)


def _machine_ignore(original, dead_chips, dead_links):
    """ Creates a near copy of the machine without the dead bits.

    Creates a new Machine with the the Chips that where in the original
        machine but are not listed as dead.

    Each Chip will only have the links that already existed and are not listed
        as dead.

    Spinnaker_links and fpga_links are re-added so removing a wrap around link
        could results in and extra spinnaker or fpga link.

    Dead Chips or links not in the original machine are ignored.

    Does not change the original machine!

    :param original: Machine to make a near copy of
    :param dead_chips: Collection of dead chips x and y cooridnates
    :type dead_chips: Collection (int, int)
    :param dead_links: Collection of dead link x y and direction cooridnates
    :type dead_links: Collection of (int, int, int)
    :return: A New Machine object
    """
    new_machine = machine_from_size(original.width, original.height)
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
            router = Router(links, chip.router.emergency_routing_enabled,
                            chip.router.n_available_multicast_entries)
            chip = Chip(
                chip.x, chip.y, chip.n_processors, router, chip.sdram,
                chip.nearest_ethernet_x, chip.nearest_ethernet_y,
                chip.ip_address, chip.virtual, chip.tag_ids)
        new_machine.add_chip(chip)
    new_machine.add_spinnaker_links()
    new_machine.add_fpga_links()
    new_machine.validate()
    return new_machine


def _generate_uni_direction_link_error(
        dest_x, dest_y, src_x, srx_y, back, original):
    # get the chips so we can find ethernet's and local ids
    dest_chip = original.get_chip_at(dest_x, dest_y)
    src_chip = original.get_chip_at(src_x, srx_y)
    src_ethernet = original.get_chip_at(
        src_chip.nearest_ethernet_x, src_chip.nearest_ethernet_y).ip_address

    # if the dest chip is dead. Only report src chip ip address.
    if dest_chip is None:
        return ONE_LINK_DEAD_CHIP.format(
            back, dest_x, dest_y, src_x, srx_y, src_x, srx_y, src_ethernet,
            dest_x, dest_y)

    # got working chips, so get the separate ethernet's
    dest_ethernet = original.get_chip_at(
        dest_chip.nearest_ethernet_x, dest_chip.nearest_ethernet_y).ip_address

    # get board local ids
    (local_src_chip_x, local_src_chip_y) = original.get_local_xy(src_chip)
    (local_dest_chip_x, local_dest_chip_y) = original.get_local_xy(dest_chip)

    # generate bespoke error message based off if they both reside on same
    # board.
    if src_ethernet == dest_ethernet:
        return ONE_LINK_SAME_BOARD_MSG.format(
            back, dest_x, dest_y, src_x, srx_y, src_ethernet,
            local_dest_chip_x, local_dest_chip_y, local_src_chip_x,
            local_src_chip_y)
    else:
        return ONE_LINK_DIFFERENT_BOARDS_MSG.format(
            back, dest_x, dest_y, src_x, srx_y, dest_x, dest_y, dest_ethernet,
            local_dest_chip_x, local_dest_chip_y, src_x, srx_y, src_ethernet,
            local_src_chip_x, local_src_chip_y)


def machine_repair(original, repair_machine=False, removed_chips=tuple()):
    """ Remove chips that can't be reached or that can't reach other chips\
        due to missing links.

        Also remove any one way links.

    :param original: the original machine
    :type original: Machine
    :param repair_machine: A flag to say if the machine requires unexpected
        repairs.
        It True the unexpected repairs are logged and then done
        If false will raise an exception if the machine needs an unexpected
        repair
    :type repair_machine: bool
    :param removed_chips: List of chips (x and y coordinates) that have been
        removed while the machine was being created.
        Oneway links to these chip are expected repairs so always done and
        never logged
    :type removed_chips: list(tuple(int,int))
    :raises SpinnMachineException: if repair_machine is false and an unexpected
        repair is needed.
    :return: Either the original machine or a repaired replacement
    :rtype: Machine
    """
    dead_chips = set()
    dead_links = set()

    # holder for error message
    error_message = ""

    for xy in original.unreachable_incoming_local_chips():
        chip = original.get_chip_at(xy[0], xy[1])
        error_xy = original.get_local_xy(chip)
        ethernet = original.get_chip_at(
            chip.nearest_ethernet_x, chip.nearest_ethernet_y)
        msg = BAD_MSG.format(
            "unreachable incoming chips", error_xy, ethernet.ip_address)
        if repair_machine:
            dead_chips.add(xy)
            logger.warning(msg)
        else:
            logger.error(msg)
            error_message += msg
    for xy in original.unreachable_outgoing_local_chips():
        chip = original.get_chip_at(xy[0], xy[1])
        error_xy = original.get_local_xy(chip)
        ethernet = original.get_chip_at(
            chip.nearest_ethernet_x, chip.nearest_ethernet_y)
        msg = BAD_MSG.format(
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
                ethernet_chip = original.get_chip_at(
                    chip.nearest_ethernet_x, chip.nearest_ethernet_y)
                msg = CHIP_REMOVED_BY_DEAD_PARENT.format(
                    chip.x, chip.y, parent_x, parent_y,
                    ethernet_chip.ip_address)
                if repair_machine:
                    dead_chips.add((chip.x, chip.y))
                    logger.warning(msg)
                else:
                    logger.error(msg)
                    error_message += msg

    if not repair_machine and error_message != "":
        raise SpinnMachineException(error_message)

    if len(dead_chips) == 0 and len(dead_links) == 0:
        return original

    new_machine = _machine_ignore(original, dead_chips, dead_links)
    return machine_repair(new_machine, repair_machine)
