from spinn_machine.no_wrap_machine import NoWrapMachine
from spinn_machine.horizontal_wrap_machine import HorizontalWrapMachine
from spinn_machine.vertical_wrap_machine import VerticalWrapMachine
from spinn_machine.full_wrap_machine import FullWrapMachine


def machine_from_size(width, height, chips=None, boot_x=0, boot_y=0):
    if chips is None:
        chips = []
    if width == 2 and height == 2:
        return FullWrapMachine(width, height, chips, boot_x, boot_y)
    if width % 12 == 0:
        if height % 12 == 0:
            return FullWrapMachine(width, height, chips, boot_x, boot_y)
        else:
            return HorizontalWrapMachine(width, height, chips, boot_x, boot_y)
    else:
        if height % 12 == 0:
            return VerticalWrapMachine(width, height, chips, boot_x, boot_y)
        else:
            return NoWrapMachine(width, height, chips, boot_x, boot_y)


def machine_from_chips(chips, boot_x=0, boot_y=0):
    max_x = 0
    max_y = 0
    for chip in chips:
        if chip.x > max_x:
            max_x = chip.x
        if chip.y > max_y:
            max_y = chip.y
    return machine_from_size(max_x + 1, max_y + 1, chips, boot_x, boot_y)