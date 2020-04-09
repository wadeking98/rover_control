#!/usr/bin/env python3
from socket import *
from threading import Thread
import sys
import time
#from picamera import PiCamera




def command_recv():
    while True:
        msg_enc, _ = rsock.recvfrom(1024)
        print(msg_enc)
    pass

def frame_send():
    while True:
        time.sleep(0.1)
        rsock.sendto(bytes(0b1111),("255.255.255.255", 5555))
    pass

if __name__ == "__main__":
    IP = gethostbyname(gethostname())
    if len(sys.argv) >= 2 and sys.argv[1] =="test":
        IP = "10.0.0.2"

    rsock = socket(AF_INET, SOCK_DGRAM)
    #rover will be sending and receiving so we need to bind
    rsock.bind((IP, 5555))
    rsock.setsockopt(SOL_SOCKET, SO_REUSEADDR,1)
    rsock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    cthread = Thread(target=command_recv, name="command_thread")
    fthread = Thread(target=frame_send, name="frame_thread")

    cthread.start()
    fthread.start()