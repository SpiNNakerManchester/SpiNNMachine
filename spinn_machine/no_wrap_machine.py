from .machine import Machine
from spinn_utilities.overrides import overrides


class NoWrapMachine(Machine):
    def __init__(self, width, height, chips, boot_x, boot_y):
        super(NoWrapMachine, self).__init__(width, height, chips, boot_x, boot_y)

    @overrides(Machine.x_y_by_ethernet)
    def x_y_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in Machine.BOARD_48_CHIPS:
            yield (x + ethernet_x, y + ethernet_y)

    @overrides(Machine.x_y_over_link)
    def x_y_over_link(self, x, y, link):
        add_x, add_y = Machine.LINK_ADD_TABLE[link]
        link_x = x + add_x
        link_y = y + add_y
        return link_x, link_y
