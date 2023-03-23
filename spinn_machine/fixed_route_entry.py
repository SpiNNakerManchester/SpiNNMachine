# Copyright (c) 2017 The University of Manchester
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

from .exceptions import SpinnMachineAlreadyExistsException


class FixedRouteEntry(object):
    """
    Describes an entry in a SpiNNaker chip's fixed route routing table.
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
        """
        The destination processor IDs.

        :rtype: iterable(int)
        """
        return self._processor_ids

    @property
    def link_ids(self):
        """
        The destination link IDs.

        :rtype: iterable(int)
        """
        return self._link_ids

    def __repr__(self):
        return ("{%s}:{%s}" % (
            ", ".join(map(str, self._link_ids)),
            ", ".join(map(str, self._processor_ids))))
