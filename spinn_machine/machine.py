# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division
from collections import OrderedDict
from six import iteritems, iterkeys, itervalues, add_metaclass
from .exceptions import (SpinnMachineAlreadyExistsException,
                         SpinnMachineException)
from spinn_machine.link_data_objects import FPGALinkData, SpinnakerLinkData
from spinn_utilities.abstract_base import (
    AbstractBase, abstractproperty, abstractmethod)


@add_metaclass(AbstractBase)
class Machine(object):
    """ A representation of a SpiNNaker Machine with a number of Chips.\
        Machine is also iterable, providing ((x, y), chip) where:

            * x is the x-coordinate of a chip
            * y is the y-coordinate of a chip
            * chip is the chip with the given x, y coordinates
    """

    # current opinions is that the Ethernet connected chip can handle 10
    # UDP packets per millisecond
    MAX_BANDWIDTH_PER_ETHERNET_CONNECTED_CHIP = 10 * 256
    DEFAULT_MAX_CORES_PER_CHIP = 18
    __max_cores = None
    MAX_CHIPS_PER_48_BOARD = 48
    MAX_CHIPS_PER_4_CHIP_BOARD = 4
    BOARD_VERSION_FOR_48_CHIPS = [4, 5]
    BOARD_VERSION_FOR_4_CHIPS = [2, 3]

    # other useful magic numbers for machines
    MAX_CHIP_X_ID_ON_ONE_BOARD = 7
    MAX_CHIP_Y_ID_ON_ONE_BOARD = 7
    SIZE_X_OF_ONE_BOARD = 8
    SIZE_Y_OF_ONE_BOARD = 8

    # Table of the amount to add to the x and y coordinates to get the
    #  coordinates down the given link (0-5)
    LINK_ADD_TABLE = [(1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1)]

    CHIPS_PER_BOARD = {
        (0, 0): 18, (0, 1): 18, (0, 2): 18, (0, 3): 18, (1, 0): 18, (1, 1): 17,
        (1, 2): 18, (1, 3): 17, (1, 4): 18, (2, 0): 18, (2, 1): 18, (2, 2): 18,
        (2, 3): 18, (2, 4): 18, (2, 5): 18, (3, 0): 18, (3, 1): 17, (3, 2): 18,
        (3, 3): 17, (3, 4): 18, (3, 5): 17, (3, 6): 18, (4, 0): 18, (4, 1): 18,
        (4, 2): 18, (4, 3): 18, (4, 4): 18, (4, 5): 18, (4, 6): 18, (4, 7): 18,
        (5, 1): 18, (5, 2): 17, (5, 3): 18, (5, 4): 17, (5, 5): 18, (5, 6): 17,
        (5, 7): 18, (6, 2): 18, (6, 3): 18, (6, 4): 18, (6, 5): 18, (6, 6): 18,
        (6, 7): 18, (7, 3): 18, (7, 4): 18, (7, 5): 18, (7, 6): 18, (7, 7): 18
    }
    BOARD_48_CHIPS = list(CHIPS_PER_BOARD.keys())

    __slots__ = (
        "_boot_ethernet_address",
        "_chips",
        "_ethernet_connected_chips",
        "_fpga_links",
        # Declared height of the machine excluding virtual chips
        # This can not be changed
        "_height",
        # List of the possible chips (x,y) on each board of the machine
        "_local_xys",
        # Max x value of any chip including virtual chips
        # This could change as new chips are added
        "_max_chip_x",
        # Max y value of any chip including virtual chips
        # This could change as new chips are added
        "_max_chip_y",
        # Extra information about how this machine was created
        # to be used in the str method
        "_origin",
        "_spinnaker_links",
        "_maximum_user_cores_on_chip",
        "_virtual_chips",
        # Declared width of the machine excluding virtual chips
        # This can not be changed
        "_width"
    )

    @staticmethod
    def max_cores_per_chip():
        """
        Gets the max core per chip for the while system.

        There is no guarantee that there will be any Chips with this many\
        cores, only that there will be no cores with more.

        :return: the default cores per chip unless overridden by set
        """
        if Machine.__max_cores is None:
            Machine.__max_cores = Machine.DEFAULT_MAX_CORES_PER_CHIP
        return Machine.__max_cores

    @staticmethod
    def set_max_cores_per_chip(new_max):
        """
        Allows setting the max number of cores per chip for the whole system.

        Allows virtual machines to go higher than normal.

        Real machines can only be capped never increased beyond what they
        actually have.

        :param new_max: New value to use for the max
        :raises: SpinnMachineException if max_cores_per_chip has already been\
            used and is now being changed.\
            The Exception also happens if the value is set twice to difference\
            values. For example in the script and in the config.
        """
        if Machine.__max_cores is None:
            Machine.__max_cores = new_max
        elif Machine.__max_cores != new_max:
            raise SpinnMachineException(
                "max_cores_per_chip has already been accessed "
                "so can not be changed.")

    def __init__(self, width, height, chips=None, origin=None):
        """
        Creates an abstract machine that must be superclassed by wrap type.

        Use machine_fatcory methods to determine the correct machine class

        :param width: The width of the machine excluding any virtual chips
        :type width: int
        :param height: The height of the machine excluding any virtual chips
        :type height: int
        :param chips: An iterable of chips in the machine
        :type chips: iterable(Chip)
        :param origin: Extra information about how this machine was created \
            to be used in the str method. Example "Virtual" or "Json"
        :type origin: str
        :raise SpinnMachineAlreadyExistsException: \
            If any two chips have the same x and y coordinates
        """
        self._width = width
        self._height = height

        if (self._width == self._height == 8) or \
                self.multiple_48_chip_boards():
            self._local_xys = self.BOARD_48_CHIPS
        else:
            self._local_xys = []
            for x in range(width):
                for y in range(height):
                    self._local_xys.append((x, y))

        # The current maximum chip x coordinate
        self._max_chip_x = 0

        # The current maximum chip y coordinate
        self._max_chip_y = 0

        # The maximum number of user cores on any chip
        self._maximum_user_cores_on_chip = 0

        # The list of chips with Ethernet connections
        self._ethernet_connected_chips = list()

        # The dictionary of SpiNNaker links by board address and "ID" (int)
        self._spinnaker_links = dict()

        # The dictionary of FPGA links by board address, FPGA and link ID
        self._fpga_links = dict()

        # Store the boot chip information
        self._boot_ethernet_address = None

        # The dictionary of chips
        self._chips = OrderedDict()
        if chips is not None:
            self.add_chips(chips)

        self._virtual_chips = list()

        if origin is None:
            self._origin = ""
        else:
            self._origin = origin

    @abstractmethod
    def multiple_48_chip_boards(self):
        """
        Checks that the width and height correspond to the expected size for a
        multi-board machine made up of more than one 48 chip board.

        The assumption is that any size machine can be supported but that
        only ones with an expected 48 chip board size can have more than one
        ethernet chip.

        :return: True if this machine can have multiple 48 chip boards
        :rtype: bool
        """

    @abstractmethod
    def get_xys_by_ethernet(self, ethernet_x, ethernet_y):
        """
        Yields the potential x,y locations of all the chips on the board
        with this ethernet. Including the Ethernet chip itself.

        Wrap-arounds are handled as appropriate.

        Note: This method does not check if the chip actually exists as is
        intended to be called to create the chips.

        Warning: GIGO! This methods assumes that ethernet_x and ethernet_y are
        the local 0,0 of an existing board, within the width and height of the
        machine.

        :param ethernet_x: \
            The x coordinate of a (local 0,0) legal ethernet chip
        :param ethernet_y: \
            The y coordinate of a (local 0,0) legal ethernet chip
        :return: Yields the (x, y) coordinates of all the potential chips on \
            this board.
        :rtype: iterable(tuple(int,int))
        """

    @abstractmethod
    def get_xy_cores_by_ethernet(self, ethernet_x, ethernet_y):
        """
        Yields the potential x,y locations and the typical number of cores
        of all the chips on the board with this ethernet.

        Includes the Ethernet chip itself.

        Wrap-arounds are handled as appropriate.

        Note: This method does not check if the chip actually exists,
        nor report the actual number of cores on this chip, as is
        intended to be called to create the chips.

        The number of cores is based on the 1,000,000 core machine where the
        board where built with the the 17 core chips placed in the same
        location on nearly every board.

        Warning: GIGO! This methods assumes that ethernet_x and ethernet_y are
        the local 0,0 of an existing board, within the width and height of the
        machine.

        :param ethernet_x: \
            The x coordinate of a (local 0,0) legal ethernet chip
        :param ethernet_y: \
            The y coordinate of a (local 0,0) legal ethernet chip
        :return: Yields (x, y, n_cores) where x , y are coordinates of all \
            the potential chips on this board, and n_cores is the typcial \
            number of cores for a chip in that possition.
        :rtype: iterable(tuple(int,int))
        """

    @abstractmethod
    def get_down_xys_by_ethernet(self, ethernet_x, ethernet_y):
        """
        Yields the (x,y) coordinates of the down chips on the board with this
        ethernet.

        Note the Ethernet chip itself can not be missing if validated

        Wrap-arounds are handled as appropriate.

        This method does check if the chip actually exists.

        :param ethernet_x: \
            The x coordinate of a (local 0,0) legal ethernet chip
        :param ethernet_y: \
            The y coordinate of a (local 0,0) legal ethernet chip
        :return: Yields the (x, y) of the down chips on this board.
        :rtype: iterable(tuple(int,int))
        """

    @abstractmethod
    def get_chips_by_ethernet(self, ethernet_x, ethernet_y):
        """
        Yields the actual chips on the board with this ethernet.
        Including the Ethernet chip itself.

        Wrap-arounds are handled as appropriate.

        This method does check if the chip actually exists.

        :param ethernet_x: \
            The x coordinate of a (local 0,0) legal ethernet chip
        :param ethernet_y: \
            The y coordinate of a (local 0,0) legal ethernet chip
        :return: Yields the chips on this board.
        :rtype: iterable(Chip)
        """

    @abstractmethod
    def get_existing_xys_by_ethernet(self, ethernet_x, ethernet_y):
        """
        Yields the (x,y)s of actual chips on the board with this ethernet.
        Including the Ethernet chip itself.

        Wrap-arounds are handled as appropriate.

        This method does check if the chip actually exists.

        :param ethernet_x: \
            The x coordinate of a (local 0,0) legal ethernet chip
        :param ethernet_y: \
            The y coordinate of a (local 0,0) legal ethernet chip
        :return: Yields the (x,y)s of chips on this board.
        :rtype: iterable(tuple(int,int))
        """

    @abstractmethod
    def xy_over_link(self, x, y, link):
        """
        Get the potential x,y location of the chip reached over this link.

        Wrap-arounds are handled as appropriate.

        Note: This method does not check if either chip source or destination
        actually exists as is intended to be called to create the links.

        It is the callers responsibility to check the validity of this call
        before making it or the validity of the result.

        Warning: GIGO! This methods assumes that x and y are within the
        width and height of the machine, and that the link goes to another
        chip on the machine.

        On machine without full wrap-around it is possible that this method
        generates x,y values that fall outside of the legal values including
        negative values, x = width or y = height.

        :param x: The x coordinate of a chip that will exist on the machine
        :param y: The y coordinate of a chip that will exist on the machine
        :param link: The link to another chip that could exist on the machine
        :return: x and y coordinates of the chip over that link if it is \
            valid or some fictional x,y if not.
        :rtype: tuple(int,int)
        """

    @abstractmethod
    def get_local_xy(self, chip):
        """
        Converts the x and y coordinates into the local coordinates on the
        board as if the ethernet was at position 0,0

        This method does take wrap-arounds into consideration.

        This method assumes that chip is on the machine or is a copy of a
        chip on the machine

        :param chip: A Chip in the machine
        :return: Local (x, y) coordinates.
        :rtype: tuple(int,int)
        """

    @abstractmethod
    def get_global_xy(self, local_x, local_y, ethernet_x, ethernet_y):
        """
        Converts the local x and y coordinates into global x,y coordinates,
        under the assumption that they are on the board with local 0,0 at
        ethernet_x, ethernet_y

        This method does take wrap-arounds into consideration.

        GIGO: This method does not check if input parameters make sense,
        nor does it check if there is a chip at the resulting global x,y

        :param local_x: A valid local x coordinate for a chip
        :param local_y: A valid local y coordinate for a chip
        :param ethernet_x: The global ethernet x for the board the chip is on
        :param ethernet_y: The global ethernet y for the board the chip is on
        :return: global (x,y) coordinates of the chip
        :rtype: tuple(int,int)
        """

    @abstractmethod
    def get_vector_length(self, source, destination):
        """
        Get the mathematical length of the shortest vector (x, y, z) from
        source to destination

        Use the same algorithm as vector to find the best x, y pair but then
        is optimised to directly calculate length

        This method does not check if the chips and links it assumes to take
        actually exist.
        For example long paths along a none wrapping edge may well travel
        through the missing area.

        This method does take wrap-arounds into consideration as applicable.

        From https://github.com/project-rig/rig/blob/master/rig/geometry.py
        Described in http://jhnet.co.uk/articles/torus_paths

        On full wrap-around machines (before minimisation) the vectors can have
        any of the 4 combinations of positive and negative x and y
        The positive one is: `destination - source % dimension`
        The negative one is: `positive - dimension`
        If source is less than dimension the negative one is the wrap around
        If destination is greater than source the positive one wraps

        One no wrap or part wrap boards the x/y that does not wrap is just
        destination - source

        The length of vectors where both x and y have the same sign will be
        `max(abs(x), abs(y))`.  As the z direction can be used in minimisation
        The length of vectors where x and y have opposite signs will be
        `abs(x)` and `abs(y)` as these are already minimum so z is not used.

        GIGO: This method does not check if input parameters make sense,

        :param source: (x,y) coordinates of the source chip
        :type source: (int, int)
        :param destination:  (x,y) coordinates of the destination chip
        :type destination: (int, int)
        :return: The distance in steps
        :rtype: int
        """

    @abstractmethod
    def get_vector(self, source, destination):
        """
        Get mathematical shortest vector (x, y, z) from source to destination

        This method does not check if the chips and links it assumes to take
        actually exist.
        For example long paths along a none wrapping edge may well travel
        through the missing area.

        This method does take wrap-arounds into consideration as applicable.

        From https://github.com/project-rig/rig/blob/master/rig/geometry.py
        Described in http://jhnet.co.uk/articles/torus_paths

        Use the same algorithm as vector_length
        using the best x, y pair as minimize(x, y, 0)

        :param source: (x,y) coordinates of the source chip
        :type source: (int, int)
        :param destination:  (x,y) coordinates of the destination chip
        :return:
        """

    def validate(self):
        """
        Validates the machine and raises an exception in unexpected conditions.

        Assumes that at the time this is called all chips are on the board.

        This allows the checks to be avoided when creating a virtual machine
        (Except of course in testing)

        An Error is raised if there is a chip with a x outside of the
        range 0 to width -1 (except for virtual ones)
        An Error is raised if there is a chip with a y outside of the
        range 0 to height -1 (except for virtual ones)
        An Error is raise if there is no chip at the declared ethernet x and y
        An Error is raised if an ethernet chip is not at a local 0,0
        An Error is raised if there is no ethernet chip is at 0,0
        An Error is raised if this is a unexpected multiple board situation
        :rtype: None
        """
        if self._boot_ethernet_address is None:
            raise SpinnMachineException(
                "no ethernet chip at 0, 0 found")
        if len(self._ethernet_connected_chips) > 1:
            if not self.multiple_48_chip_boards():
                raise SpinnMachineException(
                    "A {} machine of size {}, {} can not handle multiple "
                    "ethernet chips".format(
                        self.wrap, self._width, self._height))
        # The fact that self._boot_ethernet_address is set means there is an
        # ethernet chip and it is at 0,0 so no need to check that

        for chip in self.chips:
            if chip.x < 0:
                raise SpinnMachineException(
                    "{} has a negative x".format(chip))
            if chip.y < 0:
                raise SpinnMachineException(
                    "{} has a negative y".format(chip))
            if not chip.virtual:
                if chip.x >= self._width:
                    raise SpinnMachineException(
                        "{} has an x large than width {}".format(
                            chip, self._width))
                if chip.y >= self._height:
                    raise SpinnMachineException(
                        "{} has an y large than heigth {}".format(
                            chip, self._width))
            if chip.ip_address:
                # Ethernet Chip checks
                if chip.x % 4 != 0:
                    raise SpinnMachineException(
                        "Ethernet {} has a x which is not divisible by 4"
                        "".format(chip))
                if (chip.x + chip.y) % 12 != 0:
                    raise SpinnMachineException(
                        "Ethernet {} has a x y pair that do not add up to 12"
                        "".format(chip))
            elif not chip.virtual:
                # None Ethernet chip checks
                if not self.is_chip_at(
                        chip.nearest_ethernet_x, chip.nearest_ethernet_y):
                    raise SpinnMachineException(
                        "{} has an invalid ethernet chip".format(chip))
                local_xy = self.get_local_xy(chip)
                if local_xy not in self._local_xys:
                    raise SpinnMachineException(
                        "{} has an unexpected local xy of {}".format(
                            chip, local_xy))

    @abstractproperty
    def wrap(self):
        """ String to represent the type of wrap.

        :return: Short string for type of wrap
        """

    def add_chip(self, chip):
        """ Add a chip to the machine

        :param chip: The chip to add to the machine
        :type chip: :py:class:`~spinn_machine.Chip`
        :return: Nothing is returned
        :rtype: None
        :raise SpinnMachineAlreadyExistsException: \
            If a chip with the same x and y coordinates already exists
        """
        chip_id = (chip.x, chip.y)
        if chip_id in self._chips:
            raise SpinnMachineAlreadyExistsException(
                "chip", "{}, {}".format(chip.x, chip.y))

        self._chips[chip_id] = chip

        if chip.x > self._max_chip_x:
            self._max_chip_x = chip.x
        if chip.y > self._max_chip_y:
            self._max_chip_y = chip.y

        if chip.ip_address is not None:
            self._ethernet_connected_chips.append(chip)
            if (chip.x == 0) and (chip.y == 0):
                self._boot_ethernet_address = chip.ip_address

        if chip.n_user_processors > self._maximum_user_cores_on_chip:
            self._maximum_user_cores_on_chip = chip.n_user_processors

    def add_virtual_chip(self, chip):
        """
        :rtype: None
        """
        self._virtual_chips.append(chip)
        self.add_chip(chip)

    def add_chips(self, chips):
        """ Add some chips to the machine

        :param chips: an iterable of chips
        :type chips: iterable(:py:class:`~spinn_machine.Chip`)
        :return: Nothing is returned
        :rtype: None
        :raise SpinnMachineAlreadyExistsException: \
            If a chip with the same x and y coordinates as one being added \
            already exists
        """
        for next_chip in chips:
            self.add_chip(next_chip)

    @property
    def chips(self):
        """ An iterable of chips in the machine

        :return: An iterable of chips
        :rtype: iterable(:py:class:`~spinn_machine.Chip`)
        :raise None: does not raise any known exceptions
        """
        return itervalues(self._chips)

    @property
    def chip_coordinates(self):
        """ An iterable of chip coordinates in the machine

        :return: An iterable of chip coordinates
        :rtype: iterable(int,int)
        """
        return iterkeys(self._chips)

    def __iter__(self):
        """ Get an iterable of the chip coordinates and chips

        :return: An iterable of tuples of ((x, y), chip) where:
            * (x, y) is a tuple where:
                * x is the x-coordinate of a chip
                * y is the y-coordinate of a chip
            * chip is a chip
        :rtype: iterable((int, int), :py:class:`~spinn_machine.Chip`)
        :raise None: does not raise any known exceptions
        """
        return iteritems(self._chips)

    def __len__(self):
        """ Get the total number of chips.

        :return: The number of items in the underlying iterable
        :rtype: int
        """
        return len(self._chips)

    def get_chip_at(self, x, y):
        """ Get the chip at a specific (x, y) location.\
            Also implemented as __getitem__((x, y))

        :param x: the x-coordinate of the requested chip
        :type x: int
        :param y: the y-coordinate of the requested chip
        :type y: int
        :return: the chip at the specified location, or None if no such chip
        :rtype: :py:class:`~spinn_machine.Chip`
        :raise None: does not raise any known exceptions
        """
        chip_id = (x, y)
        if chip_id in self._chips:
            return self._chips[chip_id]
        return None

    def __getitem__(self, x_y_tuple):
        """ Get the chip at a specific (x, y) location

        :param x_y_tuple: A tuple of (x, y) where:
            * x is the x-coordinate of the chip to retrieve
            * y is the y-coordinate of the chip to retrieve
        :type x_y_tuple: (int, int)
        :return: the chip at the specified location, or None if no such chip
        :rtype: :py:class:`~spinn_machine.Chip`
        :raise None: does not raise any known exceptions
        """
        x, y = x_y_tuple
        return self.get_chip_at(x, y)

    def is_chip_at(self, x, y):
        """ Determine if a chip exists at the given coordinates.\
            Also implemented as __contains__((x, y))

        :param x: x location of the chip to test for existence
        :type x: int
        :param y: y location of the chip to test for existence
        :type y: int
        :return: True if the chip exists, False otherwise
        :rtype: bool
        :raise None: does not raise any known exceptions
        """
        return (x, y) in self._chips

    def is_link_at(self, x, y, link):
        """ Determine if a link exists at the given coordinates

        :param x: The x location of the chip to test the link of
        :type x: int
        :param y: The y location of the chip to test the link of
        :type y: int
        :param link: The link to test the existence of
        :type link: int
        """
        return (x, y) in self._chips and self._chips[x, y].router.is_link(link)

    def __contains__(self, x_y_tuple):
        """ Determine if a chip exists at the given coordinates

        :param x_y_tuple: A tuple of (x, y) where:
            * x is the x-coordinate of the chip to retrieve
            * y is the y-coordinate of the chip to retrieve
        :type x_y_tuple: tuple(int, int)
        :return: True if the chip exists, False otherwise
        :rtype: bool
        :raise None: does not raise any known exceptions
        """
        x, y = x_y_tuple
        return self.is_chip_at(x, y)

    @property
    def max_chip_x(self):
        """ The maximum x-coordinate of any chip in the board

        :return: The maximum x-coordinate
        :rtype: int
        """
        return self._max_chip_x

    @property
    def max_chip_y(self):
        """ The maximum y-coordinate of any chip in the board

        :return: The maximum y-coordinate
        :rtype: int
        """
        return self._max_chip_y

    @property
    def width(self):
        """ The width to the machine ignoring virtual chips

        :return: The width to the machine ignoring virtual chips
        :rtype: int
        """
        return self._width

    @property
    def height(self):
        """ The height to the machine ignoring virtual chips

        :return: The height to the machine ignoring virtual chips
        :rtype: int
        """
        return self._height

    @property
    def n_chips(self):
        """ The number of chips in the machine.

        :rtype: int
        """
        return len(self._chips)

    @property
    def ethernet_connected_chips(self):
        """ The chips in the machine that have an Ethernet connection

        :rtype: iterable(Chip)
        """
        return self._ethernet_connected_chips

    @property
    def spinnaker_links(self):
        """ The set of SpiNNaker links in the machine

        :rtype: iterable(~spinn_machine.link_data_objects.SpinnakerLinkData)
        """
        return iteritems(self._spinnaker_links)

    def get_spinnaker_link_with_id(
            self, spinnaker_link_id, board_address=None):
        """ Get a SpiNNaker link with a given ID

        :param spinnaker_link_id: The ID of the link
        :type spinnaker_link_id: int
        :param board_address:\
            the board address that this SpiNNaker link is associated with
        :type board_address: str or None
        :return: The SpiNNaker link data or None if no link
        :rtype:\
            :py:class:`~spinn_machine.link_data_objects.SpinnakerLinkData`
        """
        if board_address is None:
            board_address = self._boot_ethernet_address
        return self._spinnaker_links.get(
            (board_address, spinnaker_link_id), None)

    def get_fpga_link_with_id(self, fpga_id, fpga_link_id, board_address=None):
        """ Get an FPGA link data item that corresponds to the FPGA and FPGA\
            link for a given board address.

        :param fpga_id:\
            the ID of the FPGA that the data is going through.  Refer to \
            technical document located here for more detail:
            https://drive.google.com/file/d/0B9312BuJXntlVWowQlJ3RE8wWVE
        :type fpga_link_id: int
        :param fpga_link_id:\
            the link ID of the FPGA. Refer to technical document located here\
            for more detail:
            https://drive.google.com/file/d/0B9312BuJXntlVWowQlJ3RE8wWVE
        :type fpga_id: int
        :param board_address:\
            the board address that this FPGA link is associated with
        :type board_address: str
        :rtype:\
            :py:class:`~spinn_machine.link_data_objects.FPGALinkData`
        :return: the given FPGA link object or None if no such link
        """
        if board_address is None:
            board_address = self._boot_ethernet_address
        return self._fpga_links.get(
            (board_address, fpga_id, fpga_link_id), None)

    def add_spinnaker_links(self):
        """ Add SpiNNaker links that are on a given machine depending on the\
            version of the board.
        """
        if self._width == self._height == 2:
            chip_0_0 = self.get_chip_at(0, 0)
            if not chip_0_0.router.is_link(3):
                self._spinnaker_links[chip_0_0.ip_address, 0] = \
                    SpinnakerLinkData(0, 0, 0, 3, chip_0_0.ip_address)
            chip = self.get_chip_at(1, 0)
            if not chip.router.is_link(0):
                self._spinnaker_links[chip_0_0.ip_address, 1] = \
                    SpinnakerLinkData(1, 1, 0, 0, chip_0_0.ip_address)
        elif (self._width == self._height == 8) or \
                self.multiple_48_chip_boards():
            for chip in self._ethernet_connected_chips:
                if not chip.router.is_link(4):
                    self._spinnaker_links[
                        chip.ip_address, 0] = SpinnakerLinkData(
                            0, chip.x, chip.y, 4, chip.ip_address)

    def add_fpga_links(self):
        """ Add FPGA links that are on a given machine depending on the\
            version of the board.
        """
        if self._width == self._height == 8 or self.multiple_48_chip_boards():

            for ethernet_connected_chip in self._ethernet_connected_chips:

                # the sides of the hexagonal shape of the board are as follows
                #
                #
                #                 Top
                #                 ####
                #                #####
                #  Top Left     ###### Right
                #              #######
                #             ########
                #             #######
                #    Left     ###### Bottom Right
                #             #####
                #             Bottom
                #

                # handle the first chip
                ex = ethernet_connected_chip.x
                ey = ethernet_connected_chip.y
                ip = ethernet_connected_chip.ip_address

                # List of x, y, l1, l2, dx, dy where:
                #     x = start x
                #     y = start y
                #     l1 = first link
                #     l2 = second link
                #     dx = change in x to next
                #     dy = change in y to next
                chip_links = [(7, 3, 0, 5, -1, -1),  # Bottom Right
                              (4, 0, 4, 5, -1, 0),   # Bottom
                              (0, 0, 4, 3, 0, 1),    # Left
                              (0, 3, 2, 3, 1, 1),    # Top Left
                              (4, 7, 2, 1, 1, 0),    # Top
                              (7, 7, 0, 1, 0, -1)]   # Right

                f = 0
                lk = 0
                for i, (x, y, l1, l2, dx, dy) in enumerate(chip_links):
                    for _ in range(4):
                        fx = (x + ex) % (self._max_chip_x + 1)
                        fy = (y + ey) % (self._max_chip_y + 1)
                        self._add_fpga_link(f, lk, fx, fy, l1, ip)
                        f, lk = self._next_fpga_link(f, lk)
                        if i % 2 == 1:
                            x += dx
                            y += dy
                        fx = (x + ex) % (self._max_chip_x + 1)
                        fy = (y + ey) % (self._max_chip_y + 1)
                        self._add_fpga_link(f, lk, fx, fy, l2, ip)
                        f, lk = self._next_fpga_link(f, lk)
                        if i % 2 == 0:
                            x += dx
                            y += dy

    # pylint: disable=too-many-arguments
    def _add_fpga_link(self, fpga_id, fpga_link, x, y, link, board_address):
        if self.is_chip_at(x, y) and not self.is_link_at(x, y, link):
            self._fpga_links[board_address, fpga_id, fpga_link] = \
                FPGALinkData(
                    fpga_link_id=fpga_link, fpga_id=fpga_id,
                    connected_chip_x=x, connected_chip_y=y,
                    connected_link=link, board_address=board_address)

    @staticmethod
    def _next_fpga_link(fpga_id, fpga_link):
        if fpga_link == 15:
            return fpga_id + 1, 0
        return fpga_id, fpga_link + 1

    def __str__(self):
        return "[{}{}Machine: max_x={}, max_y={}, n_chips={}]".format(
            self._origin, self.wrap, self._max_chip_x, self._max_chip_y,
            self.n_chips)

    def __repr__(self):
        return self.__str__()

    def get_cores_and_link_count(self):
        """ Get the number of cores and links from the machine

        Links are assumed to be bidirectional so the total links counted is
        half of the unidirectional links found.

        Spinnaker and fpga links are not included.

        :return: tuple of (n_cores, n_links)
        :rtype: tuple(int,int)
        """
        cores = 0
        total_links = 0
        for chip_key in self._chips:
            chip = self._chips[chip_key]
            cores += chip.n_processors
            total_links += len(chip.router)
        return cores, total_links / 2

    def cores_and_link_output_string(self):
        """ Get a string detailing the number of cores and links

        :rtype: str
        """
        cores, links = self.get_cores_and_link_count()
        return "{} cores and {} links".format(cores, links)

    @property
    def boot_chip(self):
        """ The chip used to boot the machine

        :rtype: Chip
        """
        return self._chips[0, 0]

    def get_existing_xys_on_board(self, chip):
        """ Get the chips that are on the same board as the given chip

        :param chip: The chip to find other chips on the same board as
        :return: An iterable of (x, y) coordinates of chips on the same board
        :rtype: iterable(tuple(int,int))
        """
        return self.get_existing_xys_by_ethernet(
            chip.nearest_ethernet_x, chip.nearest_ethernet_y)

    @property
    def maximum_user_cores_on_chip(self):
        """ The maximum number of user cores on any chip
        """
        return self._maximum_user_cores_on_chip

    @property
    def total_available_user_cores(self):
        """ The total number of cores on the machine which are not \
            monitor cores

        :return: total
        :rtype: int
        """
        # pylint: disable=protected-access
        return sum(chip._n_user_processors for chip in self.chips)

    @property
    def total_cores(self):
        """ The total number of cores on the machine, including monitors

        :return: total
        :rtype: int
        """
        return sum(
            1 for chip in self.chips for _processor in chip.processors)

    def unreachable_outgoing_chips(self):
        """
        Detects chips that can not reach any of their neighbours

        Current implementation does NOT deal with group of unreachable chips

        :return: List (hopefully empty) if the (x,y) cooridinates of
            unreachable chips.
        """
        removable_coords = list()
        for (x, y) in self.chip_coordinates:
            # If no links out of the chip work, remove it
            is_link = False
            for link in range(6):
                if self.is_link_at(x, y, link):
                    is_link = True
                    break
            if not is_link:
                removable_coords.append((x, y))
        return removable_coords

    def unreachable_incoming_chips(self):
        """
        Detects chips that are not reachable from any of their neighbours

        Current implementation does NOT deal with group of unreachable chips

        :return: List (hopefully empty) if the (x,y) cooridinates of
            unreachable chips.
        """
        removable_coords = list()
        for (x, y) in self.chip_coordinates:
            # Go through all the chips that surround this one
            moves = [(1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1)]
            is_link = False
            for link, (x_move, y_move) in enumerate(moves):
                opposite = (link + 3) % 6
                next_x = x + x_move
                next_y = y + y_move
                if self.is_link_at(next_x, next_y, opposite):
                    is_link = True
                    break
            if not is_link:
                removable_coords.append((x, y))
        return removable_coords

    def unreachable_outgoing_local_chips(self):
        """
        Detects chips that can not reach any of their LOCAL neighbours

        Current implementation does NOT deal with group of unreachable chips

        :return: List (hopefully empty) if the (x,y) cooridinates of
            unreachable chips.
        """
        removable_coords = list()
        for chip in self._chips.values():
            # If no links out of the chip work, remove it
            is_link = False
            moves = [(1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1)]
            x = chip.x
            y = chip.y
            nearest_ethernet_x = chip.nearest_ethernet_x
            nearest_ethernet_y = chip.nearest_ethernet_y
            for link, (x_move, y_move) in enumerate(moves):
                if chip.router.is_link(link):
                    n_x_y = (x + x_move, y + y_move)
                    if n_x_y in self._chips:
                        neighbour = self._chips[n_x_y]
                        if (neighbour.nearest_ethernet_x ==
                                nearest_ethernet_x and
                            neighbour.nearest_ethernet_y ==
                                nearest_ethernet_y):
                            is_link = True
                            break
            if not is_link:
                removable_coords.append((x, y))
        return removable_coords

    def unreachable_incoming_local_chips(self):
        """
        Detects chips that are not reachable from any of their LOCAL neighbours

        Current implementation does NOT deal with group of unreachable chips

        :return: List (hopefully empty) if the (x,y) cooridinates of
            unreachable chips.
        """
        removable_coords = list()
        for chip in self._chips.values():
            x = chip.x
            y = chip.y
            nearest_ethernet_x = chip.nearest_ethernet_x
            nearest_ethernet_y = chip.nearest_ethernet_y
            # Go through all the chips that surround this one
            moves = [(-1, 0), (-1, -1), (0, -1), (1, 0), (1, 1), (0, 1)]
            is_link = False
            for opposite, (x_move, y_move) in enumerate(moves):
                n_x_y = (x + x_move, y + y_move)
                if n_x_y in self._chips:
                    neighbour = self._chips[n_x_y]
                    if neighbour.router.is_link(opposite):
                        if (neighbour.nearest_ethernet_x ==
                                nearest_ethernet_x and
                            neighbour.nearest_ethernet_y ==
                                nearest_ethernet_y):
                            is_link = True
                            break
            if not is_link:
                removable_coords.append((x, y))
        return removable_coords

    def one_way_links(self):
        """
        :rtype: iterable(tuple(int,int,int))
        """
        link_checks = [(0, 3), (1, 4), (2, 5), (3, 0), (4, 1), (5, 2)]
        for chip in self.chips:
            for out, back in link_checks:
                link = chip.router.get_link(out)
                if link is not None:
                    if not self.is_link_at(
                            link.destination_x, link.destination_y, back):
                        yield chip.x, chip.y, out

    def _minimize_vector(self, x, y):
        """
        Minimizes an x, y, 0 vector.

        When vectors are minimised, (1,1,1) is added or subtracted from them.
        This process does not change the range of numbers in the vector.
        When a vector is minimal,
        it is easy to see that the range of numbers gives the
        magnitude since there are at most two non-zero numbers (with opposite
        signs) and the sum of their magnitudes will also be their range.

        This can be farther optimised with then knowledge that z is always 0

        :param x:
        :param y:
        :return: (x, y, z) vector
        :rtype: tuple(int,int,int)
        """
        if x > 0:
            if y > 0:
                # delta is the smaller of x or y
                if x > y:
                    return (x - y, 0, -y)
                else:
                    return (0, y - x, -x)
            else:
                # two non-zero numbers (with opposite signs)
                return (x, y, 0)
        else:
            if y > 0:
                # two non-zero numbers (with opposite signs)
                return (x, y, 0)
            else:
                # delta is the greater (nearest to zero) of x or y
                if x > y:
                    return (0, y - x, -x)
                else:
                    return (x - y, 0, -y)

    @property
    def virtual_chips(self):
        """
        :rtype: iterable(Chip)
        """
        return itervalues(self._virtual_chips)

    @property
    def local_xys(self):
        """
        Provides a list of local (x,y) values for a perfect board on this
        machine.

        Local (x,y)s never include wrap-arounds.

        Note: no check is done to see if any board in the machine actually
        has a chip with this local x, y

        :return: a list of (x,y) coordinates
        :rtype: iterable(tuple(int,int))
        """
        return self._local_xys
