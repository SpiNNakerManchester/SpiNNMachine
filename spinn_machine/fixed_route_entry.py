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
    Describes the sole entry in a SpiNNaker chip's fixed route routing table.
    There is only one fixed route entry per chip.
    """
    __slots__ = (
        # the processors IDs for this route
        "_processor_ids",
        # the link IDs for this route
        "_link_ids",
        "__repr")

    def __init__(self, processor_ids, link_ids):
        """
        :param iterable(int) processor_ids:
        :param iterable(int) link_ids:
        """
        self.__repr = None
        # Add processor IDs, checking that there is only one of each
        self._processor_ids = frozenset(processor_ids)
        self.__check_dupes(processor_ids, "processor ID")

        # Add link IDs, checking that there is only one of each
        self._link_ids = frozenset(link_ids)
        self.__check_dupes(link_ids, "link ID")

    @staticmethod
    def __check_dupes(sequence, name):
        check = set()
        for _id in sequence:
            if _id in check:
                raise SpinnMachineAlreadyExistsException(name, str(_id))
            check.add(_id)

    @property
    def processor_ids(self):
        """
        The destination processor IDs.

        :rtype: frozenset(int)
        """
        return self._processor_ids

    @property
    def link_ids(self):
        """
        The destination link IDs.

        :rtype: frozenset(int)
        """
        return self._link_ids

    def __repr__(self):
        if not self.__repr:
            self.__repr = ("{%s}:{%s}" % (
                ", ".join(map(str, sorted(self._link_ids))),
                ", ".join(map(str, sorted(self._processor_ids)))))
        return self.__repr
