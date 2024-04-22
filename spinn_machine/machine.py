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
from __future__ import annotations
from collections import Counter
import logging
from typing import (
    Dict, Iterable, Iterator, List, Optional, Sequence, Set, Tuple, Union,
    TYPE_CHECKING)
from typing_extensions import TypeAlias
from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from spinn_utilities.typing.coords import XY
from spinn_machine.data import MachineDataView
from spinn_machine.link_data_objects import FPGALinkData, SpinnakerLinkData
from .exceptions import (
    SpinnMachineAlreadyExistsException, SpinnMachineException)

if TYPE_CHECKING:
    from .chip import Chip

logger = logging.getLogger(__name__)
_SpinLinkKey: TypeAlias = Tuple[Union[str, XY], int]
_FpgaLinkKey: TypeAlias = Tuple[Union[str, XY], int, int]


class Machine(object, metaclass=AbstractBase):
    """
    A representation of a SpiNNaker Machine with a number of Chips.
    Machine is also iterable, providing ``((x, y), chip)`` where:

        * ``x`` is the x-coordinate of a chip,
        * ``y`` is the y-coordinate of a chip,
        * ``chip`` is the chip with the given ``(x, y)`` coordinates.

    """

    # Table of the amount to add to the x and y coordinates to get the
    #  coordinates down the given link (0-5)
    LINK_ADD_TABLE = [(1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1)]

    __slots__ = (
        "_boot_ethernet_address",
        # A map off the expected x, y coordinates on a standard board to
        # the most likely number of cores on that chip.
        "_chip_core_map",
        "_chips",
        "_ethernet_connected_chips",
        "_fpga_links",
        # Declared height of the machine
        # This can not be changed
        "_height",
        # A Counter of the number of cores on each Chip
        "_n_cores_counter",
        # A Counter of links on each Chip
        # Counts each direction so the n_links is half the total
        "_n_links_counter",
        # A Counter for the number of router entries on each Chip
        "_n_router_entries_counter",
        # Extra information about how this machine was created
        # to be used in the str method
        "_origin",
        "_spinnaker_links",
        # A Counter for SDRAM on each Chip
        "_sdram_counter",
        # Declared width of the machine
        # This can not be changed
        "_width"
    )

    def __init__(self, width: int, height: int, chip_core_map: Dict[XY, int],
                 origin: str = ""):
        """
        :param int width: The width of the machine excluding
        :param int height:
            The height of the machine
        :param dict((int, int), int) chip_core_map:
            A map off the expected x,y coordinates on a standard board to
            the most likely number of cores on that chip.
        :param str origin: Extra information about how this machine was created
            to be used in the str method. Example "``Virtual``" or "``Json``"
        :raise SpinnMachineAlreadyExistsException:
            If any two chips have the same x and y coordinates
        """
        if origin is not None:
            assert isinstance(origin, str)
        self._width = width
        self._height = height
        self._chip_core_map = chip_core_map

        # The list of chips with Ethernet connections
        self._ethernet_connected_chips: List[Chip] = list()

        # The dictionary of SpiNNaker links by board address and "ID" (int)
        self._spinnaker_links: Dict[_SpinLinkKey, SpinnakerLinkData] = dict()

        # The dictionary of FPGA links by board address, FPGA and link ID
        self._fpga_links: Dict[_FpgaLinkKey, FPGALinkData] = dict()

        # Store the boot chip information
        self._boot_ethernet_address: Optional[str] = None

        # The dictionary of chips
        self._chips: Dict[XY, Chip] = dict()

        self._origin = origin

        self._n_cores_counter: Counter[int] = Counter()
        self._n_links_counter: Counter[int] = Counter()
        self._n_router_entries_counter: Counter[int] = Counter()
        self._sdram_counter: Counter[int] = Counter()

    @abstractmethod
    def get_xys_by_ethernet(
            self, ethernet_x: int, ethernet_y: int) -> Iterable[XY]:
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
        raise NotImplementedError

    @abstractmethod
    def get_xy_cores_by_ethernet(
            self, ethernet_x: int, ethernet_y: int) -> Iterable[
                Tuple[XY, int]]:
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
        :return: Yields `((x, y), n_cores)` where `x, y` are coordinates of all
            the potential chips on this board, and `n_cores` is the typical
            number of cores for a chip in that position.
        :rtype: iterable(tuple(tuple(int,int),int))
        """
        raise NotImplementedError

    @abstractmethod
    def get_down_xys_by_ethernet(
            self, ethernet_x: int, ethernet_y: int) -> Iterable[XY]:
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
        raise NotImplementedError

    def get_chips_by_ethernet(
            self, ethernet_x: int, ethernet_y: int) -> Iterable[Chip]:
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
    def get_existing_xys_by_ethernet(
            self, ethernet_x: int, ethernet_y: int) -> Iterable[XY]:
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
        raise NotImplementedError

    @abstractmethod
    def xy_over_link(self, x: int, y: int, link: int) -> XY:
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
        raise NotImplementedError

    @abstractmethod
    def get_local_xy(self, chip: Chip) -> XY:
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
        raise NotImplementedError

    def where_is_chip(self, chip: Chip) -> str:
        """
        Returns global and local location for this chip.

        This method assumes that chip is on the machine or is a copy of a
        chip on the machine.

        :param Chip chip: A Chip in the machine
        :return: A human-readable description of the location of a chip.
        :rtype: str
        """
        try:
            chip00 = self[0, 0]
            try:
                local00 = self[chip.nearest_ethernet_x,
                               chip.nearest_ethernet_y]
                ip_address = f"on {local00.ip_address}"
            except KeyError:
                ip_address = ""
            (localx, localy) = self.get_local_xy(chip)
            return (f"global chip {chip.x}, {chip.y} on {chip00.ip_address} "
                    f"is chip {localx}, {localy} {ip_address}")
        except Exception:  # pylint: disable=broad-except
            return str(chip)

    def where_is_xy(self, x: int, y: int) -> str:
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
    def get_global_xy(
            self, local_x: int, local_y: int,
            ethernet_x: int, ethernet_y: int) -> XY:
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
        raise NotImplementedError

    @abstractmethod
    def get_vector_length(self, source: XY, destination: XY) -> int:
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
        raise NotImplementedError

    @abstractmethod
    def get_vector(self, source: XY, destination: XY) -> Tuple[int, int, int]:
        """
        Get mathematical shortest vector (x, y, z) from source to destination.
        The z direction uses the diagonal inter-chip links; (0,0,1) is
        equivalent to (1,1,0) in terms of where it reaches but uses a more
        efficient route.

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
        raise NotImplementedError

    @abstractmethod
    def concentric_xys(self, radius: int, start: XY) -> Iterable[XY]:
        """
        A generator that produces coordinates for concentric rings of
        possible chips based on the links of the chips.

        No check is done to see if the chip exists.
        This may even produce coordinates with negative numbers

        Mostly copied from:
        https://github.com/project-rig/rig/blob/master/rig/geometry.py

        :param int radius: The radius of rings to produce (0 = start only)
        :param tuple(int,int) start: The start coordinate
        :rtype: iterable(tuple(int,int))
        """
        raise NotImplementedError

    def validate(self) -> None:
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
        version = MachineDataView.get_machine_version()
        if len(self._ethernet_connected_chips) > 1:
            if not version.supports_multiple_boards:
                raise SpinnMachineException(
                    f"A {self.wrap} machine of size {self._width}, "
                    f"{self._height} can not handle multiple ethernet chips")
        # The fact that self._boot_ethernet_address is set means there is an
        # Ethernet chip and it is at 0,0 so no need to check that

        for chip in self.chips:
            if chip.x < 0:
                raise SpinnMachineException(
                    f"{self.where_is_chip(chip)} has a negative x")
            if chip.y < 0:
                raise SpinnMachineException(
                    f"{self.where_is_chip(chip)} has a negative y")
            if chip.x >= self._width:
                raise SpinnMachineException(
                    f"{self.where_is_chip(chip)} has an x larger "
                    f"than width {self._width}")
            if chip.y >= self._height:
                raise SpinnMachineException(
                    f"{self.where_is_chip(chip)} has a y larger "
                    f"than height {self._height}")
            if chip.n_processors < version.minimum_cores_expected:
                raise SpinnMachineException(
                    f"{self.where_is_chip(chip)} has too few cores "
                    f"found {chip.n_processors}")
            if chip.ip_address:
                # Ethernet Chip checks
                error = version.illegal_ethernet_message(chip.x, chip.y)
                if error is not None:
                    raise SpinnMachineException(
                        f"{self.where_is_chip(chip)} {error}")
            else:
                # Non-Ethernet chip checks
                if not self.is_chip_at(
                        chip.nearest_ethernet_x, chip.nearest_ethernet_y):
                    raise SpinnMachineException(
                        f"{self.where_is_chip(chip)} "
                        f"has an invalid ethernet chip")
                local_xy = self.get_local_xy(chip)
                if local_xy not in self._chip_core_map:
                    raise SpinnMachineException(
                        f"{self.where_is_chip(chip)} "
                        f"has an unexpected local xy of {local_xy}")

    @property
    @abstractmethod
    def wrap(self) -> str:
        """
        A short string representing the type of wrap.

        :rtype: str
        """
        raise NotImplementedError

    def add_chip(self, chip: Chip):
        """
        Add a chip to the machine.

        :param ~spinn_machine.Chip chip: The chip to add to the machine
        :raise SpinnMachineAlreadyExistsException:
            If a chip with the same x and y coordinates already exists
        """
        if chip in self._chips:
            raise SpinnMachineAlreadyExistsException(
                "chip", f"{chip.x}, {chip.y}")

        self._chips[chip] = chip

        # keep some stats about the
        self._n_cores_counter[chip.n_processors] += 1
        self._n_links_counter[len(chip.router)] += 1
        self._n_router_entries_counter[
            chip.router.n_available_multicast_entries] += 1
        self._sdram_counter[chip.sdram] += 1

        if chip.ip_address is not None:
            self._ethernet_connected_chips.append(chip)
            if (chip == (0, 0)):
                self._boot_ethernet_address = chip.ip_address

    def add_chips(self, chips: Iterable[Chip]):
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
    def chips(self) -> Iterator[Chip]:
        """
        An iterable of chips in the machine.

        :rtype: iterable(Chip)
        """
        return iter(self._chips.values())

    @property
    def chip_coordinates(self) -> Iterator[XY]:
        """
        An iterable of chip coordinates in the machine.

        :rtype: iterable(tuple(int,int))
        """
        return iter(self._chips.keys())

    def __iter__(self) -> Iterator[Tuple[XY, Chip]]:
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

    def __len__(self) -> int:
        """
        Get the total number of chips.

        :return: The number of items in the underlying iterable
        :rtype: int
        """
        return len(self._chips)

    def get_chip_at(self, x: int, y: int) -> Optional[Chip]:
        """
        Get the chip at a specific (x, y) location.
        Also implemented as ``__getitem__((x, y))``

        :param int x: the x-coordinate of the requested chip
        :param int y: the y-coordinate of the requested chip
        :return: the chip at the specified location,
            or ``None`` if no such chip
        :rtype: ~spinn_machine.Chip or None
        """
        return self._chips.get((x, y))

    def __getitem__(self, x_y_tuple: XY) -> Chip:
        """
        Get the chip at a specific (x, y) location.

        :param tuple(int,int) x_y_tuple: A tuple of (x, y) where:
            * x is the x-coordinate of the chip to retrieve
            * y is the y-coordinate of the chip to retrieve
        :return: the chip at the specified location
        :rtype: ~spinn_machine.Chip
        """
        return self._chips[x_y_tuple]

    def is_chip_at(self, x: int, y: int) -> bool:
        """
        Determine if a chip exists at the given coordinates.
        Also implemented as ``__contains__((x, y))``

        :param int x: x location of the chip to test for existence
        :param int y: y location of the chip to test for existence
        :return: True if the chip exists, False otherwise
        :rtype: bool
        """
        return (x, y) in self._chips

    def is_link_at(self, x: int, y: int, link: int) -> bool:
        """
        Determine if a link exists at the given coordinates.

        :param int x: The x location of the chip to test the link of
        :param int y: The y location of the chip to test the link of
        :param int link: The link to test the existence of
        """
        return (x, y) in self._chips and self._chips[x, y].router.is_link(link)

    def __contains__(self, x_y_tuple: XY):
        """
        Determine if a chip exists at the given coordinates.

        :param x_y_tuple: A tuple of (x, y) where:
            * x is the x-coordinate of the chip to retrieve
            * y is the y-coordinate of the chip to retrieve
        :type x_y_tuple: tuple(int, int)
        :return: True if the chip exists, False otherwise
        :rtype: bool
        """
        return x_y_tuple in self._chips

    @property
    def width(self) -> int:
        """
        The width of the machine, in chips.

        :rtype: int
        """
        return self._width

    @property
    def height(self) -> int:
        """
        The height of the machine, in chips.

        :rtype: int
        """
        return self._height

    @property
    def n_chips(self) -> int:
        """
        The number of chips in the machine.

        :rtype: int
        """
        return len(self._chips)

    @property
    def ethernet_connected_chips(self) -> Sequence[Chip]:
        """
        The chips in the machine that have an Ethernet connection.

        :rtype: iterable(Chip)
        """
        return self._ethernet_connected_chips

    @property
    def spinnaker_links(self) -> Iterator[
            Tuple[_SpinLinkKey, SpinnakerLinkData]]:
        """
        The set of SpiNNaker links in the machine.

        :rtype: iterable(tuple(tuple(str,int),
            ~spinn_machine.link_data_objects.SpinnakerLinkData))
        """
        return iter(self._spinnaker_links.items())

    def get_spinnaker_link_with_id(
            self, spinnaker_link_id: int, board_address: Optional[str] = None,
            chip_coords: Optional[XY] = None) -> SpinnakerLinkData:
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
        :return: The SpiNNaker link data
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
            c_key = (chip_coords, spinnaker_link_id)
            link_data = self._spinnaker_links.get(c_key, None)
            if link_data is not None:
                return link_data
            raise KeyError(
                f"SpiNNaker link {spinnaker_link_id} not found"
                f" on chip {chip_coords}")

        # Otherwise try board address.
        if board_address is None:
            board_address = self._boot_ethernet_address
            assert board_address is not None
        a_key = (board_address, spinnaker_link_id)
        if a_key not in self._spinnaker_links:
            raise KeyError(
                f"SpiNNaker Link {spinnaker_link_id} does not exist on board"
                f" {board_address}")
        return self._spinnaker_links[a_key]

    def get_fpga_link_with_id(
            self, fpga_id: int, fpga_link_id: int,
            board_address: Optional[str] = None,
            chip_coords: Optional[XY] = None) -> FPGALinkData:
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
        :return: the given FPGA link object
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
            c_key = (chip_coords, fpga_id, fpga_link_id)
            link_data = self._fpga_links.get(c_key, None)
            if link_data is not None:
                return link_data
            raise KeyError(
                f"FPGA {fpga_id}, link {fpga_link_id} not found"
                f" on chip {chip_coords}")

        # Otherwise try board address
        if board_address is None:
            board_address = self._boot_ethernet_address
            assert board_address is not None
        b_key = (board_address, fpga_id, fpga_link_id)
        if b_key not in self._fpga_links:
            raise KeyError(
                f"FPGA Link {fpga_id}:{fpga_link_id} does not exist on board"
                f" {board_address}")
        return self._fpga_links[b_key]

    def add_spinnaker_links(self) -> None:
        """
        Add SpiNNaker links that are on a given machine depending on the
        version of the board.
        """
        version = MachineDataView.get_machine_version()
        for ethernet in self._ethernet_connected_chips:
            ip = ethernet.ip_address
            assert ip is not None
            for (s_id, (local_x, local_y, link)) in enumerate(
                    version.spinnaker_links()):
                global_x, global_y = self.get_global_xy(
                    local_x, local_y, ethernet.x, ethernet.y)
                chip = self.get_chip_at(global_x, global_y)
                if chip is not None and not chip.router.is_link(link):
                    self._add_spinnaker_link(
                        s_id, global_x, global_y, link, ip)

    def _add_spinnaker_link(
            self, spinnaker_link_id: int, x: int, y: int, link: int,
            board_address: str):
        link_data = SpinnakerLinkData(
            spinnaker_link_id, x, y, link, board_address)
        self._spinnaker_links[board_address, spinnaker_link_id] = link_data
        self._spinnaker_links[(x, y), spinnaker_link_id] = link_data

    def add_fpga_links(self) -> None:
        """
        Add FPGA links that are on a given machine depending on the
        version of the board.
        """
        version = MachineDataView.get_machine_version()
        for ethernet in self._ethernet_connected_chips:
            ip = ethernet.ip_address
            assert ip is not None
            for (local_x, local_y, link, fpga_id, fpga_link) in \
                    version.fpga_links():
                global_x, global_y = self.get_global_xy(
                    local_x, local_y, ethernet.x, ethernet.y)
                chip = self.get_chip_at(global_x, global_y)
                if chip is not None:
                    self._add_fpga_link(fpga_id, fpga_link, chip.x, chip.y,
                                        link, ip, ethernet.x, ethernet.y)

    def _add_fpga_link(
            self, fpga_id: int, fpga_link: int, x: int, y: int, link: int,
            board_address: str, ex: int, ey: int):
        # pylint: disable=too-many-arguments
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
    def _next_fpga_link(fpga_id: int, fpga_link: int) -> Tuple[int, int]:
        if fpga_link == 15:
            return fpga_id + 1, 0
        return fpga_id, fpga_link + 1

    def __str__(self) -> str:
        return (f"[{self._origin}{self.wrap}Machine: width={self._width}, "
                f"height={self._height}, n_chips={len(self._chips)}]")

    def __repr__(self) -> str:
        return self.__str__()

    def get_cores_count(self) -> int:
        """
        Get the number of cores from the machine.

        :return: n_cores
        :rtype: int
        """
        return sum(n * count for n, count in self._n_cores_counter.items())

    def get_links_count(self) -> float:
        """
        Get the number of links from the machine.

        Links are assumed to be bidirectional so the total links counted is
        half of the unidirectional links found.

        SpiNNaker and FPGA links are not included.

        :return: n_links; fractional parts indicate partial link problems
        :rtype: float
        """
        return sum(n * count for n, count in self._n_links_counter.items()) / 2

    @property
    def min_n_router_enteries(self) -> int:
        """
        The minimum number of router_enteries found on any Chip

        :return: The lowest n router entry found on any Router
        :rtype: int
        """
        return sorted(self._n_router_entries_counter.keys())[-1]

    def summary_string(self) -> str:
        """
        Gets a summary of the Machine and logs warnings for weirdness

        :return: A String describing the Machine
        :raises IndexError: If there are no Chips in the MAchine
        :raises AttributeError: If there is no boot chip
        """
        # pylint: disable=logging-fstring-interpolation
        version = MachineDataView.get_machine_version()

        sdram = sorted(self._sdram_counter.keys())
        if len(sdram) == 1:
            if sdram[0] != version.max_sdram_per_chip:
                logger.warning(
                    f"The sdram per chip of {sdram[0]} was different to the "
                    f"expected value of {version.max_sdram_per_chip} "
                    f"for board Version {version.name}")
            sdram_st = f"sdram of {sdram[0]} bytes"
        else:
            sdram_st = f"sdram of between {sdram[0]} and {sdram[-1]} bytes"
            logger.warning(f"Not all Chips have the same sdram. "
                           f"The counts where {self._sdram_counter}.")

        routers = sorted(self._n_router_entries_counter.keys())
        if len(routers) == 1:
            if routers[0] != version.n_router_entries:
                logger.warning(
                    f"The number of router entries per chip of {routers[0]} "
                    f"was different to the expected value of "
                    f"{version.n_router_entries} "
                    f"for board Version {version.name}")
            routers_st = f"router table of size {routers[0]}"
        else:
            routers_st = (f"router table sizes between "
                          f"{routers[0]} and {routers[-1]}")
            logger.warning(
                f"Not all Chips had the same n_router_tables. "
                f"The counts where {self._n_router_entries_counter}.")

        cores = sorted(self._n_cores_counter.keys())
        if len(cores) == 1:
            cores_st = f" {cores[0]} cores"
        else:
            cores_st = f"between {cores[0]} and {cores[-1]} cores"

        links = sorted(self._n_links_counter.keys())
        if len(links) == 1:
            links_st = f" {links[0]} links."
        else:
            links_st = f"between {links[0]} and {links[-1]} links"

        return (
            f"Machine on {self.boot_chip.ip_address} "
            f"with {self.n_chips} Chips, {self.get_cores_count()} cores "
            f"and {self.get_links_count()} links. "
            f"Chips have {sdram_st}, {routers_st}, {cores_st} and {links_st}.")

    @property
    def boot_chip(self) -> Chip:
        """
        The chip used to boot the machine.

        :rtype: Chip
        """
        return self._chips[0, 0]

    def get_existing_xys_on_board(self, chip: Chip) -> Iterable[XY]:
        """
        Get the chips that are on the same board as the given chip.

        :param chip: The chip to find other chips on the same board as
        :return: An iterable of (x, y) coordinates of chips on the same board
        :rtype: iterable(tuple(int,int))
        """
        return self.get_existing_xys_by_ethernet(
            chip.nearest_ethernet_x, chip.nearest_ethernet_y)

    @property
    def total_available_user_cores(self) -> int:
        """
        The total number of cores on the machine which are not
        monitor cores.

        :rtype: int
        """
        return sum(chip.n_placable_processors for chip in self.chips)

    @property
    def total_cores(self) -> int:
        """
        The total number of cores on the machine, including monitors.

        :rtype: int
        """
        return sum(chip.n_processors for chip in self.chips)

    def unreachable_outgoing_chips(self) -> List[XY]:
        """
        Detects chips that can not reach any of their neighbours.

        Current implementation does *not* deal with group of unreachable chips.

        :return: List (hopefully empty) if the (x,y) coordinates of
            unreachable chips.
        :rtype: list(tuple(int,int))
        """
        removable_coords: List[XY] = list()
        for (x, y) in self.chip_coordinates:
            # If no links out of the chip work, remove it
            for link in range(6):
                if self.is_link_at(x, y, link):
                    break
            else:
                removable_coords.append((x, y))
        return removable_coords

    def unreachable_incoming_chips(self) -> List[XY]:
        """
        Detects chips that are not reachable from any of their neighbours.

        Current implementation does *not* deal with group of unreachable chips.

        :return: List (hopefully empty) if the (x,y) coordinates of
            unreachable chips.
        :rtype: list(tuple(int,int))
        """
        removable_coords: List[XY] = list()
        for (x, y) in self.chip_coordinates:
            # Go through all the chips that surround this one
            moves = [(1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1)]
            for link, (x_move, y_move) in enumerate(moves):
                opposite = (link + 3) % 6
                next_x = x + x_move
                next_y = y + y_move
                if self.is_link_at(next_x, next_y, opposite):
                    break
            else:
                removable_coords.append((x, y))
        return removable_coords

    def unreachable_outgoing_local_chips(self) -> List[XY]:
        """
        Detects chips that can not reach any of their *local* neighbours.

        Current implementation does *not* deal with group of unreachable chips.

        :return: List (hopefully empty) if the (x,y) coordinates of
            unreachable chips.
        :rtype: list(tuple(int,int))
        """
        removable_coords: List[XY] = list()
        for chip in self._chips.values():
            # If no links out of the chip work, remove it
            moves = [(1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1)]
            x, y = chip
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
                            break
            else:
                removable_coords.append((x, y))
        return removable_coords

    def unreachable_incoming_local_chips(self) -> List[XY]:
        """
        Detects chips that are not reachable from any of their *local*
        neighbours.

        Current implementation does *not* deal with group of unreachable chips.

        :return: List (hopefully empty) if the (x,y) coordinates of
            unreachable chips.
        :rtype: list(tuple(int,int))
        """
        removable_coords: List[XY] = list()
        for chip in self._chips.values():
            x, y = chip
            nearest_ethernet_x = chip.nearest_ethernet_x
            nearest_ethernet_y = chip.nearest_ethernet_y
            # Go through all the chips that surround this one
            moves = [(-1, 0), (-1, -1), (0, -1), (1, 0), (1, 1), (0, 1)]
            for opposite, (x_move, y_move) in enumerate(moves):
                n_x_y = (x + x_move, y + y_move)
                if n_x_y in self._chips:
                    neighbour = self._chips[n_x_y]
                    if neighbour.router.is_link(opposite):
                        if (neighbour.nearest_ethernet_x ==
                                nearest_ethernet_x and
                            neighbour.nearest_ethernet_y ==
                                nearest_ethernet_y):
                            break
            else:
                removable_coords.append((x, y))
        return removable_coords

    def one_way_links(self) -> Iterable[Tuple[int, int, int, int]]:
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

    @staticmethod
    def _minimize_vector(x: int, y: int) -> Tuple[int, int, int]:
        """
        Minimises an (x, y, 0) vector.

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
    def local_xys(self) -> Iterable[XY]:
        """
        Provides a list of local (x,y) coordinates for a perfect board on this
        machine.

        Local (x,y)s never include wrap-arounds.

        .. note::
            No check is done to see if any board in the machine actually
            has a chip with this local (x, y).

        :rtype: iterable(tuple(int,int))
        """
        return self._chip_core_map.keys()

    def get_unused_xy(self) -> XY:
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
        # get a set of xys that could be connected to any existing Ethernet
        xys_by_ethernet: Set[XY] = set()
        for ethernet_x, ethernet_y in self.ethernet_connected_chips:
            xys_by_ethernet.update(self.get_xys_by_ethernet(
                ethernet_x, ethernet_y))
        x = 0
        while (True):
            for y in range(self.height):
                xy = (x, y)
                if xy not in self._chips and xy not in xys_by_ethernet:
                    return xy
            x += 1

    @staticmethod
    def _basic_concentric_xys(radius: int, start: XY) -> Iterator[XY]:
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
