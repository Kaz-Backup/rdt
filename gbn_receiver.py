from typing import Callable
from utils import Packet, ACK, NetworkEventListener, get_probability

class GBN_Receiver:
    expectedseqnum = 1

    listener = NetworkEventListener(protocol="Go-Back-N", source="Receiver")
    base_udt_send: Callable[[Packet], None] = None
    
    @classmethod
    def udt_send(self, packet: Packet):
        # Probability for corrupted packet (60% chance corrupted)
        packet.is_valid = get_probability()

        # Probability for lost packet (60% chance lost)
        if not get_probability():
            return
        
        self.base_udt_send("sender", packet)

    @classmethod
    def rdt_rcv(self,rcvpkt: Packet):

        # Check if corrupted
        if not rcvpkt.is_valid: 
            self.listener.on_corrupted_packet(rcvpkt)
            return

        # Check if not in-order
        if rcvpkt.seq != self.expectedseqnum:
            self.listener.on_out_of_order_packet(rcvpkt)

            # When out of order, resend an ACK for the last received packet
            sndpkt = ACK(self.expectedseqnum-1)
            self.listener.on_sending_packet(sndpkt)
            self.udt_send(sndpkt)

            return

        self.listener.on_received_packet(rcvpkt)
        self.extract(rcvpkt,rcvpkt.data)
        self.deliver_data(rcvpkt.data)
        
        # Send ACK
        sndpkt = ACK(self.expectedseqnum)
        self.listener.on_sending_packet(sndpkt)
        self.expectedseqnum += 1
        self.udt_send(sndpkt)
    
    @classmethod
    def extract(self,packet,data):
        pass
        # print(f"Extracting: {packet}, data = {data}")

    
    @classmethod
    def deliver_data(self,data):
        pass
        # print(f"Delivering Data: {data}")
