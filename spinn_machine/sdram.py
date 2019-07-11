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

from .exceptions import SpinnMachineInvalidParameterException


class SDRAM(object):
    """ Represents the properties of the SDRAM of a chip in the machine
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
        """ The SDRAM available for user applications

        :return: The space available in bytes
        :rtype: int
        """
        return self._size

    def __str__(self):
        return "{} MB".format(self._size // (1024 * 1024))

    def __repr__(self):
        return self.__str__()
