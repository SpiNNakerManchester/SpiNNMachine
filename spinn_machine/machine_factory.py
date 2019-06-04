from .no_wrap_machine import NoWrapMachine
from .horizontal_wrap_machine import HorizontalWrapMachine
from .vertical_wrap_machine import VerticalWrapMachine
from .full_wrap_machine import FullWrapMachine


def machine_from_size(width, height, chips=None, origin=None):
    """
    Create a machine with the assumed wrap-around based on the sizes.

    This could include a machine with no wrap-arounds, only vertical ones,
    only horizontal ones or both.

    Note: If the sizes do not match the ones for a known wrap around machine,
    no wrap-arounds is assumed.

    :param width: The width of the machine excluding any vertical chips
    :param height: The height of the machine excluding any vertical chips
    :param chips: Any chips to be add.
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
    Or at least a list which includes a chip with the highest x and
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
