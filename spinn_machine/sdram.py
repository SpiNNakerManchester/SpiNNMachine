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

from .exceptions import SpinnMachineInvalidParameterException


class SDRAM(object):
    """
    Represents the properties of the SDRAM of a chip in the machine.
    """

    DEFAULT_SDRAM_BYTES = 117 * 1024 * 1024
    max_sdram_found = 0

    __slots__ = ("_size", )

    def __init__(self, size=DEFAULT_SDRAM_BYTES):
        """
        :param size: the space available in SDRAM
        :type size: int
        """
        if size < 0:
            raise SpinnMachineInvalidParameterException(
                "size", size, "negative sizes are meaningless")
        SDRAM.max_sdram_found = max(SDRAM.max_sdram_found, size)
        self._size = size

    @property
    def size(self):
        """
        The SDRAM available for user applications, in bytes.

        :rtype: int
        """
        return self._size

    def __str__(self):
        return f"{self._size // (1024 * 1024)} MB"

    def __repr__(self):
        return self.__str__()
