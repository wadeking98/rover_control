#!/usr/bin/env python3
from socket import *
from threading import *
from pynput.keyboard import Key, Listener
from PIL import Image
import time
import sys
import cv2
import numpy as np
import gzip


UDP_ADDR = ()
dir_dict = {Key.up:0b001, Key.down:0b010, Key.left: 0b011, Key.right: 0b100}
direction = 0b000
PORT = 5555
MAX_IMG_SIZE = 750*480*3
IMG_BUFF = np.zeros(MAX_IMG_SIZE, dtype=np.float)
IMG_SHAPE = []
RECV_BUFF_SIZE = 65536

def sendAndWait(msg_bytes, addr, sock, time=5):
    sock.settimeout(time)
    sock.sendto(msg_bytes, addr)
    msg_r = None
    try:
        msg_r, _ = sock.recvfrom(1024)
    except:
        pass
    sock.settimeout(None)
    return msg_r

def sendAndWaitForRep(msg_bytes, addr, sock, string, time=1, retry=5):
    msg_r = None
    while msg_r != string and retry > 0:
        msg_r = sendAndWait(msg_bytes, addr, sock, time)
        retry -= 1
    return msg_r


def connect():
    global UDP_ADDR
    msg_r = sendAndWaitForRep("syn".encode(),UDP_ADDR,csock,"ack")
    if msg_r is None:
        print("could not connect")
        exit(1)
    csock.sendto("ack".encode(),UDP_ADDR)
    #print(msg_r.decode())
    return

def command_send():
    """
    Thread to send rover control commands
    """
    while True:
        time.sleep(0.2)
        csock.sendto(gzip.compress(bytes(direction)),UDP_ADDR)
    pass

def frame_recv():
    #print("got here")
    """
    Thread to receive incoming image frames from the rover
    """
    global IMG_BUFF
    global IMG_SHAPE
    while True:
        msg_enc, _ = csock.recvfrom(RECV_BUFF_SIZE)

        seg = np.frombuffer(gzip.decompress(msg_enc), dtype=np.int32)
        # seg = np.frombuffer(msg_enc), dtype=np.int32)
        shape_dim = seg[1]
        offset = 2 #fist two are seq number and shape dim
        IMG_SHAPE = seg[offset:shape_dim+offset]
        #print(seg[0])
        for i in range(offset+shape_dim,len(seg)):
            IMG_BUFF[seg[0]+i-(offset+shape_dim)] = seg[i]/255.0
            
            
        


def img_show():
    global IMG_BUFF
    time.sleep(1)
    cv2.namedWindow("rover display", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("rover display",500,500)
    #calculate the toal length of the image
    img_len = 1
    for d in IMG_SHAPE:
        img_len *= d

    img = np.reshape(IMG_BUFF[:img_len], IMG_SHAPE)
    while True:
        time.sleep(0.2)
        cv2.imshow("rover display", img)
        cv2.waitKey(1)
        
        


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
    
    if len(sys.argv) < 2:
        print("Usage: python3 controller.py <rover_ip>")
        exit(0)
   

    csock = socket(AF_INET, SOCK_DGRAM)
    #controller will be sending and receiving so we need to bind
    #csock.bind((IP, 5555))
    csock.setsockopt(SOL_SOCKET, SO_REUSEADDR,1)
    csock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    UDP_ADDR = (sys.argv[1],PORT)

    connthread = Thread(target=connect, name="conn_thread")
    cthread = Thread(target=command_send, name="command_thread")
    fthread1 = Thread(target=frame_recv, name="frame_thread")
    fthread2 = Thread(target=frame_recv, name="frame_thread")
    fthread3 = Thread(target=frame_recv, name="frame_thread")
    imgthread = Thread(target=img_show, name="img_thread")

    connthread.start()
    connthread.join()

    cthread.start()
    fthread1.start()
    fthread2.start()
    fthread3.start()
    imgthread.start()

    # Collect events until released
    with Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()
