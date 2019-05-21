from .machine import Machine
#from spinn_utilities.overrides import overrides


class FullWrapMachine(Machine):
    def __init__(self, width, height, chips, boot_x, boot_y):
        super(FullWrapMachine, self).__init__(width, height, chips, boot_x, boot_y)

    #@overrides(Machine.x_y_by_ethernet)
    #def x_y_by_ethernet(self, ethernet_x, ethernet_y):
    #    for (x, y) in Machine.BOARD_48_CHIPS:
    #        yield (x + ethernet_x, y + ethernet_y)
