"""
a Link in a SpiNNaker machine
"""
from .exceptions import SpinnMachineAlreadyExistsException


class Link(object):
    """ Represents a directional link between SpiNNaker chips in the machine
    """

    __slots__ = (
        "_destination_x", "_destination_y", "_source_link_id", "_source_x",
        "_source_y"
    )

    # pylint: disable=too-many-arguments
    def __init__(self, source_x, source_y, source_link_id, destination_x,
                 destination_y):
        """
        :param source_x: The x-coordinate of the source chip of the link
        :type source_x: int
        :param source_y: The y-coordinate of the source chip of the link
        :type source_y: int
        :param source_link_id: The ID of the link in the source chip
        :type source_link_id: int
        :param destination_x: \
            The x-coordinate of the destination chip of the link
        :type destination_x: int
        :param destination_y: \
            The y-coordinate of the destination chip of the link
        :type destination_y: int
        :raise None: No known exceptions are raised
        """
        self._source_x = source_x
        self._source_y = source_y
        self._source_link_id = source_link_id
        self._destination_x = destination_x
        self._destination_y = destination_y

    @property
    def source_x(self):
        """ The x-coordinate of the source chip of this link

        :return: The x-coordinate
        :rtype: int
        """
        return self._source_x

    @property
    def source_y(self):
        """ The y-coordinate of the source chip of this link

        :return: The y-coordinate
        :rtype: int
        """
        return self._source_y

    @property
    def source_link_id(self):
        """ The ID of the link on the source chip

        :return: The link ID
        :rtype: int
        """
        return self._source_link_id

    @property
    def destination_x(self):
        """ The x-coordinate of the destination chip of this link

        :return: The x-coordinate
        :rtype: int
        """
        return self._destination_x

    @property
    def destination_y(self):
        """ The y-coordinate of the destination chip of this link

        :return: The y-coordinate
        :rtype: int
        """
        return self._destination_y

    __REPR_TEMPLATE = ("[Link: source_x={}, source_y={}, source_link_id={}, "
                       "destination_x={}, destination_y={}]")

    def __str__(self):
        return self.__REPR_TEMPLATE.format(
            self._source_x, self._source_y, self._source_link_id,
            self._destination_x, self._destination_y)

    def __repr__(self):
        return self.__str__()
