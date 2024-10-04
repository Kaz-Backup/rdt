from typing import Callable
from utils import Packet, ACK, NACK, NetworkEventListener, empty_fn, get_probability


class SW_Receiver:

    listener = NetworkEventListener(protocol="Stop-and-Wait", source="Receiver")
    base_udt_send: Callable[[str, Packet], None] = empty_fn

    last_received = None
    seqnum = 0

    @classmethod
    def udt_send(self, packet):
        # Probability for corrupted packet (60% chance corrupted)
        packet.is_valid = get_probability()

        # Probability for lost packet (60% chance lost)
        if not get_probability():
            return
        
        self.base_udt_send("sender", packet)

    @classmethod
    def rdt_rcv(self, packet: Packet) -> bool:
        # Check if not in-order
        if packet.seq != self.seqnum:
            self.listener.on_out_of_order_packet(packet)
            
            if self.last_received:
                self.udt_send(ACK(self.last_received.seq))

            return

        # Check if corrupted. If yes, send NACK
        if not packet.is_valid: 
            self.listener.on_corrupted_packet(packet)

            nack = NACK(self.seqnum)
            self.udt_send(nack)
            return
        
        self.last_received = packet
        self.listener.on_received_packet(packet)

        # Send ACK
        ack = ACK(self.seqnum)
        self.udt_send(ack)
        
        # Toggle sequence number
        self.seqnum = 1 if self.seqnum == 0 else 0