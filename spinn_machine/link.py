from spinn_machine.exceptions import SpinnMachineAlreadyExistsException
from enum import Enum

class Link(object):
    """ Represents a directional link between chips in the machine
    """
    
    def __init__(self, source_x, source_y, source_link_id, destination_x,
                 destination_y, multicast_default_from, multicast_default_to):
        """
        
        :param source_x: The x-coordinate of the source chip of the link
        :type source_x: int
        :param source_y: The y-coordinate of the source chip of the link
        :type source_y: int
        :param source_link_id: The id of the link in the source chip
        :type source_link_id: int
        :param destination_x: The x-coordinate of the destination chip of the\
                    link
        :type destination_x: int
        :param destination_y: The y-coordinate of the destination chip of the\
                    link
        :type destination_y: int
        :param multicast_default_from: Traffic received on the link identified\
                    by multicast_default_from will be sent to the link herein\
                    defined if no entry is present in the multicast routing\
                    table.  On SpiNNaker chips, multicast_default_from is\
                    usually the same as multicast_default_to.  None if no\
                    such default exists, or the link does not exist.
        :type multicast_default_from: int
        :param multicast_default_to: Traffic received on the link herein\
                    defined will be sent to the link identified by\
                    multicast_default_from if no entry is present in the\
                    multicast routing table.  On SpiNNaker chips,\
                    multicast_default_to is usually the same as\
                    multicast_default_from.  None if no such link exists, or\
                    the link does not exist.
        :type multicast_default_to: int
        :raise None: No known exceptions are raised
        """
        self._source_x = source_x
        self._source_y = source_y
        self._source_link_id = source_link_id
        self._destination_x = destination_x
        self._destination_y = destination_y
        self._multicast_default_from = multicast_default_from
        self._multicast_default_to = multicast_default_to
    
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
        """ The id of the link on the source chip
        
        :return: The link id
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
    
    @property
    def multicast_default_from(self):
        """ The id of the link for which this link is the default
        
        :return: The id of a link, or None if no such link
        :rtype: int
        """
        return self._multicast_default_from
    
    @multicast_default_from.setter
    def multicast_default_from(self, multicast_default_from):
        """ Sets the id of the link for which this link is the default,\
            if not already set
            
        :param multicast_default_from: The id of a link
        :type multicast_default_from: int
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: If\
                    a value has already been set
        """
        if self._multicast_default_from is not None:
            raise SpinnMachineAlreadyExistsException(
                "multicast_default_from", str(self._multicast_default_from))
        self._multicast_default_from = multicast_default_from
    
    @property
    def multicast_default_to(self):
        """ The id of the link to which to send default routed multicast
        
        :return: The id of a link, or None if no such link
        :rtype: int
        """
        return self._multicast_default_to
    
    @multicast_default_to.setter
    def multicast_default_to(self, multicast_default_to):
        """ Sets the id of the link to which to send default routed multicast
            
        :param multicast_default_to: The id of a link
        :type multicast_default_to: int
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: If\
                    a value has already been set
        """
        if self._multicast_default_to is not None:
            raise SpinnMachineAlreadyExistsException(
                "multicast_default_to", str(self._multicast_default_to))
        self._multicast_default_to = multicast_default_to
    
    def __str__(self):
        return ("[Link: source_x={}, source_y={}, source_link_id={},"
                " destination_x={}, destination_y={}, default_from={},"
                " default_to={}]".format(self._source_x, self._source_y,
                                         self._source_link_id,
                                         self._destination_x,
                                         self._destination_y,
                                         self._multicast_default_from,
                                         self._multicast_default_to))
    
    def __repr__(self):
        return self.__str__()
