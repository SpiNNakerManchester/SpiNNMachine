from spinn_utilities.overrides import overrides
from .machine import Machine


class VerticalWrapMachine(Machine):
    def __init__(self, width, height, chips):
        super(VerticalWrapMachine, self).__init__(width, height, chips)

    @overrides(Machine.x_y_by_ethernet)
    def x_y_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in Machine.BOARD_48_CHIPS:
            local_x = (x + ethernet_x)
            local_y = (y + ethernet_y) % self._height
            yield (local_x, local_y)

    @overrides(Machine.x_y_over_link)
    def x_y_over_link(self, x, y, link):
        add_x, add_y = Machine.LINK_ADD_TABLE[link]
        link_x = x + add_x
        link_y = (y + add_y + self.height) % self.height
        return link_x, link_y
