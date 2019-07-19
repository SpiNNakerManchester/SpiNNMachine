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

from .exceptions import SpinnMachineAlreadyExistsException


class FixedRouteEntry(object):
    """ Describes an entry in a SpiNNaker chip's fixed route routing table.
    """

    __slots__ = (

        # the processors IDs for this route
        "_processor_ids",

        # the link IDs for this route
        "_link_ids"
    )

    def __init__(self, processor_ids, link_ids):
        # Add processor IDs, checking that there is only one of each
        self._processor_ids = set()
        for processor_id in processor_ids:
            if processor_id in self._processor_ids:
                raise SpinnMachineAlreadyExistsException(
                    "processor ID", str(processor_id))
            self._processor_ids.add(processor_id)

        # Add link IDs, checking that there is only one of each
        self._link_ids = set()
        for link_id in link_ids:
            if link_id in self._link_ids:
                raise SpinnMachineAlreadyExistsException(
                    "link ID", str(link_id))
            self._link_ids.add(link_id)

    @property
    def processor_ids(self):
        """ The destination processor IDs

        :return: An iterable of processor IDs
        :rtype: iterable(int)
        """
        return self._processor_ids

    @property
    def link_ids(self):
        """ The destination link IDs

        :return: An iterable of link IDs
        :rtype: iterable(int)
        """
        return self._link_ids

    def __repr__(self):
        return ("{%s}:{%s}" % (
            ", ".join(map(str, self._link_ids)),
            ", ".join(map(str, self._processor_ids))))
