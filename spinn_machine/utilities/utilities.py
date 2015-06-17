"""
utilitiy functions for figuring bits of a machine without having a machine
object
"""

from spinn_machine import exceptions


def get_cloest_chips_to(chip_x, chip_y, max_x, max_y, invalid_chips):
    """
    gets the closest chip to a given chip coords
    :param chip_x: the chip coord in x axis for looking for cloest to
    :param chip_y: the chip coord in y axis for looking for cloest to
    :param max_y: the max y coord in the machine
    :param max_x: the max x coord in the machine
    :param invalid_chips: list of chips to remove
    :return:
    """
    neigbhouring_ids = _locate_neighbouring_chips(
        chip_x, chip_y, max_x, max_y)
    found_chips = list()
    for chip_coord in neigbhouring_ids:
        if ((invalid_chips is not None and
                chip_coord not in invalid_chips) or
                invalid_chips is None):
            found_chips.append(chip_coord)
    if len(found_chips) == 0:
        raise exceptions.SpinnMachineException(
            "no sensible middle chips were found in the middle of the machine,"
            "please rectiy your machine layout qand try again")
    return found_chips


def _does_this_chip_exist(chip_x, chip_y, max_x, max_y, invalid_chips):
    """
    checks if a chip exists in a expected machine format
    :param chip_x: the input chips x coordinate
    :param chip_y: the input chip y coordinate
    :param max_x: the max x dimension of the machine
    :param max_y: the max y dimension of the machine
    :param invalid_chips: what chips are none existent
    :return: boolean if chip does exist, false otehrwise
    """
    if (max_x > chip_x >= 0 and max_y > chip_y >= 0 and
            (invalid_chips is not None and
             ((chip_x, chip_y) not in invalid_chips))):
        return True
    else:
        return False


def _locate_neighbouring_chips(chip_x, chip_y, max_x, max_y):
    """
    locates the chips which reside next to the input chip
    :param chip_x: the input chips x coordinate
    :param chip_y: the input chip y coordinate
    :return: a iterable of tuples containing x and y of neighbouring chips
    """
    next_chips = list()
    removal_chips = list()
    next_chips.append({'x': chip_x + 1, 'y': chip_y})
    next_chips.append({'x': chip_x + 1, 'y': chip_y + 1})
    next_chips.append({'x': chip_x, 'y': chip_y + 1})
    next_chips.append({'x': chip_x - 1, 'y': chip_y + 1})
    next_chips.append({'x': chip_x - 1, 'y': chip_y})
    next_chips.append({'x': chip_x - 1, 'y': chip_y - 1})
    next_chips.append({'x': chip_x, 'y': chip_y - 1})

    for chip in next_chips:
        chip_id_x = chip['x']
        chip_id_y = chip['y']
        if (chip_id_x < 0 or chip_id_x > max_x or
                chip_id_y < 0 or chip_id_y > max_y):
            removal_chips.append((chip_id_x, chip_id_y))
    for (chip_id_x, chip_id_y) in removal_chips:
        next_chips.remove((chip_id_x, chip_id_y))
    return next_chips
