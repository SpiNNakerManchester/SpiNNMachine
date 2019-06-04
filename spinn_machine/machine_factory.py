from .no_wrap_machine import NoWrapMachine
from .horizontal_wrap_machine import HorizontalWrapMachine
from .vertical_wrap_machine import VerticalWrapMachine
from .full_wrap_machine import FullWrapMachine
try:
    from collections.abc import defaultdict
except ImportError:
    from collections import defaultdict
from spinn_machine import (Chip, Router)
from .exceptions import SpinnMachineException

BAD_MSG = "Your machine has {} at {} on board {} which will cause " \
          "algorithms to fail. " \
          "Please report this to spinnakerusers@googlegroups.com "


def machine_from_size(width, height, chips=None, origin=None):
    """
    Create a machine with the assumed wrap-around based on the sizes.

    This could include a machine with no wrap-arounds, only vertical ones,
    only horizontal ones or both.

    Note: If the sizes do not match the ones for a known wrap-around machine,
    no wrap-arounds is assumed.

    :param width: The width of the machine excluding any virtual chips
    :param height: The height of the machine excluding any virtual chips
    :param chips: Any chips to be added.
    :param origin: Extra information about how this machine was created
        to be used in the str method. Example "Virtual" or "Json"
    :return: A subclass of Machine
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
    :return: A subclass of Machine
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

    Creates a new Machine with the the Chips that where in the orginal machine
        but are not listed as dead.

    Each Chip will only have the links that already existed and are not listed
        as dead.

    Spinnaker_links and fpga_links are readded so removing a wrap around link
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
    for x, y, d in dead_links:
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
                             chip.router.clock_speed,
                             chip.router.n_available_multicast_entries)
            chip = Chip(
                chip.x, chip.y, chip.processors, router, chip.sdram,
                chip.nearest_ethernet_x, chip.nearest_ethernet_y,
                chip.ip_address, chip.virtual, chip.tag_ids)
        new_machine.add_chip(chip)
    new_machine.add_spinnaker_links()
    new_machine.add_fpga_links()
    new_machine.validate()
    return new_machine


def machine_repair(original, repair_machine=False):
    """ Remove chips that can't be reached or that can't reach other chips\
        due to missing links

        Also Reomve and one way links
    """
    dead_chips = set()
    dead_links = set()
    for xy in original.unreachable_incoming_chips():
        if repair_machine:
            dead_chips.add(xy)
        else:
            chip = original.get_chip_at(xy[0], xy[1])
            ethernet = original.get_chip_at(
                chip.nearest_ethernet_x, chip.nearest_ethernet_y)
            raise SpinnMachineException(
                BAD_MSG.format(
                    "unreachable incoming chips", xy, ethernet.ip_address))
    for xy in original.unreachable_outgoing_chips():
        if repair_machine:
            dead_chips.add(xy)
        else:
            chip = original.get_chip_at(xy[0], xy[1])
            ethernet = original.get_chip_at(
                chip.nearest_ethernet_x, chip.nearest_ethernet_y)
            raise SpinnMachineException(
                BAD_MSG.format(
                    "unreachable outcoming chips", xy, ethernet.ip_address))
    for xyd in original.one_way_links():
        if repair_machine:
            dead_links.add(xyd)
        else:
            chip = original.get_chip_at(xyd[0], xyd[1])
            ethernet = original.get_chip_at(
                chip.nearest_ethernet_x, chip.nearest_ethernet_y)
            raise SpinnMachineException(
                BAD_MSG.format("One way links", xyd, ethernet.ip_address))
    if len(dead_chips) == 0 and len(dead_links) == 0:
        return original
    new_machine = _machine_ignore(original, dead_chips, dead_links)
    return machine_repair(new_machine, repair_machine)
