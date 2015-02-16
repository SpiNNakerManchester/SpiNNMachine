from spinnman import constants
from spinnman import exceptions


class AbstractIPTAG(object):

    def __init__(self, port, tag):
        self._port = port
        self._tag = tag
        self._check_port_nums_from_defaults()

    @property
    def port(self):
        """ Return the port of the tag
        """
        return self._port

    @property
    def tag(self):
        """ Return the tag of the packet
        """
        return self._tag

    def _check_port_nums_from_defaults(self):
        if (self._port == constants.SCP_SCAMP_PORT or
                self._port == constants.UDP_BOOT_CONNECTION_DEFAULT_PORT):
            raise exceptions.SpinnmanInvalidParameterException(
                "port", str(self._port),
                "The port number speicified is one that is already used by "
                "either the boot or spinn api listener. therefore cannot be "
                "used as a port number to a tags or reverse tags")

