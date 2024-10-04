from typing import Callable, Any
import random
import threading
import time

class Packet:
    seq = 0
    data = ""
    ACK = False
    NACK = False
    is_valid = True

    def __init__(self, seq, data, ACK=False, NACK=False):
        self.seq = seq
        self.data = data
        self.ACK = ACK
        self.NACK = NACK
    
    def __str__(self):
        return f"Packet(seq={self.seq}, data={self.data})"

class ACK(Packet):
    def __init__(self, seq):
        super().__init__(seq, data=None, ACK=True, NACK=False)

    def __str__(self):
        return f"ACK({self.seq})"

class NACK(Packet):
    def __init__(self, seq):
        super().__init__(seq, data=None, ACK=False, NACK=True)

    def __str__(self):
        return f"NACK({self.seq})"

def empty_fn(*args, **kargs):
    pass

class NetworkEventListener:
    protocol = None
    source = None

    def __init__(self, protocol, source):
        self.protocol = protocol
        self.source = source

    
    _on_sending_packet: Callable[['NetworkEventListener', Packet], None] = empty_fn
    _on_received_packet: Callable[['NetworkEventListener', Packet], None] = empty_fn
    _on_corrupted_packet: Callable[['NetworkEventListener', Packet], None] = empty_fn
    _on_out_of_order_packet: Callable[['NetworkEventListener', Packet], None] = empty_fn
    _on_timeout_retransmission: Callable[['NetworkEventListener', Packet], None] = empty_fn
    _on_refused_data: Callable[['NetworkEventListener', Any], None] = empty_fn


    def on_sending_packet(self, packet: Packet):
        self._on_sending_packet(self, packet)

    def on_received_packet(self, packet: Packet):
        self._on_received_packet(self, packet)

    def on_corrupted_packet(self, packet: Packet):
        self._on_corrupted_packet(self, packet)

    def on_out_of_order_packet(self, packet: Packet):
        self._on_out_of_order_packet(self, packet)

    def on_timeout_retransmission(self, packet: Packet):
        self._on_timeout_retransmission(self, packet)

    def on_refused_data(self, data):
        self._on_refused_data(self, data)


def get_probability() -> bool:
    number = random.randrange(0,100)
    
    # 40% success, 60% fail
    return number <= 40


timer_counter = 0

def run_timer(action):
    global timer_counter
    timer_counter+=1
    current_counter = timer_counter

    time.sleep(2)
    if (timer_counter == current_counter):
        action()


def start_timer(action):
    timer = threading.Thread(target=run_timer, args=(action,))
    timer.start()

def stop_timer():
    global timer_counter
    timer_counter+=1