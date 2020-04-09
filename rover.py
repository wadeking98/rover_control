#!/usr/bin/env python3
from socket import *
from threading import Thread
import sys
import time
#from picamera import PiCamera

CON_ADDR = ()

def connect():
    global CON_ADDR
    msg_enc, addr = rsock.recvfrom(1024)
    CON_ADDR = addr
    rsock.sendto("test".encode(), addr)
    print(addr)
    return


def command_recv():
    while True:
        msg_enc, _ = rsock.recvfrom(1024)
        print(msg_enc)
    pass

def frame_send():
    while True:
        time.sleep(0.1)
        rsock.sendto(bytes(0b1111),("255.255.255.255", 5554))
    pass

if __name__ == "__main__":
    IP = gethostbyname(gethostname())
    if len(sys.argv) >= 2 and sys.argv[1] =="test":
        IP = "192.168.4.1"

    rsock = socket(AF_INET, SOCK_DGRAM)
    #rover will be sending and receiving so we need to bind
    rsock.bind((IP, 5555))
    # rsock.setsockopt(SOL_SOCKET, SO_REUSEADDR,1)
    # rsock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    connthread = Thread(target=connect, name="conn_thread")
    cthread = Thread(target=command_recv, name="command_thread")
    fthread = Thread(target=frame_send, name="frame_thread")

    connthread.start()
    connthread.join()
    # cthread.start()
    # fthread.start()