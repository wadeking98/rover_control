#!/usr/bin/env python3
from socket import *
from threading import Thread
from pynput.keyboard import Key, Listener
import time
import sys



UDP_ADDR = ()
dir_dict = {Key.up:0b001, Key.down:0b010, Key.left: 0b011, Key.right: 0b100}
direction = 0b000
PORT = 5555

def connect():
    global UDP_ADDR
    csock.sendto("test1".encode(), UDP_ADDR)
    msg_enc, _ = csock.recvfrom(1024)
    print(msg_enc.decode())
    return

def command_send():
    """
    Thread to send rover control commands
    """
    while True:
        time.sleep(0.1)
        csock.sendto(bytes(direction),("192.168.4.1",PORT))
    pass

def frame_recv():
    print("got here")
    """
    Thread to receive incoming image frames from the rover
    """
    while True:
        msg_enc, _ = csock.recvfrom(1024)
        print(msg_enc)
    pass


def on_press(key):
    global direction
    try:
        direction = dir_dict[key]
    except:
        print("not a valid key")
        return
    print('{0} pressed'.format(
        key))

def on_release(key):
    global direction
    print('{0} release'.format(
        key))
    direction = 0b000
    if key == Key.esc:
        # Stop listener
        return False




if __name__ == "__main__":
    
    if len(sys.argv) < 3:
        print("Usage: python3 controller.py <rover_ip> <controller_ip>")
        exit(0)
   
    IP = sys.argv[2]

    csock = socket(AF_INET, SOCK_DGRAM)
    #controller will be sending and receiving so we need to bind
    csock.bind((IP, 5555))
    csock.setsockopt(SOL_SOCKET, SO_REUSEADDR,1)
    csock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    UDP_ADDR = (sys.argv[1],PORT)

    connthread = Thread(target=connect, name="conn_thread")
    cthread = Thread(target=command_send, name="command_thread")
    fthread = Thread(target=frame_recv, name="frame_thread")

    connthread.start()
    connthread.join()

    cthread.start()
    fthread.start()

    # Collect events until released
    with Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()
