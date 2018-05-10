from .exceptions import SpinnMachineAlreadyExistsException


class FixedRouteEntry(object):
    """ Describes an entry in a SpiNNaker chip's fixed route routing table.
    """

    __slots__ = (

        # the processors ids for this route
        "_processor_ids",

        # the link ids for this route
        "_link_ids"
    )

    def __init__(self, processor_ids, link_ids):
        # Add processor ids, checking that there is only one of each
        self._processor_ids = set()
        for processor_id in processor_ids:
            if processor_id in self._processor_ids:
                raise SpinnMachineAlreadyExistsException(
                    "processor id", str(processor_id))
            self._processor_ids.add(processor_id)

        # Add link ids, checking that there is only one of each
        self._link_ids = set()
        for link_id in link_ids:
            if link_id in self._link_ids:
                raise SpinnMachineAlreadyExistsException(
                    "link id", str(link_id))
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
