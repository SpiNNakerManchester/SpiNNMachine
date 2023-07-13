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

import logging
from spinn_utilities.abstract_base import (
    AbstractBase, abstractmethod, abstractproperty)
from spinn_utilities.log import FormatAdapter
from spinn_utilities.config_holder import get_config_int
from spinn_machine.exceptions import SpinnMachineException

logger = FormatAdapter(logging.getLogger(__name__))


class AbstractVersion(object, metaclass=AbstractBase):
    """
    Properties for sa spec
    """

    __slots__ = [
        # the board address associated with this tag
        "_max_cores_per_chip",
        "_max_sdram_per_chip"
    ]

    def __init__(self, max_cores_per_chip, max_sdram_per_chip):
        self.__verify_config_width_height()
        self.__set_max_cores_per_chip(max_cores_per_chip)
        self.__set_max_sdram_per_chip(max_sdram_per_chip)

    def __verify_config_width_height(self):
        """
        Check that if there is a cfg width or height the values are valid

        :raises SpinnMachineException:
            If the cfg width or height is unexpected
        """
        width = get_config_int("Machine", "width")
        height = get_config_int("Machine", "height")
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

    def __set_max_cores_per_chip(self, max_cores_per_chip):
        self._max_cores_per_chip = max_cores_per_chip
        max_machine_core = get_config_int("Machine", "max_machine_core")
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

    def __set_max_sdram_per_chip(self, max_sdram_per_chip):
        self._max_sdram_per_chip = max_sdram_per_chip
        max_sdram = get_config_int("Machine", "max_sdram_allowed_per_chip")
        if max_sdram is not None:
            if max_sdram > self._max_sdram_per_chip:
                logger.info(
                    f"Ignoring csg setting "
                    f"[Machine]max_sdram_allowed_per_chip "
                    f"{max_sdram} as it is larger than "
                    f"{self._max_sdram_per_chip} which is the default for a "
                    f"{self.name} board ")
            if max_sdram < self._max_cores_per_chip:
                logger.warning(
                    f"Max sdram per chip reduced to {max_sdram_per_chip} "
                    f"due to cfg setting [Machine]max_sdram_allowed_per_chip")
                self._max_sdram_per_chip = max_sdram_per_chip

    @abstractproperty
    def name(self):
        """
        The name of the Specific version

        :rtype: str
        """

    @property
    def max_cores_per_chip(self):
        """
        Gets the max core per chip for the whole system.

        There is no guarantee that there will be any Chips with this many
        cores, only that there will be no cores with more.

        :return: the default cores per chip
        :rtype: int
        """
        return self._max_cores_per_chip

    @abstractproperty
    def n_non_user_cores(self):
        """
        The number of user cores per chip

        :rtype: int
        """

    @property
    def max_sdram_per_chip(self):
        """
        Gets the max sdram per chip for the whole system.

        While it is likely that all Chips will have this sdram
        this should not be counted on. Ask each Chip for its sdram.

        :return: the default sdram per chip
        :rtype: int
        """
        return self._max_sdram_per_chip

    @abstractproperty
    def n_chips_per_board(self):
        """
        The normal number of Chips on each board of this version

        Remember that will the board may have dead or excluded chips

        :rtype: int
        """

    def verify_size(self, width, height):
        """
        Checks that the width and height are allowed for this version

        :param int width:
        :param int height:
        :raise SpinnMachineException: If the size is unexpected
        """
        if width is None:
            raise SpinnMachineException("Width can not be None")
        if height is None:
            raise SpinnMachineException("Height can not be None")
        if width <= 0:
            raise SpinnMachineException("Unexpected {width=}")
        if height <= 0:
            raise SpinnMachineException("Unexpected {height=}")
        self._verify_size(width, height)

    @abstractmethod
    def _verify_size(self, width, height):
        """
        Adds the width and height checks that depend on the version

        :param int width:
        :param int height:
        :raise SpinnMachineException:
            If the size is unexpected
        """

    def create_machine(self, width, height, origin=None):
        """
        Creates a new Empty machine based on the width, height and version

        :param int width: The width of the machine excluding any virtual chips
        :param int height:
            The height of the machine excluding any virtual chips
        :param origin: Extra information about how this machine was created
            to be used in the str method. Example "``Virtual``" or "``Json``"
        :type origin: str or None
        :return: A subclass of Machine with no Chips in it
        :rtype: ~spinn_machine.Machine
        :raises SpinnMachineInvalidParameterException:
            If the size is unexpected
        """
        self.verify_size(width, height)
        return self._create_machine(width, height, origin)

    @abstractmethod
    def _create_machine(self, width, height, origin):
        """
        Creates a new Empty machine based on the width, height and version

        :param int width: The width of the machine excluding any virtual chips
        :param int height:
            The height of the machine excluding any virtual chips
        :param origin: Extra information about how this machine was created
            to be used in the str method. Example "``Virtual``" or "``Json``"
        :type origin: str or None
        :return: A subclass of Machine with no Chips in it
        :rtype: ~spinn_machine.Machine
        """
