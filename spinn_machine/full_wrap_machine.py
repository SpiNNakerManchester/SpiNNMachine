from spinn_utilities.overrides import overrides
from .machine import Machine


class FullWrapMachine(Machine):
    """
    Provides an extension of Machine which supports full wrap arounds
    """

    def __init__(self, width, height, chips=None, origin=None):
        """
        Creates a fully wrapped machine

        :param width: The width of the machine excluding any vertical chips
        :param height: The height of the machine excluding any vertical chips
        :param chips: An iterable of chips in the machine
        :type chips: iterable of :py:class:`~spinn_machine.Chip`
        :param origin: Extra information about how this mnachine was created
        to be used in the str method. Example "Virtual" or "Json"
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: \
            If any two chips have the same x and y coordinates
        """
        super(FullWrapMachine, self).__init__(width, height, chips, origin)

    @overrides(Machine.x_y_by_ethernet)
    def x_y_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._board_chips:
            local_x = (x + ethernet_x) % self._width
            local_y = (y + ethernet_y) % self._height
            yield (local_x, local_y)

    @overrides(Machine.get_chips_by_ethernet)
    def get_chips_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._board_chips:
            local_xy = (
                           (x + ethernet_x) % self._width,
                           (y + ethernet_y) % self._height)
            if (local_xy) in self._chips:
                yield local_xy

    @overrides(Machine.x_y_over_link)
    def x_y_over_link(self, x, y, link):
        add_x, add_y = Machine.LINK_ADD_TABLE[link]
        link_x = (x + add_x + self._width) % self._width
        link_y = (y + add_y + self.height) % self.height
        return link_x, link_y

    @property
    @overrides(Machine.wrap)
    def wrap(self):
        return "Wrapped"
