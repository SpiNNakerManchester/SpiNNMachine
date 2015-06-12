from spinn_machine.exceptions import SpinnMachineInvalidParameterException


class SDRAM(object):
    """ Represents the properties of the SDRAM of a chip in the machine
    """
    DEFAULT_SDRAM_BYTES = 128 * 1024 * 1024

    def __init__(self, size=DEFAULT_SDRAM_BYTES):
        """

        :param size: size of the SDRAM in bytes
        :type size: int
        :raise spinn_machine.exceptions.SpinnMachineInvalidParameterException:\
                    If the size is less than 0
        """
        if size < 0:
            raise SpinnMachineInvalidParameterException(
                "size", str(size), "Must not be less than 0")
        self._size = size

    @property
    def size(self):
        """ The size of SDRAM in bytes

        :return: The size of SDRAM in bytes
        :rtype: int
        :raise None: does not raise any known exceptions
        """
        return self._size
    
    def __str__(self):
        return "{} MB".format(self._size / (1024 * 1024))
    
    def __repr__(self):
        return self.__str__()
