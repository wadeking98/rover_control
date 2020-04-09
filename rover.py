#!/usr/bin/env python3
from socket import socket, AF_INET, SOCK_DGRAM, gethostname, gethostbyname
from threading import Thread
from pynput.keyboard import Key, Listener
import sys
import time
#from picamera import PiCamera

dir_dict = {Key.up:0b001, Key.down:0b010, Key.left: 0b011, Key.right: 0b100}



def command_recv():
    while True:
        msg_enc, _ = rsock.recvfrom(1024)
        print(msg_enc)
    pass

def frame_send():
    while True:
        time.sleep(0.1)
        rsock.sendto(bytes(0b1111),("10.0.0.1", 5555))
    pass

if __name__ == "__main__":
    IP = gethostbyname(gethostname())
    if len(sys.argv) >= 2 and sys.argv[1] =="test":
        IP = "10.0.0.2"

    rsock = socket(AF_INET, SOCK_DGRAM)
    #rover will be sending and receiving so we need to bind
    rsock.bind((IP, 5555))

    cthread = Thread(target=command_recv, name="command_thread")
    fthread = Thread(target=frame_send, name="frame_thread")

    cthread.start()
    fthread.start()