# Copyright (c) 2023 The University of Manchester
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
import logging
from typing import Dict, List, Optional, Sequence, Tuple, TYPE_CHECKING
from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from spinn_utilities.log import FormatAdapter
from spinn_utilities.config_holder import get_config_int_or_none
from spinn_utilities.typing.coords import XY
from spinn_machine.data import MachineDataView
from spinn_machine.exceptions import SpinnMachineException
if TYPE_CHECKING:
    from spinn_machine.machine import Machine

logger = FormatAdapter(logging.getLogger(__name__))


class AbstractVersion(object, metaclass=AbstractBase):
    """
    Base class for the version classes.

    Version classes are the main way to create a Machine object of the
    correct class.

    The version classes contain properties that will change depending
    on the version.
    """

    __slots__ = (
        # the board address associated with this tag
        "_max_cores_per_chip",
        "_max_sdram_per_chip")

    def __init__(self, max_cores_per_chip: int, max_sdram_per_chip: int):
        self.__verify_config_width_height()
        self.__set_max_cores_per_chip(max_cores_per_chip)
        self.__set_max_sdram_per_chip(max_sdram_per_chip)

    def __verify_config_width_height(self) -> None:
        """
        Check that if there is a cfg width or height the values are valid

        :raises SpinnMachineException:
            If the cfg width or height is unexpected
        """
        width = get_config_int_or_none("Machine", "width")
        height = get_config_int_or_none("Machine", "height")
        if width is None:
            if height is None:
                pass
            else:
                raise SpinnMachineException(
                    f"the cfg has a [Machine]width {width} but a no height")
        else:
            if height is None:
                raise SpinnMachineException(
                    f"the cfg has a [Machine]height {width} but a no width")
            else:
                self.verify_size(width, height)

    def __set_max_cores_per_chip(self, max_cores_per_chip: int):
        self._max_cores_per_chip = max_cores_per_chip
        max_machine_core = get_config_int_or_none(
            "Machine", "max_machine_core")
        if max_machine_core is not None:
            if max_machine_core > self._max_cores_per_chip:
                logger.info(
                    f"Ignoring csg setting [Machine]max_machine_core "
                    f"{max_machine_core} as it is larger than "
                    f"{self._max_cores_per_chip} which is the default for a "
                    f"{self.name} board ")
            if max_machine_core < self._max_cores_per_chip:
                logger.warning(
                    f"Max cores per chip reduced to {max_machine_core} "
                    f"due to cfg setting [Machine]max_machine_core")
                self._max_cores_per_chip = max_machine_core

    def __set_max_sdram_per_chip(self, max_sdram_per_chip: int):
        self._max_sdram_per_chip = max_sdram_per_chip
        max_sdram = get_config_int_or_none(
            "Machine", "max_sdram_allowed_per_chip")
        if max_sdram is not None:
            if max_sdram > self._max_sdram_per_chip:
                logger.info(
                    f"Ignoring csg setting "
                    f"[Machine]max_sdram_allowed_per_chip "
                    f"{max_sdram} as it is larger than "
                    f"{self._max_sdram_per_chip} which is the default for a "
                    f"{self.name} board ")
            if max_sdram < self._max_sdram_per_chip:
                logger.warning(
                    f"Max SDRAM per chip reduced to {max_sdram_per_chip} "
                    f"due to cfg setting [Machine]max_sdram_allowed_per_chip")
                self._max_sdram_per_chip = max_sdram

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name of the specific version.

        :rtype: str
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def number(self) -> int:
        """
        The version number that produced this Version.

        :rtype: int
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def board_shape(self) -> Tuple[int, int]:
        """
        The width and height of a single board of this type
        """
        raise NotImplementedError

    @property
    def max_cores_per_chip(self) -> int:
        """
        Gets the maximum number of cores per chip for the whole system.

        There is no guarantee that there will be any chips with this many
        cores, only that there will be no cores with more.

        :rtype: int
        """
        return self._max_cores_per_chip

    @property
    @abstractmethod
    def n_scamp_cores(self) -> int:
        """
        The number of scamp cores per chip.

        :rtype: int
        """
        raise NotImplementedError

    @property
    def max_sdram_per_chip(self) -> int:
        """
        Gets the maximum SDRAM per chip for the whole system.

        While it is likely that all Chips will have this SDRAM
        this should not be counted on. Ask each Chip for its SDRAM.

        :return: the default SDRAM per chip
        :rtype: int
        """
        return self._max_sdram_per_chip

    @property
    def n_chips_per_board(self) -> int:
        """
        The normal number of chips on each board of this version.

        Remember that will the board may have dead or excluded chips.

        :rtype: int
        """
        return len(self.chip_core_map)

    @property
    @abstractmethod
    def n_router_entries(self) -> int:
        """
        The standard number of router entries in a router table.

        While it is likely that all chips will have this number it should
        not be counted on. Ask each chip's router for the correct value.

        :rtype: int
        """
        raise NotImplementedError

    @property
    def expected_xys(self) -> Sequence[XY]:
        """
        List of the standard x,y coordinates of chips for this version.

        Remember that will the board may have dead or excluded chips.

        :return:
        """
        return list(self.chip_core_map.keys())

    @property
    @abstractmethod
    def chip_core_map(self) -> Dict[XY, int]:
        """
        A map off the expected x,y coordinates on a standard board to
        the most likely number of cores on that chip.

        :rtype: dict((int, int), int)
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def clock_speeds_hz(self) -> List[int]:
        """
        The processor clock speeds in Hz this processor can run at

        :rtype: int
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def dtcm_bytes(self) -> int:
        """
        The Data Tightly Coupled Memory available on a processor in bytes

        :rtype: int
        """
        raise NotImplementedError

    @abstractmethod
    def get_potential_ethernet_chips(
            self, width: int, height: int) -> Sequence[XY]:
        """
        Get the coordinates of chips that should be Ethernet chips.

        This may well be passed down to SpiNNakerTriadGeometry.

        .. note::
            This methods assumes that width and height would pass
            :py:meth:`verify_size`.
            If not, the results may be wrong.

        :param int width: The width of the machine to find the chips in
        :param int height: The height of the machine to find the chips in
        :rtype: list(tuple(int, int))
        """
        raise NotImplementedError

    def verify_size(self, width: Optional[int], height: Optional[int]):
        """
        Checks that the width and height are allowed for this version.

        :param int width:
        :param int height:
        :raise SpinnMachineException: If the size is unexpected
        """
        if width is None:
            raise SpinnMachineException("Width can not be None")
        if height is None:
            raise SpinnMachineException("Height can not be None")
        if width <= 0:
            raise SpinnMachineException(f"Unexpected width={width}")
        if height <= 0:
            raise SpinnMachineException(f"Unexpected height={height}")
        self._verify_size(width, height)

    @abstractmethod
    def _verify_size(self, width: int, height: int):
        """
        Implements the width and height checks that depend on the version.

        :param int width:
        :param int height:
        :raise SpinnMachineException:
            If the size is unexpected
        """
        raise NotImplementedError

    def create_machine(
            self, width: Optional[int], height: Optional[int],
            origin: Optional[str] = None) -> Machine:
        """
        Creates a new empty machine based on the width, height and version.

        :param int width: The width of the machine excluding any virtual chips
        :param int height:
            The height of the machine excluding any virtual chips
        :param origin: Extra information about how this machine was created
            to be used in ``str(version)``. Example "``Virtual``" or "``Json``"
        :type origin: str or None
        :return: A subclass of Machine with no chips in it
        :rtype: ~spinn_machine.Machine
        :raises SpinnMachineInvalidParameterException:
            If the size is unexpected
        """
        self.verify_size(width, height)
        return self._create_machine(width or 0, height or 0, origin or "")

    @abstractmethod
    def _create_machine(self, width: int, height: int, origin: str) -> Machine:
        """
        Create a new empty machine based on the width, height and version.
        The width and height will have been validated.

        :param int width: The width of the machine excluding any virtual chips
        :param int height:
            The height of the machine excluding any virtual chips
        :param origin: Extra information about how this machine was created
            to be used in the str method. Example "``Virtual``" or "``Json``"
        :type origin: str
        :return: A subclass of Machine with no Chips in it
        :rtype: ~spinn_machine.Machine
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def minimum_cores_expected(self) -> int:
        """
        The minimum number of Chip that we expect from a Chip

        If there are less that this number of Cores Machine.validate and
        other methods are allowed to raise an exception

        :rtype: int
        :return: The lowest number of cores to accept before flagging a
            Chip to be blacklisted
        """
        raise NotImplementedError

    @abstractmethod
    def illegal_ethernet_message(self, x: int, y: int) -> Optional[str]:
        """
        Checks if x and y could be for an Ethernet.

        This method will return an explanation if the values for x and y are
        known be illegal for an Ethernet chip.

        Due to the limited information available this method will generate
        False negatives.
        So this method returning None does not imply that x, y is an
        Ethernet location

        :param int x:
        :param int y:
        :return: An explanation that the x and y can never be an Ethernet
        """
        raise NotImplementedError

    def size_from_n_cores(self, n_cores: int) -> Tuple[int, int]:
        """
        Returns the size needed to support this many cores.

        Takes into consideration scamp and monitor cores.

        Designed for use with virtual boards.
        Does not include a safety factor for blacklisted cores or chips.
        For real machines a slightly bigger Machine may be needed.

        :param int n_cores: Number of None Scamp and monitor cores needed
        :rtype: (int, int)
        """
        cores_per_board = sum(self.chip_core_map.values())
        cores_per_board -= MachineDataView.get_ethernet_monitor_cores()
        cores_per_board -= (
                (MachineDataView.get_all_monitor_cores() + self.n_scamp_cores)
                * self.n_chips_per_board)
        # Double minus to round up
        return self.size_from_n_boards(-(-n_cores // cores_per_board))

    def size_from_n_chips(self, n_chips: int) -> Tuple[int, int]:
        """
        Returns the size needed to support this many chips.

        Designed for use with virtual boards.
        Does not include a safety factor for blacklisted Chips.
        For real machines a slightly bigger Machine may be needed.

        :param int n_boards:
        :rtype: (int, int)
        :raises SpinnMachineException:
            If multiple boards are needed but not supported
        """
        # Double minus to round up
        return self.size_from_n_boards(-(-n_chips // self.n_chips_per_board))

    def size_from_n_boards(self, n_boards: int) -> Tuple[int, int]:
        """
        Returns the size needed to support this many boards.

        :param int n_boards:
        :rtype: (int, int)
        :raises SpinnMachineException:
            If multiple boards are needed but not supported
        """
        # Override for versions that support multiple boards
        if n_boards == 1:
            return self.board_shape
        if self.supports_multiple_boards:
            raise NotImplementedError
        raise SpinnMachineException(
            f"Version {self} does not support multiple boards")

    @property
    @abstractmethod
    def supports_multiple_boards(self) -> bool:
        """
        Specifies if this version allows machines of more than one board

        :return:
        """
        raise NotImplementedError

    def spinnaker_links(self) -> List[Tuple[int, int, int]]:
        """
        The list of Local X, Y and link Id to add spinnaker links to

        These are applied local to each Ethernet Chip and only if the link is
        not connected to another board

        :rtype: List((int, int, int))
        """
        raise NotImplementedError

    def fpga_links(self) -> List[Tuple[int, int, int, int, int]]:
        """
        The list of Local X, Y, link, fpga_link_id and fpga_id

        These are applied local to each Ethernet Chip and even if the link is
        connected to another board

        :rtype: List((int, int, int, int, int))
        """
        raise NotImplementedError

    def quads_maps(self) -> Optional[Dict[int, Tuple[int, int, int]]]:
        """
        If applicable returns a map of virtual id to quad qx, qy, qp

        Spin 1 boards will return None!

        :rtype: None or dict(int, (int, int, int)
        """
        raise NotImplementedError
