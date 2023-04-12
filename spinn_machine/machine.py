# Copyright (c) 2014 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .exceptions import (
    SpinnMachineAlreadyExistsException, SpinnMachineException)
from spinn_machine.link_data_objects import FPGALinkData, SpinnakerLinkData
from spinn_utilities.abstract_base import (
    AbstractBase, abstractproperty, abstractmethod)
import logging

logger = logging.getLogger(__name__)


class Machine(object, metaclass=AbstractBase):
    """
    A representation of a SpiNNaker Machine with a number of Chips.
    Machine is also iterable, providing ``((x, y), chip)`` where:

        * ``x`` is the x-coordinate of a chip,
        * ``y`` is the y-coordinate of a chip,
        * ``chip`` is the chip with the given ``(x, y)`` coordinates.

    Use
    :py:func:`~spinn_machine.machine_from_chips`
    and
    :py:func:`~spinn_machine.machine_from_size`
    to determine the correct machine class.
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
    ROUTER_ENTRIES = 1023

    __slots__ = (
        "_boot_ethernet_address",
        "_chips",
        "_ethernet_connected_chips",
        "_fpga_links",
        # Declared height of the machine
        # This can not be changed
        "_height",
        # List of the possible chips (x,y) on each board of the machine
        "_local_xys",
        # Extra information about how this machine was created
        # to be used in the str method
        "_origin",
        "_spinnaker_links",
        "_maximum_user_cores_on_chip",
        # Declared width of the machine
        # This can not be changed
        "_width"
    )

    @staticmethod
    def max_cores_per_chip():
        """
        Gets the max core per chip for the while system.

        There is no guarantee that there will be any Chips with this many
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

        :param int new_max: New value to use for the max
        :raises SpinnMachineException: if `max_cores_per_chip` has already been
            used and is now being changed.
            This exception also happens if the value is set twice to different
            values. For example in the script and in the configuration file.
        """
        if Machine.__max_cores is None:
            Machine.__max_cores = new_max
        elif Machine.__max_cores != new_max:
            raise SpinnMachineException(
                "max_cores_per_chip has already been accessed "
                "so can not be changed.")

    def __init__(self, width, height, chips=None, origin=None):
        """
        :param int width: The width of the machine excluding
        :param int height:
            The height of the machine
        :param iterable(Chip) chips: An iterable of chips in the machine
        :param str origin: Extra information about how this machine was created
            to be used in the str method. Example "``Virtual``" or "``Json``"
        :raise SpinnMachineAlreadyExistsException:
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
        self._chips = dict()
        if chips is not None:
            self.add_chips(chips)

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
        Ethernet-enabled chip.

        :return: True if this machine can have multiple 48 chip boards
        :rtype: bool
        """

    @abstractmethod
    def get_xys_by_ethernet(self, ethernet_x, ethernet_y):
        """
        Yields the potential x,y locations of all the chips on the board
        with this Ethernet-enabled chip. Including the Ethernet-enabled chip
        itself.

        Wrap-arounds are handled as appropriate.

        .. note::
            This method does not check if the chip actually exists as is
            intended to be called to create the chips.

        .. warning::
            GIGO! This methods assumes that ethernet_x and ethernet_y are the
            local 0,0 of an existing board, within the width and height of the
            machine.

        :param int ethernet_x:
            The X coordinate of a (local 0,0) legal Ethernet-enabled chip
        :param int ethernet_y:
            The Y coordinate of a (local 0,0) legal Ethernet-enabled chip
        :return: Yields the (x, y) coordinates of all the potential chips on
            this board.
        :rtype: iterable(tuple(int,int))
        """

    @abstractmethod
    def get_xy_cores_by_ethernet(self, ethernet_x, ethernet_y):
        """
        Yields the potential (x,y) locations and the typical number of cores
        of all the chips on the board with this Ethernet-enabled chip.

        Includes the Ethernet-enabled chip itself.

        Wrap-arounds are handled as appropriate.

        .. note::
            This method does not check if the chip actually exists,
            nor report the actual number of cores on this chip, as is
            intended to be called to create the chips.

        The number of cores is based on the 1,000,000 core machine where the
        board where built with the the 17 core chips placed in the same
        location on nearly every board.

        .. warning::
            GIGO! This methods assumes that ethernet_x and ethernet_y are the
            local 0,0 of an existing board, within the width and height of the
            machine.

        :param int ethernet_x:
            The X coordinate of a (local 0,0) legal Ethernet-enabled chip
        :param int ethernet_y:
            The Y coordinate of a (local 0,0) legal Ethernet-enabled chip
        :return: Yields (x, y, n_cores) where x , y are coordinates of all
            the potential chips on this board, and n_cores is the typical
            number of cores for a chip in that position.
        :rtype: iterable(tuple(int,int))
        """

    @abstractmethod
    def get_down_xys_by_ethernet(self, ethernet_x, ethernet_y):
        """
        Yields the (x,y) coordinates of the down chips on the board with this
        Ethernet-enabled chip.

        .. note::
            The Ethernet chip itself can not be missing if validated.

        Wrap-arounds are handled as appropriate.

        This method does check if the chip actually exists.

        :param int ethernet_x:
            The X coordinate of a (local 0,0) legal Ethernet-enabled chip
        :param int ethernet_y:
            The Y coordinate of a (local 0,0) legal Ethernet-enabled chip
        :return: Yields the (x, y) of the down chips on this board.
        :rtype: iterable(tuple(int,int))
        """

    def get_chips_by_ethernet(self, ethernet_x, ethernet_y):
        """
        Yields the actual chips on the board with this Ethernet-enabled chip.
        Including the Ethernet-enabled chip itself.

        Wrap-arounds are handled as appropriate.

        This method does check if the chip actually exists.

        :param int ethernet_x:
            The X coordinate of a (local 0,0) legal Ethernet-enabled chip
        :param int ethernet_y:
            The Y coordinate of a (local 0,0) legal Ethernet-enabled chip
        :return: Yields the chips on this board.
        :rtype: iterable(Chip)
        """
        for chip_xy in self.get_existing_xys_by_ethernet(
                ethernet_x, ethernet_y):
            yield self._chips[chip_xy]

    @abstractmethod
    def get_existing_xys_by_ethernet(self, ethernet_x, ethernet_y):
        """
        Yields the (x,y)s of actual chips on the board with this
        Ethernet-enabled chip.
        Including the Ethernet-enabled chip itself.

        Wrap-arounds are handled as appropriate.

        This method does check if the chip actually exists.

        :param int ethernet_x:
            The X coordinate of a (local 0,0) legal Ethernet-enabled chip
        :param int ethernet_y:
            The Y coordinate of a (local 0,0) legal Ethernet-enabled chip
        :return: Yields the (x,y)s of chips on this board.
        :rtype: iterable(tuple(int,int))
        """

    @abstractmethod
    def xy_over_link(self, x, y, link):
        """
        Get the potential (x,y) location of the chip reached over this link.

        Wrap-arounds are handled as appropriate.

        .. note::
            This method does not check if either chip source or destination
            actually exists as is intended to be called to create the links.

            It is the callers responsibility to check the validity of this call
            before making it or the validity of the result.

        .. warning::
            GIGO! This methods assumes that x and y are within the width and
            height of the machine, and that the link goes to another chip on
            the machine.

        On machine without full wrap-around it is possible that this method
        generates (x,y) values that fall outside of the legal values including
        negative values, x = width or y = height.

        :param int x: The x coordinate of a chip that will exist on the machine
        :param int y: The y coordinate of a chip that will exist on the machine
        :param int link:
            The link to another chip that could exist on the machine
        :return: x and y coordinates of the chip over that link if it is
            valid or some fictional (x,y) if not.
        :rtype: tuple(int,int)
        """

    @abstractmethod
    def get_local_xy(self, chip):
        """
        Converts the x and y coordinates into the local coordinates on the
        board as if the Ethernet-enabled chip was at position 0,0.

        This method does take wrap-arounds into consideration.

        This method assumes that chip is on the machine or is a copy of a
        chip on the machine

        :param Chip chip: A Chip in the machine
        :return: Local (x, y) coordinates.
        :rtype: tuple(int,int)
        """

    def where_is_chip(self, chip):
        """
        Returns global and local location for this chip.

        This method assumes that chip is on the machine or is a copy of a
        chip on the machine.

        :param Chip chip: A Chip in the machine
        :return: A human-readable description of the location of a chip.
        :rtype: str
        """
        chip00 = self.get_chip_at(0, 0)
        local00 = self.get_chip_at(
            chip.nearest_ethernet_x, chip.nearest_ethernet_y)
        (localx, localy) = self.get_local_xy(chip)
        return (f"global chip {chip.x}, {chip.y} on {chip00.ip_address} "
                f"is chip {localx}, {localy} on {local00.ip_address}")

    def where_is_xy(self, x, y):
        """
        Returns global and local location for this chip.

        :param int x: X coordinate
        :param int y: Y coordinate
        :return: A human-readable description of the location of a chip.
        :rtype: str
        """
        chip = self.get_chip_at(x, y)
        if chip:
            return self.where_is_chip(chip)
        return f"No chip {x}, {y} found"

    @abstractmethod
    def get_global_xy(self, local_x, local_y, ethernet_x, ethernet_y):
        """
        Converts the local (X, Y) coordinates into global (x,y) coordinates,
        under the assumption that they are on the board with local (0,0) at
        global coordinates (`ethernet_x`, `ethernet_y`).

        This method does take wrap-arounds into consideration.

        .. warning::
            GIGO: This method does not check if input parameters make sense,
            nor does it check if there is a chip at the resulting global (x,y)

        :param int local_x: A valid local x coordinate for a chip
        :param int local_y: A valid local y coordinate for a chip
        :param int ethernet_x:
            The global Ethernet-enabled chip X coordinate for the board the
            chip is on
        :param int ethernet_y:
            The global Ethernet-enabled chip Y coordinate for the board the
            chip is on
        :return: global (x,y) coordinates of the chip
        :rtype: tuple(int,int)
        """

    @abstractmethod
    def get_vector_length(self, source, destination):
        """
        Get the mathematical length of the shortest vector (x, y, z) from
        source to destination.

        Use the same algorithm as vector to find the best x, y pair but then
        is optimised to directly calculate length

        This method does not check if the chips and links it assumes to take
        actually exist.
        For example long paths along a non-wrapping edge may well travel
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

        .. warning::
            GIGO: This method does not check if input parameters make sense.

        :param source: (x,y) coordinates of the source chip
        :type source: tuple(int, int)
        :param destination: (x,y) coordinates of the destination chip
        :type destination: tuple(int, int)
        :return: The distance in steps
        :rtype: int
        """

    @abstractmethod
    def get_vector(self, source, destination):
        """
        Get mathematical shortest vector (x, y, z) from source to destination.

        This method does not check if the chips and links it assumes to take
        actually exist.
        For example long paths along a non-wrapping edge may well travel
        through the missing area.

        This method does take wrap-arounds into consideration as applicable.

        From https://github.com/project-rig/rig/blob/master/rig/geometry.py
        Described in http://jhnet.co.uk/articles/torus_paths

        Use the same algorithm as vector_length
        using the best x, y pair as `minimize(x, y, 0)`

        :param source: (x,y) coordinates of the source chip
        :type source: tuple(int, int)
        :param destination: (x,y) coordinates of the destination chip
        :type destination: tuple(int, int)
        :return: The vector
        """

    @abstractmethod
    def concentric_xys(self, radius, start):
        """
        A generator that produces coordinates for concentric rings of
        possible chips based on the links of the chips.

        No check is done to see if the chip exists.
        This may even produce coordinates with negative numbers

        Mostly copied from:
        https://github.com/project-rig/rig/blob/master/rig/geometry.py

        :param int radius: The radius of rings to produce (0 = start only)
        :param tuple(int,int) start: The start coordinate
        :rtype: tuple(int,int)
        """

    def validate(self):
        """
        Validates the machine and raises an exception in unexpected conditions.

        Assumes that at the time this is called all chips are on the board.

        This allows the checks to be avoided when creating a virtual machine
        (Except of course in testing)

        :raises SpinnMachineException:
            * An Error is raised if there is a chip with a x outside of the
              range 0 to width -1.
            * An Error is raised if there is a chip with a y outside of the
              range 0 to height -1.
            * An Error is raise if there is no chip at the declared
              Ethernet-enabled chip x and y.
            * An Error is raised if an Ethernet-enabled chip is not at a local
              0,0.
            * An Error is raised if there is no Ethernet-enabled chip is at
              0,0.
            * An Error is raised if this is a unexpected multiple board
              situation.
        """
        if self._boot_ethernet_address is None:
            raise SpinnMachineException(
                "no ethernet chip at 0, 0 found")
        if len(self._ethernet_connected_chips) > 1:
            if not self.multiple_48_chip_boards():
                raise SpinnMachineException(
                    f"A {self.wrap} machine of size {self._width}, "
                    f"{self._height} can not handle multiple ethernet chips")
        # The fact that self._boot_ethernet_address is set means there is an
        # ethernet chip and it is at 0,0 so no need to check that

        for chip in self.chips:
            if chip.x < 0:
                raise SpinnMachineException(f"{chip} has a negative x")
            if chip.y < 0:
                raise SpinnMachineException(f"{chip} has a negative y")
            if chip.x >= self._width:
                raise SpinnMachineException(
                    f"{chip} has an x larger than width {self._width}")
            if chip.y >= self._height:
                raise SpinnMachineException(
                    f"{chip} has a y larger than height {self._height}")
            if chip.ip_address:
                # Ethernet Chip checks
                if chip.x % 4 != 0:
                    raise SpinnMachineException(
                        f"Ethernet {chip} has a x which is not divisible by 4")
                if (chip.x + chip.y) % 12 != 0:
                    raise SpinnMachineException(
                        f"Ethernet {chip} has an x,y pair that "
                        "does not add up to 12")
            else:
                # Non-Ethernet chip checks
                if not self.is_chip_at(
                        chip.nearest_ethernet_x, chip.nearest_ethernet_y):
                    raise SpinnMachineException(
                        f"{chip} has an invalid ethernet chip")
                local_xy = self.get_local_xy(chip)
                if local_xy not in self._local_xys:
                    raise SpinnMachineException(
                        f"{chip} has an unexpected local xy of {local_xy}")

    @abstractproperty
    def wrap(self):
        """
        A short string representing the type of wrap.

        :rtype: str
        """

    def add_chip(self, chip):
        """
        Add a chip to the machine.

        :param ~spinn_machine.Chip chip: The chip to add to the machine
        :raise SpinnMachineAlreadyExistsException:
            If a chip with the same x and y coordinates already exists
        """
        chip_id = (chip.x, chip.y)
        if chip_id in self._chips:
            raise SpinnMachineAlreadyExistsException(
                "chip", f"{chip.x}, {chip.y}")

        self._chips[chip_id] = chip

        if chip.ip_address is not None:
            self._ethernet_connected_chips.append(chip)
            if (chip.x == 0) and (chip.y == 0):
                self._boot_ethernet_address = chip.ip_address

        if chip.n_user_processors > self._maximum_user_cores_on_chip:
            self._maximum_user_cores_on_chip = chip.n_user_processors

    def add_chips(self, chips):
        """
        Add some chips to the machine.

        :param iterable(~spinn_machine.Chip) chips: an iterable of chips
        :raise SpinnMachineAlreadyExistsException:
            If a chip with the same x and y coordinates as one being added
            already exists
        """
        for next_chip in chips:
            self.add_chip(next_chip)

    @property
    def chips(self):
        """
        An iterable of chips in the machine.

        :rtype: iterable(:py:class:`~spinn_machine.Chip`)
        """
        return iter(self._chips.values())

    @property
    def chip_coordinates(self):
        """
        An iterable of chip coordinates in the machine.

        :rtype: iterable(tuple(int,int))
        """
        return iter(self._chips.keys())

    def __iter__(self):
        """
        Get an iterable of the chip coordinates and chips.

        :return: An iterable of tuples of ((x, y), chip) where:
            * (x, y) is a tuple where:
                * x is the x-coordinate of a chip
                * y is the y-coordinate of a chip
            * chip is a chip
        :rtype: iterable(tuple(tuple(int, int), ~spinn_machine.Chip))
        """
        return iter(self._chips.items())

    def __len__(self):
        """
        Get the total number of chips.

        :return: The number of items in the underlying iterable
        :rtype: int
        """
        return len(self._chips)

    def get_chip_at(self, x, y):
        """
        Get the chip at a specific (x, y) location.
        Also implemented as ``__getitem__((x, y))``

        :param int x: the x-coordinate of the requested chip
        :param int y: the y-coordinate of the requested chip
        :return: the chip at the specified location,
            or ``None`` if no such chip
        :rtype: ~spinn_machine.Chip or None
        """
        chip_id = (x, y)
        if chip_id in self._chips:
            return self._chips[chip_id]
        return None

    def __getitem__(self, x_y_tuple):
        """
        Get the chip at a specific (x, y) location.

        :param tuple(int,int) x_y_tuple: A tuple of (x, y) where:
            * x is the x-coordinate of the chip to retrieve
            * y is the y-coordinate of the chip to retrieve
        :return: the chip at the specified location, or `None` if no such chip
        :rtype: ~spinn_machine.Chip or None
        """
        x, y = x_y_tuple
        return self.get_chip_at(x, y)

    def is_chip_at(self, x, y):
        """
        Determine if a chip exists at the given coordinates.
        Also implemented as ``__contains__((x, y))``

        :param int x: x location of the chip to test for existence
        :param int y: y location of the chip to test for existence
        :return: True if the chip exists, False otherwise
        :rtype: bool
        """
        return (x, y) in self._chips

    def is_link_at(self, x, y, link):
        """
        Determine if a link exists at the given coordinates.

        :param int x: The x location of the chip to test the link of
        :param int y: The y location of the chip to test the link of
        :param int link: The link to test the existence of
        """
        return (x, y) in self._chips and self._chips[x, y].router.is_link(link)

    def __contains__(self, x_y_tuple):
        """
        Determine if a chip exists at the given coordinates.

        :param x_y_tuple: A tuple of (x, y) where:
            * x is the x-coordinate of the chip to retrieve
            * y is the y-coordinate of the chip to retrieve
        :type x_y_tuple: tuple(int, int)
        :return: True if the chip exists, False otherwise
        :rtype: bool
        """
        x, y = x_y_tuple
        return self.is_chip_at(x, y)

    @property
    def width(self):
        """
        The width of the machine, in chips.

        :rtype: int
        """
        return self._width

    @property
    def height(self):
        """
        The height of the machine, in chips.

        :rtype: int
        """
        return self._height

    @property
    def n_chips(self):
        """
        The number of chips in the machine.

        :rtype: int
        """
        return len(self._chips)

    @property
    def ethernet_connected_chips(self):
        """
        The chips in the machine that have an Ethernet connection.

        :rtype: iterable(Chip)
        """
        return self._ethernet_connected_chips

    @property
    def spinnaker_links(self):
        """
        The set of SpiNNaker links in the machine.

        :rtype: iterable(tuple(tuple(str,int),
            ~spinn_machine.link_data_objects.SpinnakerLinkData))
        """
        return iter(self._spinnaker_links.items())

    def get_spinnaker_link_with_id(
            self, spinnaker_link_id, board_address=None, chip_coords=None):
        """
        Get a SpiNNaker link with a given ID.

        :param int spinnaker_link_id: The ID of the link
        :param board_address:
            optional board address that this SpiNNaker link is associated with.
            This is ignored if chip_coords is not `None`.
            If this is `None` and chip_coords is `None`,
            the boot board will be assumed.
        :type board_address: str or None
        :param chip_coords:
            optional chip coordinates that this SpiNNaker link is associated
            with. If this is `None` and board_address is `None`, the boot board
            will be assumed.
        :type chip_coords: tuple(int, int) or None
        :return: The SpiNNaker link data or `None` if no link
        :rtype: ~spinn_machine.link_data_objects.SpinnakerLinkData
        """
        # Try chip coordinates first
        if chip_coords is not None:
            if board_address is not None:
                logger.warning(
                    "Board address will be ignored because chip coordinates"
                    " are specified")
            if chip_coords not in self._chips:
                raise KeyError(f"No chip {chip_coords} found!")
            key = (chip_coords, spinnaker_link_id)
            link_data = self._spinnaker_links.get(key, None)
            if link_data is not None:
                return link_data
            raise KeyError(
                f"SpiNNaker link {spinnaker_link_id} not found"
                f" on chip {chip_coords}")

        # Otherwise try board address.
        if board_address is None:
            board_address = self._boot_ethernet_address
        key = (board_address, spinnaker_link_id)
        if key not in self._spinnaker_links:
            raise KeyError(
                f"SpiNNaker Link {spinnaker_link_id} does not exist on board"
                f" {board_address}")
        return self._spinnaker_links[key]

    def get_fpga_link_with_id(
            self, fpga_id, fpga_link_id, board_address=None, chip_coords=None):
        """
        Get an FPGA link data item that corresponds to the FPGA and FPGA
        link for a given board address.

        :param int fpga_id:
            the ID of the FPGA that the data is going through.  Refer to
            technical document located here for more detail:
            https://drive.google.com/file/d/0B9312BuJXntlVWowQlJ3RE8wWVE
        :param int fpga_link_id:
            the link ID of the FPGA. Refer to technical document located here
            for more detail:
            https://drive.google.com/file/d/0B9312BuJXntlVWowQlJ3RE8wWVE
        :param board_address:
            optional board address that this FPGA link is associated with.
            This is ignored if chip_coords is not `None`.
            If this is `None` and chip_coords is `None`, the boot board will be
            assumed.
        :type board_address: str or None
        :param chip_coords:
            optional chip coordinates that this FPGA link is associated with.
            If this is `None` and board_address is `None`, the boot board
            will be assumed.
        :type chip_coords: tuple(int, int) or None
        :return: the given FPGA link object or ``None`` if no such link
        :rtype: ~spinn_machine.link_data_objects.FPGALinkData
        """
        # Try chip coordinates first
        if chip_coords is not None:
            if board_address is not None:
                logger.warning(
                    "Board address will be ignored because chip coordinates"
                    " are specified")
            if chip_coords not in self._chips:
                raise KeyError(f"No chip {chip_coords} found!")
            key = (chip_coords, fpga_id, fpga_link_id)
            link_data = self._fpga_links.get(key, None)
            if link_data is not None:
                return link_data
            raise KeyError(
                f"FPGA {fpga_id}, link {fpga_link_id} not found"
                f" on chip {chip_coords}")

        # Otherwise try board address
        if board_address is None:
            board_address = self._boot_ethernet_address
        key = (board_address, fpga_id, fpga_link_id)
        if key not in self._fpga_links:
            raise KeyError(
                f"FPGA Link {fpga_id}:{fpga_link_id} does not exist on board"
                f" {board_address}")
        return self._fpga_links[key]

    def add_spinnaker_links(self):
        """
        Add SpiNNaker links that are on a given machine depending on the
        version of the board.
        """
        if self._width == self._height == 2:
            chip_0_0 = self.get_chip_at(0, 0)
            if not chip_0_0.router.is_link(3):
                self._add_spinnaker_link(0, 0, 0, 3, chip_0_0.ip_address)
            chip = self.get_chip_at(1, 0)
            if not chip.router.is_link(0):
                self._add_spinnaker_link(1, 1, 0, 0, chip_0_0.ip_address)
        elif (self._width == self._height == 8) or \
                self.multiple_48_chip_boards():
            for chip in self._ethernet_connected_chips:
                if not chip.router.is_link(4):
                    self._add_spinnaker_link(
                        0, chip.x, chip.y, 4, chip.ip_address)

    def _add_spinnaker_link(
            self, spinnaker_link_id, x, y, link, board_address):
        link_data = SpinnakerLinkData(
            spinnaker_link_id, x, y, link, board_address)
        self._spinnaker_links[board_address, spinnaker_link_id] = link_data
        self._spinnaker_links[(x, y), spinnaker_link_id] = link_data

    def add_fpga_links(self):
        """
        Add FPGA links that are on a given machine depending on the
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
                        fx = (x + ex) % (self._width)
                        fy = (y + ey) % (self._height)
                        self._add_fpga_link(f, lk, fx, fy, l1, ip, ex, ey)
                        f, lk = self._next_fpga_link(f, lk)
                        if i % 2 == 1:
                            x += dx
                            y += dy
                        fx = (x + ex) % (self._width)
                        fy = (y + ey) % (self._height)
                        self._add_fpga_link(f, lk, fx, fy, l2, ip, ex, ey)
                        f, lk = self._next_fpga_link(f, lk)
                        if i % 2 == 0:
                            x += dx
                            y += dy

    # pylint: disable=too-many-arguments
    def _add_fpga_link(self, fpga_id, fpga_link, x, y, link, board_address,
                       ex, ey):
        if self.is_chip_at(x, y):
            link_data = FPGALinkData(
                fpga_link_id=fpga_link, fpga_id=fpga_id,
                connected_chip_x=x, connected_chip_y=y,
                connected_link=link, board_address=board_address)
            self._fpga_links[board_address, fpga_id, fpga_link] = link_data
            # Add for the exact chip coordinates
            self._fpga_links[(x, y), fpga_id, fpga_link] = link_data
            # Add for the Ethernet chip coordinates to allow this to work too
            self._fpga_links[(ex, ey), fpga_id, fpga_link] = link_data

    @staticmethod
    def _next_fpga_link(fpga_id, fpga_link):
        if fpga_link == 15:
            return fpga_id + 1, 0
        return fpga_id, fpga_link + 1

    def __str__(self):
        return (f"[{self._origin}{self.wrap}Machine: width={self._width}, "
                f"height={self._height}, n_chips={len(self._chips)}]")

    def __repr__(self):
        return self.__str__()

    def get_cores_and_link_count(self):
        """
        Get the number of cores and links from the machine.

        Links are assumed to be bidirectional so the total links counted is
        half of the unidirectional links found.

        SpiNNaker and FPGA links are not included.

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
        """
        Get a string detailing the number of cores and links.

        :rtype: str
        """
        cores, links = self.get_cores_and_link_count()
        return f"{cores} cores and {links} links"

    @property
    def boot_chip(self):
        """
        The chip used to boot the machine.

        :rtype: Chip
        """
        return self._chips[0, 0]

    def get_existing_xys_on_board(self, chip):
        """
        Get the chips that are on the same board as the given chip.

        :param chip: The chip to find other chips on the same board as
        :return: An iterable of (x, y) coordinates of chips on the same board
        :rtype: iterable(tuple(int,int))
        """
        return self.get_existing_xys_by_ethernet(
            chip.nearest_ethernet_x, chip.nearest_ethernet_y)

    @property
    def maximum_user_cores_on_chip(self):
        """
        The maximum number of user cores on any chip.

        :rtype: int
        """
        return self._maximum_user_cores_on_chip

    @property
    def total_available_user_cores(self):
        """
        The total number of cores on the machine which are not
        monitor cores.

        :rtype: int
        """
        return sum(chip.n_user_processors for chip in self.chips)

    @property
    def total_cores(self):
        """
        The total number of cores on the machine, including monitors.

        :rtype: int
        """
        return sum(
            1 for chip in self.chips for _processor in chip.processors)

    def unreachable_outgoing_chips(self):
        """
        Detects chips that can not reach any of their neighbours.

        Current implementation does *not* deal with group of unreachable chips.

        :return: List (hopefully empty) if the (x,y) coordinates of
            unreachable chips.
        :rtype: list(tuple(int,int))
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
        Detects chips that are not reachable from any of their neighbours.

        Current implementation does *not* deal with group of unreachable chips.

        :return: List (hopefully empty) if the (x,y) coordinates of
            unreachable chips.
        :rtype: list(tuple(int,int))
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
        Detects chips that can not reach any of their *local* neighbours.

        Current implementation does *not* deal with group of unreachable chips.

        :return: List (hopefully empty) if the (x,y) coordinates of
            unreachable chips.
        :rtype: list(tuple(int,int))
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
        Detects chips that are not reachable from any of their *local*
        neighbours.

        Current implementation does *not* deal with group of unreachable chips.

        :return: List (hopefully empty) if the (x,y) coordinates of
            unreachable chips.
        :rtype: list(tuple(int,int))
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
                        yield chip.x, chip.y, out, back

    def _minimize_vector(self, x, y):
        """
        Minimizes an (x, y, 0) vector.

        When vectors are minimised, (1,1,1) is added or subtracted from them.
        This process does not change the range of numbers in the vector.
        When a vector is minimal,
        it is easy to see that the range of numbers gives the
        magnitude since there are at most two non-zero numbers (with opposite
        signs) and the sum of their magnitudes will also be their range.

        This can be farther optimised with then knowledge that z is always 0

        :param int x:
        :param int y:
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
    def local_xys(self):
        """
        Provides a list of local (x,y) coordinates for a perfect board on this
        machine.

        Local (x,y)s never include wrap-arounds.

        .. note::
            No check is done to see if any board in the machine actually
            has a chip with this local (x, y).

        :rtype: iterable(tuple(int,int))
        """
        return self._local_xys

    def get_unused_xy(self):
        """
        Finds an unused (x,y) coordinate on this machine.

        This method will not return an (x,y) of an existing chip

        This method will not return an (x,y) on any existing board even if that
        chip does not exist, i.e., it will not return (x,y) of a known dead
        chip.

        It will however return the same `unused_xy` until a chip is added at
        that location.

        :return: an unused (x,y) coordinate
        :rtype: (int, int)
        """
        # get a set of xys that could be connected to any existing ethernet
        xys_by_ethernet = set()
        for ethernet in self.ethernet_connected_chips:
            xys_by_ethernet.update(
                self.get_xys_by_ethernet(ethernet.x, ethernet.y))
        x = 0
        while (True):
            for y in range(self.height):
                xy = (x, y)
                if xy not in self._chips and xy not in xys_by_ethernet:
                    return xy
            x += 1

    def _basic_concentric_xys(self, radius, start):
        """
        Generates concentric (x,y)s from start without accounting for wrap
        around or checking if the chip exists.

        :param int radius: The radius of rings to produce (0 = start only)
        :param tuple(int,int) start: The start coordinate
        :rtype: tuple(int,int)
        """
        x, y = start
        yield (x, y)
        for r in range(1, radius + 1):
            # Move to the next layer
            y -= 1
            # Walk around the chips at this radius
            for dx, dy in [(1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1), (1, 0)]:
                for _ in range(r):
                    yield (x, y)
                    x += dx
                    y += dy
