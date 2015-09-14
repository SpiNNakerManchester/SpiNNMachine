"""
utility functions for computing information about a machine without having a\
machine object
"""
from spinn_machine.spinnaker_link_data import SpinnakerLinkData


def get_closest_chips_to(chip_x, chip_y, max_x, max_y, invalid_chips):
    """ Get the closest chip to a given chip coordinates

    :param chip_x: the chip coord in x axis for looking for closest to
    :param chip_y: the chip coord in y axis for looking for closest to
    :param max_x: the max x coord in the machine
    :param max_y: the max y coord in the machine
    :param invalid_chips: list of chips to not include
    :return:
    """
    neigbhouring_ids = _locate_neighbouring_chips(
        chip_x, chip_y, max_x, max_y)
    found_chips = list()
    for chip_coord in neigbhouring_ids:
        if ((invalid_chips is not None and chip_coord not in invalid_chips) or
                invalid_chips is None):
            found_chips.append(chip_coord)
    return found_chips


def _locate_neighbouring_chips(chip_x, chip_y, max_x, max_y):
    """ Find the chips which reside next to the input chip

    :param chip_x: the input chips x coordinate
    :param chip_y: the input chip y coordinate
    :return: an iterable of tuples containing x and y of neighbouring chips
    """

    # Get all the possible chip ids
    next_chips = list()
    next_chips.append({'x': chip_x + 1, 'y': chip_y})
    next_chips.append({'x': chip_x + 1, 'y': chip_y + 1})
    next_chips.append({'x': chip_x, 'y': chip_y + 1})
    next_chips.append({'x': chip_x - 1, 'y': chip_y + 1})
    next_chips.append({'x': chip_x - 1, 'y': chip_y})
    next_chips.append({'x': chip_x - 1, 'y': chip_y - 1})
    next_chips.append({'x': chip_x, 'y': chip_y - 1})

    # Remove those chips that can't exist
    chips_to_remove = list()
    for chip in next_chips:
        chip_id_x = chip['x']
        chip_id_y = chip['y']
        if (chip_id_x < 0 or chip_id_x > max_x or
                chip_id_y < 0 or chip_id_y > max_y):
            chips_to_remove.append((chip_id_x, chip_id_y))
    for (chip_id_x, chip_id_y) in chips_to_remove:
        next_chips.remove((chip_id_x, chip_id_y))
    return next_chips


def locate_spinnaker_links(version_no, machine):
    """ Gets SpiNNaker links that are on a given machine depending on the\
        version of the board.

    :param version_no: which version of board to use
    :param machine: the machine to detect the links of
    :return: A SpiNNakerLink object
    :raises: SpinnMachineInvalidParameterException when:
        1. in valid spinnaker link vlaue
        2. invalid version number
        3. uses wrap arounds
    """
    spinnaker_links = list()
    if version_no == 3 or version_no == 2:
        chip = machine.get_chip_at(0, 0)
        if not chip.router.is_link(3):
            spinnaker_links.append(SpinnakerLinkData(0, 0, 0, 3))
        chip = machine.get_chip_at(1, 0)
        if not chip.router.is_link(0):
            spinnaker_links.append(SpinnakerLinkData(1, 1, 0, 0))
    elif version_no == 4 or version_no == 5:
        chip = machine.get_chip_at(0, 0)
        if not chip.router.is_link(4):
            spinnaker_links.append(SpinnakerLinkData(0, 0, 0, 4))
    return spinnaker_links
