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

from collections import OrderedDict
from six import iteritems, itervalues
from .exceptions import (
    SpinnMachineAlreadyExistsException, SpinnMachineInvalidParameterException)


class Router(object):
    """ Represents a router of a chip, with a set of available links.\
        The router is iterable over the links, providing (source_link_id,\
        link) where:

            * source_link_id is the ID of a link
            * link is the link with ID source_link_id
    """

    ROUTER_DEFAULT_AVAILABLE_ENTRIES = 1024

    # The maximum number of links/directions a router can handle
    MAX_LINKS_PER_ROUTER = 6

    # Number to add or sub from a link to get its opposite
    LINK_OPPOSITE = 3

    MAX_CORES_PER_ROUTER = 18

    __slots__ = (
        "_emergency_routing_enabled", "_links",
        "_n_available_multicast_entries"
    )

    def __init__(
            self, links, emergency_routing_enabled=False,
            n_available_multicast_entries=ROUTER_DEFAULT_AVAILABLE_ENTRIES):
        """
        :param links: iterable of links
        :type links: iterable(:py:class:`~spinn_machine.Link`)
        :param emergency_routing_enabled: \
            Determines if the router emergency routing is operating
        :type emergency_routing_enabled: bool
        :param n_available_multicast_entries: \
            The number of entries available in the routing table
        :type n_available_multicast_entries: int
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: \
            If any two links have the same source_link_id
        """
        self._links = OrderedDict()
        for link in links:
            self.add_link(link)

        self._emergency_routing_enabled = emergency_routing_enabled
        self._n_available_multicast_entries = n_available_multicast_entries

    def add_link(self, link):
        """ Add a link to the router of the chip

        :param link: The link to be added
        :type link: :py:class:`spinn_machine.Link`
        :return: Nothing is returned
        :rtype: None
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: \
            If another link already exists with the same source_link_id
        """
        if link.source_link_id in self._links:
            raise SpinnMachineAlreadyExistsException(
                "link", str(link.source_link_id))
        self._links[link.source_link_id] = link

    def is_link(self, source_link_id):
        """ Determine if there is a link with ID source_link_id.\
            Also implemented as `__contains__(source_link_id)`

        :param source_link_id: The ID of the link to find
        :type source_link_id: int
        :return: True if there is a link with the given ID, False otherwise
        :rtype: bool
        :raise None: No known exceptions are raised
        """
        return source_link_id in self._links

    def __contains__(self, source_link_id):
        """ See :py:meth:`is_link`
        """
        return self.is_link(source_link_id)

    def get_link(self, source_link_id):
        """ Get the link with the given ID, or None if no such link.\
            Also implemented as `__getitem__(source_link_id)`

        :param source_link_id: The ID of the link to find
        :type source_link_id: int
        :return: The link, or None if no such link
        :rtype: :py:class:`~spinn_machine.Link`
        :raise None: No known exceptions are raised
        """
        if source_link_id in self._links:
            return self._links[source_link_id]
        return None

    def __getitem__(self, source_link_id):
        """ See :py:meth:`get_link`
        """
        return self.get_link(source_link_id)

    @property
    def links(self):
        """ The available links of this router

        :return: an iterable of available links
        :rtype: iterable(:py:class:`~spinn_machine.Link`)
        :raise None: does not raise any known exceptions
        """
        return itervalues(self._links)

    def __iter__(self):
        """ Get an iterable of source link IDs and links in the router

        :return: an iterable of tuples of (source_link_id, link) where:
            * source_link_id is the ID of the link
            * link is a router link
        :rtype: iterable(int, :py:class:`~spinn_machine.Link`)
        :raise None: does not raise any known exceptions
        """
        return iteritems(self._links)

    def __len__(self):
        """ Get the number of links in the router

        :return: The length of the underlying iterable
        :rtype: int
        """
        return len(self._links)

    @property
    def emergency_routing_enabled(self):
        """ Indicator of whether emergency routing is enabled

        :return: True if emergency routing is enabled, False otherwise
        :rtype: bool
        :raise None: does not raise any known exceptions
        """
        return self._emergency_routing_enabled

    @property
    def n_available_multicast_entries(self):
        """ The number of available multicast entries in the routing tables

        :return: The number of available entries
        :rtype: int
        :raise None: does not raise any known exceptions
        """
        return self._n_available_multicast_entries

    @staticmethod
    def convert_routing_table_entry_to_spinnaker_route(routing_table_entry):
        """ Convert a routing table entry represented in software to a\
            binary routing table entry usable on the machine

        :param routing_table_entry: The entry to convert
        :type routing_table_entry:\
            :py:class:`~spinn_machine.MulticastRoutingEntry`
        :rtype: int
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
    def convert_spinnaker_route_to_routing_ids(route):
        """ Convert a binary routing table entry usable on the machine to \
            lists of route IDs usable in a routing table entry represented in \
            software.

        :param route: The routing table entry
        :type route: int
        :return: The list of processor IDs, and the list of link IDs.
        :rtype: tuple(list(int), list(int))
        """
        processor_ids = [pi for pi in range(0, Router.MAX_CORES_PER_ROUTER)
                         if route & 1 << (Router.MAX_LINKS_PER_ROUTER + pi)]
        link_ids = [li for li in range(0, Router.MAX_LINKS_PER_ROUTER)
                    if route & 1 << li]
        return processor_ids, link_ids

    def get_neighbouring_chips_coords(self):
        """ Utility method to convert links into x and y coordinates

        :return: iterable list of destination coordinates in x and y dict
        :rtype: iterable(dict(str,int))

        """
        next_hop_chips_coords = list()
        for link in self.links:
            next_hop_chips_coords.append(
                {'x': link.destination_x, 'y': link.destination_y})
        return next_hop_chips_coords

    def __str__(self):
        return (
            "[Router: emergency_routing={}, "
            "available_entries={}, links={}]".format(
                self._emergency_routing_enabled,
                self._n_available_multicast_entries,
                list(self._links.values())))

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def opposite(link_id):
        """
        Given a valid link_id this method returns its opposite.

        GIGO: this method assumes the input is valid.
        No verfication is done

        :param link_id: A valid link_id
        :return: The link_id for the opposite direction
        """
        # Mod is faster than if
        return (link_id + Router.LINK_OPPOSITE) % Router.MAX_LINKS_PER_ROUTER
