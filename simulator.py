import argparse
from typing import List
from utils import Packet, NetworkEventListener
from gbn_sender import GBN_Sender
from gbn_receiver import GBN_Receiver
from sw_sender import SW_Sender
from sw_receiver import SW_Receiver
import time
import threading

class NetworkSimulator:

    transmission_delay = 0.2        # seconds
    protocol = None


    @classmethod
    def ask_data(self) -> List[str]:
       return ["HELLO", "BESTGROUP", "DING", "BA", "KQ", "RAM", "SUPERTEAM", "MAKARIT", "LUFFYSAN", "CANCELLED" ]
    

    @staticmethod
    def udt_send(dest: str, packet: Packet):
        def udt_send_thread(dest: str, packet: Packet):
            # Simulate transmission delay
            time.sleep(NetworkSimulator.transmission_delay)
            
            if not packet.is_valid:
                if packet.ACK: 
                    print(f"[Network] ACK corrupted: {packet}")
                elif packet.NACK: 
                    print(f"[Network] NACK corrupted: {packet}")

            # Send to dest
            
            if NetworkSimulator.protocol == "Go-Back-N":
                if dest == "receiver":
                    GBN_Receiver.rdt_rcv(packet)
                else:
                    GBN_Sender.rdt_rcv(packet)
            else:
                if dest == "receiver":
                    SW_Receiver.rdt_rcv(packet)
                else:
                    SW_Sender.rdt_rcv(packet)

        
        thread = threading.Thread(target=udt_send_thread, args=(dest, packet))
        thread.start()

    

    @classmethod
    def start_sw(self):
        self.protocol = "Stop-and-Wait"
        print(f"=== Testing Stop-and-Wait Protocol ===")
            
           
        # Initialize modules and listeners
        SW_Sender.base_udt_send = NetworkSimulator.udt_send
        SW_Sender.listener._on_sending_packet = NetworkSimulator.on_sending_packet
        SW_Sender.listener._on_received_packet = NetworkSimulator.on_received_packet
        SW_Sender.listener._on_corrupted_packet = NetworkSimulator.on_corrupted_packet
        SW_Sender.listener._on_timeout_retransmission = NetworkSimulator.on_timeout_retransmission
        SW_Sender.listener._on_refused_data = NetworkSimulator.on_refused_data

        SW_Receiver.base_udt_send = NetworkSimulator.udt_send
        SW_Receiver.listener._on_sending_packet = NetworkSimulator.on_sending_packet
        SW_Receiver.listener._on_received_packet = NetworkSimulator.on_received_packet
        SW_Receiver.listener._on_corrupted_packet = NetworkSimulator.on_corrupted_packet
        SW_Receiver.listener._on_out_of_order_packet = NetworkSimulator.on_out_of_order_packet

        data_arr = self.ask_data()
        send_period = 5 #seconds
         
        i = 0
        while i < len(data_arr):
            sent = SW_Sender.rdt_send(data_arr[i])
            time.sleep(send_period)

            if sent: i += 1

    @classmethod
    def start_gbn(self):
        self.protocol = "Go-Back-N"
        print(f"=== Testing Go-Back-N Protocol ===")
            
           
        # Initialize modules and listeners
        GBN_Sender.base_udt_send = NetworkSimulator.udt_send
        GBN_Sender.listener._on_sending_packet = NetworkSimulator.on_sending_packet
        GBN_Sender.listener._on_received_packet = NetworkSimulator.on_received_packet
        GBN_Sender.listener._on_corrupted_packet = NetworkSimulator.on_corrupted_packet
        GBN_Sender.listener._on_timeout_retransmission = NetworkSimulator.on_timeout_retransmission
        GBN_Sender.listener._on_refused_data = NetworkSimulator.on_refused_data

        GBN_Receiver.base_udt_send = NetworkSimulator.udt_send
        GBN_Receiver.listener._on_sending_packet = NetworkSimulator.on_sending_packet
        GBN_Receiver.listener._on_received_packet = NetworkSimulator.on_received_packet
        GBN_Receiver.listener._on_corrupted_packet = NetworkSimulator.on_corrupted_packet
        GBN_Receiver.listener._on_out_of_order_packet = NetworkSimulator.on_out_of_order_packet

        data_arr = self.ask_data()
        send_period = 3 #seconds
        
        i = 0
        while i < len(data_arr):
            sent = GBN_Sender.rdt_send(data_arr[i])
            time.sleep(send_period)

            if sent: i += 1



    ##################### Event Listeners #####################
    @staticmethod
    def on_sending_packet(listener: NetworkEventListener, packet: Packet):
        if not packet.ACK and not packet.NACK:
            print(f"[{listener.source}][{listener.protocol}] Sending: {packet}")

    @staticmethod
    def on_received_packet(listener: NetworkEventListener, packet: Packet):
        if listener.protocol == "Go-Back-N":
            if packet.ACK:
                print(f"[{listener.source}][{listener.protocol}] Received ACK: {packet}")
            elif packet.NACK:
                print(f"[{listener.source}][{listener.protocol}] Received NACK: {packet}.")
            else:
                print(f"[{listener.source}][{listener.protocol}] Received expected packet: {packet}. Sending ACK...")
        else:
            if packet.ACK:
                print(f"[{listener.source}][{listener.protocol}] Received ACK: {packet}. Moving to the next packet.")
            elif packet.NACK:
                print(f"[{listener.source}][{listener.protocol}] Received NACK: {packet}. Retransmitting...")
            else:
                print(f"[{listener.source}][{listener.protocol}] Received expected packet: {packet}. Sending ACK...")
    

    @staticmethod
    def on_corrupted_packet(listener: NetworkEventListener, packet: Packet):
        if listener.protocol == "Go-Back-N":
            if packet.ACK:
                print(f"[{listener.source}][{listener.protocol}] Received corrupted or wrong ACK: {packet}")
            elif packet.NACK:
                print(f"[{listener.source}][{listener.protocol}] Received corrupted or wrong NACK: {packet}")
            else:
                print(f"[Network] Packet corrupted: {packet}")
        else:
            if packet.ACK:
                print(f"[{listener.source}][{listener.protocol}] Received corrupted or wrong ACK: {packet}. Retransmitting...")
            elif packet.NACK:
                print(f"[{listener.source}][{listener.protocol}] Received corrupted or wrong NACK: {packet}. Retransmitting...")
            else:
                print(f"[Network] Packet corrupted: {packet}. Sending NACK...")

    @staticmethod
    def on_timeout_retransmission(listener: NetworkEventListener, packet: Packet):
        if not packet.ACK and not packet.NACK:
            print(f"[{listener.source}][{listener.protocol}] Timeout waiting for ACK. Retransmitting: {packet}")
    

    @staticmethod
    def on_refused_data(listener: NetworkEventListener, data):
        if listener.protocol == "Go-Back-N":
            print(f"[{listener.source}][{listener.protocol}] Refused data due to full window. Buffered: {data}")
        else: 
            print(f"[{listener.source}][{listener.protocol}] Refused data while waiting for ACK/NACK. Returned: {data}")

    @staticmethod
    def on_out_of_order_packet(listener: NetworkEventListener, packet: Packet):
        print(f"[{listener.source}][{listener.protocol}] Received out-of-order packet: {packet}")
    

def main():
    parser = argparse.ArgumentParser(description="Simulate Stop-and-Wait or Go-Back-N protocols.")
    parser.add_argument("protocol", type=str, choices=[ "sw", "gbn" ], help="The protocol to simulate.")
    protocol = parser.parse_args().protocol

    if protocol == "sw":
        NetworkSimulator.start_sw()
    elif protocol == "gbn":
        NetworkSimulator.start_gbn()


if __name__ == "__main__":
    main()
    