
class SDRAM(object):
    """ Represents the properties of the SDRAM of a chip in the machine
    """

    DEFAULT_SDRAM_BYTES = 117 * 1024 * 1024

    def __init__(self, size=DEFAULT_SDRAM_BYTES):
        """
        :param free_size: the space available in SDRAM
        :type size: int
        """
        self._size = size

    @property
    def size(self):
        """ The SDRAM available for user applications

        :return: The space available in bytes
        :rtype: int
        """
        return self._size

    def __str__(self):
        return "{} MB".format(self._size / (1024 * 1024))

    def __repr__(self):
        return self.__str__()
