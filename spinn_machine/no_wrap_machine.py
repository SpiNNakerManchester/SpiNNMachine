from .machine import Machine


class NoWrapMachine(Machine):
    def __init__(self, chips, boot_x, boot_y):
        super(NoWrapMachine, self).__init__(chips, boot_x, boot_y)
