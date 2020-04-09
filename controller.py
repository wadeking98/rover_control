#!/usr/bin/env python3
from socket import socket, AF_INET, SOCK_DGRAM, gethostname
from threading import Thread
from pynput.keyboard import Key, Listener
import time
import sys

csock = socket(AF_INET, SOCK_DGRAM)
#controller will be sending and receiving so we need to bind
csock.bind(("10.0.0.1", 5555))

UDP_ADDR = ()
dir_dict = {Key.up:0b001, Key.down:0b010, Key.left: 0b011, Key.right: 0b100}
direction = 0b000

def command_send():
    """
    Thread to send rover control commands
    """
    while True:
        time.sleep(0.1)
        csock.sendto(bytes(direction),UDP_ADDR)
    pass

def frame_recv():
    """
    Thread to receive incoming image frames from the rover
    """
    while True:
        msg_enc, _ = csock.recvfrom(1024)
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
        print("Usage: python3 controller.py <rover_ip> <rover_port>")
        exit(0)

    UDP_ADDR = (sys.argv[1],int(sys.argv[2]))

    cthread = Thread(target=command_send, name="command_thread")
    fthread = Thread(target=frame_recv, name="frame_thread")

    cthread.start()
    fthread.start()

    # Collect events until released
    with Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()
