from spinn_utilities.overrides import overrides
from .machine import Machine


class FullWrapMachine(Machine):
    # pylint: disable=useless-super-delegation

    def __init__(self, width, height, chips=None, origin=None):
        """ Creates a fully wrapped machine.

        :param width: The width of the machine excluding any virtual chips
        :param height: The height of the machine excluding any virtual chips
        :param chips: An iterable of chips in the machine
        :type chips: iterable of :py:class:`~spinn_machine.Chip`
        :param origin: Extra information about how this mnachine was created \
            to be used in the str method. Example "Virtual" or "Json"
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: \
            If any two chips have the same x and y coordinates
        """
        super(FullWrapMachine, self).__init__(width, height, chips, origin)

    @overrides(Machine.multiple_48_chip_boards)
    def multiple_48_chip_boards(self):
        return self._width % 12 == 0 and self._height % 12 == 0

    @overrides(Machine.get_xys_by_ethernet)
    def get_xys_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._local_xys:
            chip_x = (x + ethernet_x) % self._width
            chip_y = (y + ethernet_y) % self._height
            yield (chip_x, chip_y)

    @overrides(Machine.get_chips_by_ethernet)
    def get_chips_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._local_xys:
            chip_xy = (
                           (x + ethernet_x) % self._width,
                           (y + ethernet_y) % self._height)
            if (chip_xy) in self._chips:
                yield self._chips[chip_xy]

    @overrides(Machine.get_existing_xys_by_ethernet)
    def get_existing_xys_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._local_xys:
            chip_xy = (
                           (x + ethernet_x) % self._width,
                           (y + ethernet_y) % self._height)
            if (chip_xy) in self._chips:
                yield chip_xy

    @overrides(Machine.get_down_xys_by_ethernet)
    def get_down_xys_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._local_xys:
            chip_xy = (
                           (x + ethernet_x) % self._width,
                           (y + ethernet_y) % self._height)
            if (chip_xy) not in self._chips:
                yield chip_xy

    @overrides(Machine.xy_over_link)
    def xy_over_link(self, x, y, link):
        add_x, add_y = Machine.LINK_ADD_TABLE[link]
        link_x = (x + add_x + self._width) % self._width
        link_y = (y + add_y + self.height) % self.height
        return link_x, link_y

    @overrides(Machine.get_local_xy)
    def get_local_xy(self, chip):
        local_x = ((chip.x - chip.nearest_ethernet_x + self._width)
                   % self._width)
        local_y = ((chip.y - chip.nearest_ethernet_y + self._height)
                   % self._height)
        return local_x, local_y

    @overrides(Machine.get_global_xy)
    def get_global_xy(self, local_x, local_y, ethernet_x, ethernet_y):
        global_x = (local_x + ethernet_x) % self._width
        global_y = (local_y + ethernet_y) % self._height
        return global_x, global_y

    @overrides(Machine.shortest_path_length)
    def shortest_path_length(self, source, destination):
        # Aliases for convenience
        w, h = self._width, self._height

        # Get (non-wrapping) x, y vector from source to destination as if the
        # source was at (0, 0).
        x = (destination[0] - source[0]) % w
        y = (destination[1] - source[1]) % h

        # Calculate the shortest path length.
        #
        # In an ideal world, the following code would be used::
        #
        #     >>> return min(max(x, y),      # No wrap
        #     ...            w - x + y,      # Wrap X
        #     ...            x + h - y,      # Wrap Y
        #     ...            max(w-x, h-y))  # Wrap X and Y
        #

        # No wrap
        length = x if x > y else y

        # Wrap X
        wrap_x = w - x + y
        if wrap_x < length:
            length = wrap_x

        # Wrap Y
        wrap_y = x + h - y
        if wrap_y < length:
            length = wrap_y

        # Wrap X and Y
        dx = w - x
        dy = h - y
        wrap_xy = dx if dx > dy else dy
        if wrap_xy < length:
            return wrap_xy
        else:
            return length

    @property
    @overrides(Machine.wrap)
    def wrap(self):
        return "Wrapped"
