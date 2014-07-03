from spinn_machine.exceptions import SpinnMachineInvalidParameterException

DEFAULT_SDRAM_BYTES = 128 * 1024 * 1024


class SDRAM(object):
    """ Represents the properties of the SDRAM of a chip in the machine
    """

    def __init__(self, size):
        """

        :param size: size of the SDRAM in bytes
        :type size: int
        :raise spinn_machine.exceptions.SpinnMachineInvalidParameterException:\
                    If the size is less than 0
        """
        if size < 0:
            raise SpinnMachineInvalidParameterException("size", size,
                    "Must not be less than 0")
        self._size = size

    @property
    def size(self):
        """ The size of SDRAM in bytes

        :return: The size of SDRAM in bytes
        :rtype: int
        :raise None: does not raise any known exceptions
        """
        return self._size
