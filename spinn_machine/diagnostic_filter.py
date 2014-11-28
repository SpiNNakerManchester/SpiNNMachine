import math
from spinnman.data.little_endian_byte_array_byte_reader \
    import LittleEndianByteArrayByteReader


class DiagnosticFilter(object):

    def __init__(
            self, counter_interrupt_active, enable_interrupt_on_counter_event,
            counter_event_has_occured, packet_dest, packet_source,
            if_contains_payload, type_of_router_behaviour,
            emergency_routing_mode, emergency_routing_field, packet_type):

        self._counter_interrupt_active = counter_interrupt_active
        self._enable_interrupt_on_counter_event = \
            enable_interrupt_on_counter_event
        self._counter_event_has_occured = counter_event_has_occured
        self._packet_dest = packet_dest
        self._packet_source = packet_source
        self._if_contains_payload = if_contains_payload
        self._type_of_router_behaviour = type_of_router_behaviour
        self._emergency_routing_mode = emergency_routing_mode
        self._emergency_routing_field = emergency_routing_field
        self._packet_type = packet_type

    @property
    def counter_interrupt_active(self):
        return self._counter_interrupt_active

    @property
    def enable_interrupt_on_counter_event(self):
        return self._enable_interrupt_on_counter_event

    @property
    def counter_event_has_occured(self):
        return self._counter_event_has_occured

    @property
    def packet_dest(self):
        return self._packet_dest

    @property
    def packet_source(self):
        return self._packet_source

    @property
    def if_contains_payload(self):
        return self._if_contains_payload

    @property
    def type_of_router_behaviour(self):
        return self._type_of_router_behaviour

    @property
    def emergency_routing_mode(self):
        return self._emergency_routing_mode

    @property
    def emergency_routing_field(self):
        return self._emergency_routing_field

    @property
    def packet_type(self):
        return self._packet_type

    def create_byte_array_from_filter(self):
        writer = LittleEndianByteArrayByteReader()
        data = (self._counter_interrupt_active << 31 +
                self.enable_interrupt_on_counter_event << 30 +
                self._counter_event_has_occured << 29 +
                self.packet_dest << 16 + self._packet_source << 14 +
                self._if_contains_payload << 12 +
                self._emergency_routing_mode << 8 +
                self._emergency_routing_field << 4 + self._packet_type)
        writer.write_int(data)
        return writer.data

    @staticmethod
    def create_dianostic_filter_from_byte_array_reader(reader):
        int_value = reader.read_int()
        counter_interrupt_active = int_value >> 31
        enable_interrupt_on_counter_event = int_value >> 30 & 1
        counter_event_has_occured = int_value >> 29 & 1
        packet_dest = (int_value >> 16) & math.pow(2, 8)
        packet_source = (int_value >> 14) & math.pow(2, 2)
        if_contains_payload = (int_value >> 12) & math.pow(2, 2)
        type_of_router_behaviour = (int_value >> 10) & math.pow(2, 2)
        emergency_routing_mode = (int_value >> 8) & 1
        emergency_routing_field = (int_value >> 4) & math.pow(2, 4)
        packet_type = int_value & math.pow(2, 4)
        return DiagnosticFilter(
            counter_interrupt_active, enable_interrupt_on_counter_event,
            counter_event_has_occured, packet_dest, packet_source,
            if_contains_payload, type_of_router_behaviour,
            emergency_routing_mode, emergency_routing_field, packet_type)