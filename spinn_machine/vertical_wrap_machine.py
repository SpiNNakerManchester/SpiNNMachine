from spinn_utilities.overrides import overrides
from .machine import Machine


class VerticalWrapMachine(Machine):
    def __init__(self, width, height, chips=None, origin=None):
        """
        Creates a vertically wrapped machine

        :param width: The width of the machine excluding any vertical chips
        :param height: The height of the machine excluding any vertical chips
        :param chips: An iterable of chips in the machine
        :type chips: iterable of :py:class:`~spinn_machine.Chip`
        :param origin: Extra information about how this mnachine was created
        to be used in the str method. Example "Virtual" or "Json"
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: \
            If any two chips have the same x and y coordinates
        """
        super(VerticalWrapMachine, self).__init__(width, height, chips, origin)

    @overrides(Machine.multiple_48_chip_boards)
    def multiple_48_chip_boards(self):
        return (self._width - 4) % 12 == 0 and self._height % 12 == 0

    @overrides(Machine.get_xys_by_ethernet)
    def get_xys_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._board_chips:
            local_x = (x + ethernet_x)
            local_y = (y + ethernet_y) % self._height
            yield (local_x, local_y)

    @overrides(Machine.get_chips_by_ethernet)
    def get_chips_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._board_chips:
            local_xy = (
                           (x + ethernet_x),
                           (y + ethernet_y) % self._height)
            if (local_xy) in self._chips:
                yield local_xy

    @overrides(Machine.xy_over_link)
    def xy_over_link(self, x, y, link):
        add_x, add_y = Machine.LINK_ADD_TABLE[link]
        link_x = x + add_x
        link_y = (y + add_y + self.height) % self.height
        return link_x, link_y

    @overrides(Machine.get_local_xy)
    def get_local_xy(self, chip):
        local_x = chip.x - chip.nearest_ethernet_x
        local_y = ((chip.y - chip.nearest_ethernet_y + self._height)
                   % self._height)
        return local_x, local_y

    @property
    @overrides(Machine.wrap)
    def wrap(self):
        return "VerWrap"
