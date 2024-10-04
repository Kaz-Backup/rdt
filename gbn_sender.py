from typing import Callable
from utils import NetworkEventListener, Packet, start_timer, stop_timer, empty_fn, get_probability

class GBN_Sender:
    N = 5
    nextseqnum = 1
    base = 1
    packet_list = [ None ] * 100

    listener = NetworkEventListener(protocol="Go-Back-N", source="Sender")
    base_udt_send: Callable[[str, Packet], None] = empty_fn

    @classmethod
    def udt_send(self, packet):
        # Probability for corrupted packet (60% chance corrupted)
        packet.is_valid = get_probability()

        # Probability for lost packet (60% chance lost)
        if not get_probability():
            return
        
        self.base_udt_send("receiver", packet)

    @classmethod
    def refuse_data(self, data):
        self.listener.on_refused_data(data)

    @classmethod
    def retransmit(self):
        start_timer(self.retransmit)
        for i in range(self.base-1, self.nextseqnum-1):
            packet = self.packet_list[i]
            self.listener.on_timeout_retransmission(packet)
            self.udt_send(packet)

    @classmethod
    def rdt_send(self, data) -> bool:    
        if self.nextseqnum < self.base+self.N:
            packet = Packet(self.nextseqnum, data)
            self.packet_list[packet.seq-1] = packet

            if self.base == self.nextseqnum:
                start_timer(self.retransmit)
            
            self.nextseqnum += 1    
            self.listener.on_sending_packet(packet)
            self.udt_send(packet)

            return True
        else:
            self.refuse_data(data)
            return False

    @classmethod
    def rdt_rcv(self, packet: Packet):

        # Check if corrupted
        if not packet.is_valid: 
            self.listener.on_corrupted_packet(packet)
            return
        
        self.listener.on_received_packet(packet)
        self.base = packet.seq + 1
        if self.base == self.nextseqnum:
            stop_timer()
        else:
            start_timer(self.retransmit)