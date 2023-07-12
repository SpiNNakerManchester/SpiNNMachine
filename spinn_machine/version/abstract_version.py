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
from spinn_utilities.abstract_base import (AbstractBase, abstractproperty)
from spinn_utilities.log import FormatAdapter
from spinn_utilities.config_holder import get_config_int

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

        self._max_sdram_per_chip = max_sdram_per_chip
        max_sdram = get_config_int("Machine", "max_sdram_allowed_per_chip")
        if max_sdram is not None:
            if max_sdram > self._max_sdram_per_chip:
                logger.info(
                    f"Ignoring csg setting [Machine]max_sdram_allowed_per_chip "
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
