class AbstractTag(object):

    def __init__(self, port, tag):
        self._port = port
        self._tag = tag

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
