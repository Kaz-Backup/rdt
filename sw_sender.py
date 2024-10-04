from typing import Callable
from utils import Packet, NetworkEventListener, get_probability, empty_fn, start_timer, stop_timer


class SW_Sender:

    listener = NetworkEventListener(protocol="Stop-and-Wait", source="Sender")
    base_udt_send: Callable[[str, Packet], None] = empty_fn

    seqnum = 0
    waiting = False
    packet_list = [ None, None ]


    @classmethod
    def udt_send(self, packet):
        # Probability for corrupted packet (60% chance corrupted)
        packet.is_valid = get_probability()

        # Probability for lost packet (60% chance lost)
        if not get_probability():
            return
        
        self.base_udt_send("receiver", packet)

    @classmethod
    def timeout_retransmit(self):
        start_timer(self.timeout_retransmit)
        
        packet = self.packet_list[self.seqnum]
        self.listener.on_timeout_retransmission(packet)
        self.udt_send(packet)

    @classmethod 
    def rdt_send(self, data) -> bool:
        if self.waiting:
            self.listener.on_refused_data(data)
            return False
        
        packet = Packet(self.seqnum, data)
        self.packet_list[packet.seq] = packet
         
        start_timer(self.timeout_retransmit)

        self.listener.on_sending_packet(packet)
        self.udt_send(packet)
        self.waiting = True

        return True
    
    @classmethod
    def rdt_rcv(self, packet: Packet) -> bool:
        # Check if corrupted
        if not packet.is_valid: 
            self.listener.on_corrupted_packet(packet)
            return

        stop_timer()
        self.listener.on_received_packet(packet)

        
        # Check if NACK. If yes, retransmit
        if packet.NACK:
            packet = self.packet_list[self.seqnum]
            self.udt_send(packet)
            start_timer(self.timeout_retransmit)
            return

        self.waiting = False
        
        # Toggle sequence number
        self.seqnum = 1 if self.seqnum == 0 else 0 