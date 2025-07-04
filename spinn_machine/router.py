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
from typing import (
    Dict, Iterable, Iterator, List, Optional, Tuple, Union, TYPE_CHECKING)
from .exceptions import (
    SpinnMachineAlreadyExistsException, SpinnMachineInvalidParameterException)
if TYPE_CHECKING:
    from .link import Link
    from .multicast_routing_entry import MulticastRoutingEntry
    from .routing_entry import RoutingEntry


class Router(object):
    """
    Represents a router of a chip, with a set of available links.
    The router is iterable over the links, providing (source_link_id,
    link) where:

        * ``source_link_id`` is the ID of a link
        * ``link`` is the :py:class:`Link` with ID ``source_link_id``
    """

    # The maximum number of links/directions a router can handle
    MAX_LINKS_PER_ROUTER = 6

    # Number to add or sub from a link to get its opposite
    LINK_OPPOSITE = 3

    MAX_CORES_PER_ROUTER = 18

    __slots__ = ("_links", "_n_available_multicast_entries")

    def __init__(
            self, links: Iterable[Link],
            n_available_multicast_entries: int):
        """
        :param links: iterable of links
        :param n_available_multicast_entries:
            The number of entries available in the routing table
        :raise ~spinn_machine.exceptions.SpinnMachineAlreadyExistsException:
            If any two links have the same ``source_link_id``
        """
        self._links: Dict[int, Link] = dict()
        for link in links:
            self.add_link(link)

        self._n_available_multicast_entries = n_available_multicast_entries

    def add_link(self, link: Link) -> None:
        """
        Add a link to the router of the chip.

        :param link: The link to be added
        :raise ~spinn_machine.exceptions.SpinnMachineAlreadyExistsException:
            If another link already exists with the same ``source_link_id``
        """
        if link.source_link_id in self._links:
            raise SpinnMachineAlreadyExistsException(
                "link", str(link.source_link_id))
        self._links[link.source_link_id] = link

    def is_link(self, source_link_id: int) -> bool:
        """
        Determine if there is a link with ID source_link_id.
        Also implemented as ``__contains__(source_link_id)``

        :param source_link_id: The ID of the link to find
        :return: True if there is a link with the given ID, False otherwise
        """
        return source_link_id in self._links

    def __contains__(self, source_link_id: int) -> bool:
        """
        See :py:meth:`is_link`
        """
        return self.is_link(source_link_id)

    def get_link(self, source_link_id: int) -> Optional[Link]:
        """
        Get the link with the given ID, or `None` if no such link.
        Also implemented as ``__getitem__(source_link_id)``

        :param source_link_id: The ID of the link to find
        :return: The link, or ``None`` if no such link
        """
        return self._links.get(source_link_id)

    def __getitem__(self, source_link_id: int) -> Optional[Link]:
        """
        See :py:meth:`get_link`
        """
        return self.get_link(source_link_id)

    @property
    def links(self) -> Iterator[Link]:
        """
        The available links of this router.
        """
        return iter(self._links.values())

    def __iter__(self) -> Iterator[Tuple[int, Link]]:
        """
        Get an iterable of source link IDs and links in the router.

        :return: an iterable of tuples of ``(source_link_id, link)`` where:
            * ``source_link_id`` is the ID of the link
            * ``link`` is a router link
        """
        return iter(self._links.items())

    def __len__(self) -> int:
        """
        Get the number of links in the router.

        :return: The length of the underlying iterable
        """
        return len(self._links)

    @property
    def n_available_multicast_entries(self) -> int:
        """
        The number of available multicast entries in the routing tables.
        """
        return self._n_available_multicast_entries

    @staticmethod
    def convert_routing_table_entry_to_spinnaker_route(
            routing_table_entry: Union[
                MulticastRoutingEntry, RoutingEntry]) -> int:
        """
        Convert a routing table entry represented in software to a
        binary routing table entry usable on the machine.

        :param routing_table_entry: The entry to convert
        """
        route_entry = 0
        for processor_id in routing_table_entry.processor_ids:
            if processor_id >= Router.MAX_CORES_PER_ROUTER or processor_id < 0:
                raise SpinnMachineInvalidParameterException(
                    "route.processor_ids",
                    str(routing_table_entry.processor_ids),
                    "Processor IDs must be between 0 and " +
                    str(Router.MAX_CORES_PER_ROUTER - 1))
            route_entry |= (1 << (Router.MAX_LINKS_PER_ROUTER + processor_id))
        for link_id in routing_table_entry.link_ids:
            if link_id >= Router.MAX_LINKS_PER_ROUTER or link_id < 0:
                raise SpinnMachineInvalidParameterException(
                    "route.link_ids", str(routing_table_entry.link_ids),
                    "Link IDs must be between 0 and " +
                    str(Router.MAX_LINKS_PER_ROUTER - 1))
            route_entry |= (1 << link_id)
        return route_entry

    @staticmethod
    def convert_spinnaker_route_to_routing_ids(route: int) -> Tuple[
            List[int], List[int]]:
        """
        Convert a binary routing table entry usable on the machine to lists of
        route IDs usable in a routing table entry represented in software.

        :param route: The routing table entry
        :return: The list of processor IDs, and the list of link IDs.
        """
        processor_ids = [pi for pi in range(0, Router.MAX_CORES_PER_ROUTER)
                         if route & 1 << (Router.MAX_LINKS_PER_ROUTER + pi)]
        link_ids = [li for li in range(0, Router.MAX_LINKS_PER_ROUTER)
                    if route & 1 << li]
        return processor_ids, link_ids

    def get_neighbouring_chips_coords(self) -> List[Dict[str, int]]:
        """
        Utility method to convert links into x and y coordinates.

        :return: iterable list of destination coordinates in x and y dict
        """
        return [
            {'x': link.destination_x, 'y': link.destination_y}
            for link in self.links]

    def __str__(self) -> str:
        return (
            f"[Router: "
            f"available_entries={self._n_available_multicast_entries}, "
            f"links={list(self._links.values())}]")

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def opposite(link_id: int) -> int:
        """
        Given a valid link_id this method returns its opposite.

        GIGO: this method assumes the input is valid.
        No verification is done

        :param link_id: A valid link_id
        :return: The link_id for the opposite direction
        """
        # Mod is faster than if
        return (link_id + Router.LINK_OPPOSITE) % Router.MAX_LINKS_PER_ROUTER
