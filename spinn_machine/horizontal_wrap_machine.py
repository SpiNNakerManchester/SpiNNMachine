from spinn_utilities.overrides import overrides
from .machine import Machine


class HorizontalWrapMachine(Machine):
    # pylint: disable=useless-super-delegation
    def __init__(self, width, height, chips=None, origin=None):
        """ Creates a horizontally wrapped machine.

        :param width: The width of the machine excluding any virtual chips
        :param height: The height of the machine excluding any virtual chips
        :param chips: An iterable of chips in the machine
        :type chips: iterable of :py:class:`~spinn_machine.Chip`
        :param origin: Extra information about how this mnachine was created \
            to be used in the str method. Example "Virtual" or "Json"
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: \
            If any two chips have the same x and y coordinates
        """
        super(HorizontalWrapMachine, self).__init__(
            width, height, chips, origin)

    @overrides(Machine.multiple_48_chip_boards)
    def multiple_48_chip_boards(self):
        return self._width % 12 == 0 and (self._height - 4) % 12 == 0

    @overrides(Machine.get_xys_by_ethernet)
    def get_xys_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._local_xys:
            chip_x = (x + ethernet_x) % self._width
            chip_y = (y + ethernet_y)
            yield (chip_x, chip_y)

    @overrides(Machine.get_chips_by_ethernet)
    def get_chips_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._local_xys:
            chip_xy = (
                           (x + ethernet_x) % self._width,
                           (y + ethernet_y))
            if (chip_xy) in self._chips:
                yield self._chips[chip_xy]

    @overrides(Machine.get_existing_xys_by_ethernet)
    def get_existing_xys_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._local_xys:
            chip_xy = (
                           (x + ethernet_x) % self._width,
                           (y + ethernet_y))
            if (chip_xy) in self._chips:
                yield chip_xy

    @overrides(Machine.get_down_xys_by_ethernet)
    def get_down_xys_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._local_xys:
            chip_xy = (
                           (x + ethernet_x) % self._width,
                           (y + ethernet_y))
            if (chip_xy) not in self._chips:
                yield chip_xy

    @overrides(Machine.xy_over_link)
    def xy_over_link(self, x, y, link):
        add_x, add_y = Machine.LINK_ADD_TABLE[link]
        link_x = (x + add_x + self._width) % self._width
        link_y = y + add_y
        return link_x, link_y

    @overrides(Machine.get_local_xy)
    def get_local_xy(self, chip):
        local_x = (chip.x - chip.nearest_ethernet_x + self._width) \
                  % self._width
        local_y = chip.y - chip.nearest_ethernet_y
        return local_x, local_y

    @overrides(Machine.get_global_xy)
    def get_global_xy(self, local_x, local_y, ethernet_x, ethernet_y):
        global_x = (local_x + ethernet_x) % self._width
        global_y = local_y + ethernet_y
        return global_x, global_y

    @property
    @overrides(Machine.wrap)
    def wrap(self):
        return "HorWrap"
