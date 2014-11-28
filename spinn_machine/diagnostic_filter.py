import math
from spinnman.data.little_endian_byte_array_byte_reader \
    import LittleEndianByteArrayByteReader

class DiagnosticFilter(object):

    def __init__(
            self, counter_interrupt_active, enable_interrupt_on_counter_event,
            counter_event_has_occured, is_local_packet_source,
            is_not_local_packet_source, if_contains_payload,
            if_not_contain_payload, is_default_routed, is_not_default_routed,
            emergency_routing_mode, emergency_routing_field_0_is_set,
            emergency_routing_field_1_is_set,  emergency_routing_field_2_is_set,
            emergency_routing_field_3_is_set, packet_type_fr_enabled,
            packet_type_nn_enabled, packet_type_p2p_enabled,
            packet_type_mc_enabled, packet_dest_is_link0, packet_dest_is_link1,
            packet_dest_is_link2, packet_dest_is_link3, packet_dest_is_link_4,
            packet_dest_is_link_5, packet_dest_is_monitor_core,
            packet_dest_is_local_not_monitor, packet_dest_is_dumped
    ):


        self._counter_interrupt_active = int(counter_interrupt_active)
        self._enable_interrupt_on_counter_event = \
            int(enable_interrupt_on_counter_event)
        self._counter_event_has_occured = int(counter_event_has_occured)
        self._packet_dest = packet_dest
        self._is_local_packet_source = int(is_local_packet_source)
        self._if_not_contain_payload = int(if_not_contain_payload)
        self._is_not_default_routed = int(is_not_default_routed)
        self._if_contains_payload = int(if_contains_payload)
        self._is_not_local_packet_source = int(is_not_local_packet_source)
        self._is_defaulted_routed = int(is_default_routed)
        self._emergency_routing_mode = int(emergency_routing_mode)
        self._emergency_routing_field = emergency_routing_field
        self._packet_type_fr_enabled = int(packet_type_fr_enabled)
        self._packet_type_nn_enabled = int(packet_type_nn_enabled)
        self._packet_type_p2p_enabled = int(packet_type_p2p_enabled)
        self._packet_type_mc_enabled = int(packet_type_mc_enabled)

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
        return self._is_local_packet_source

    @property
    def if_contains_payload(self):
        return self._if_contains_payload

    @property
    def type_of_router_behaviour(self):
        return self._is_defaulted_routed

    @property
    def emergency_routing_mode(self):
        return self._emergency_routing_mode

    @property
    def emergency_routing_field(self):
        return self._emergency_routing_field

    @property
    def packet_type_fr_enabled(self):
        return self._packet_type_fr_enabled

    @property
    def packet_type_nn_enabled(self):
        return self._packet_type_nn_enabled

    @property
    def packet_type_p2p_enabled(self):
        return self._packet_type_p2p_enabled

    @property
    def packet_type_mc_enabled(self):
        return self._packet_type_mc_enabled

    def create_byte_array_from_filter(self):
        writer = LittleEndianByteArrayByteReader()
        data = (self._counter_interrupt_active << 31 +
                self.enable_interrupt_on_counter_event << 30 +
                self._counter_event_has_occured << 29 +
                self.packet_dest << 16 + self._is_local_packet_source << 14 +
                self._if_contains_payload << 12 +
                self._emergency_routing_mode << 8 +
                self._emergency_routing_field << 4 +
                self._packet_type_fr_enabled << 3 +
                self._packet_type_nn_enabled << 2 +
                self._packet_type_p2p_enabled << 1 +
                self._packet_type_mc_enabled)
        writer.write_int(data)
        return writer.data

    @staticmethod
    def create_dianostic_filter_from_byte_array_reader(reader):
        int_value = reader.read_int()
        counter_interrupt_active = int_value >> 31
        enable_interrupt_on_counter_event = int_value >> 30 & 1
        counter_event_has_occured = int_value >> 29 & 1
        packet_dest = (int_value >> 16) & int(math.pow(2, 8)) - 1
        packet_source = (int_value >> 14) & int(math.pow(2, 2)) - 1
        if_contains_payload = (int_value >> 12) & int(math.pow(2, 2)) - 1
        type_of_router_behaviour = (int_value >> 10) & int(math.pow(2, 2)) - 1
        emergency_routing_mode = (int_value >> 8) & 1
        emergency_routing_field = (int_value >> 4) & int(math.pow(2, 4)) - 1
        packet_type_fr_enabled = (int_value >> 3) & 1
        packet_type_nn_enabled = (int_value >> 2) & 1
        packet_type_p2p_enabled = (int_value >> 1) & 1
        packet_type_mc_enabled = int_value & 1

        return DiagnosticFilter(
            counter_interrupt_active, enable_interrupt_on_counter_event,
            counter_event_has_occured, packet_dest, packet_source,
            if_contains_payload, type_of_router_behaviour,
            emergency_routing_mode, emergency_routing_field,
            packet_type_fr_enabled, packet_type_nn_enabled,
            packet_type_p2p_enabled, packet_type_mc_enabled)