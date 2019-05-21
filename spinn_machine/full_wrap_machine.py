from spinn_utilities.overrides import overrides
from .machine import Machine


class FullWrapMachine(Machine):
    def __init__(self, width, height, chips, boot_x, boot_y):
        super(FullWrapMachine, self).__init__(width, height, chips, boot_x, boot_y)

    @overrides(Machine.x_y_by_ethernet)
    def x_y_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in Machine.BOARD_48_CHIPS:
            local_x = (x + ethernet_x) % self._width
            local_y = (y + ethernet_y) % self._height
            yield (local_x, local_y)
