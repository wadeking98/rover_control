#!/usr/bin/env python3
from socket import *
from threading import *
import sys
import time
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
import gzip

CON_ADDR = ()
PORT = 5555
FRAME_SEG_BUFF = []
BUFF_SIZE = 5
SEG_SIZE = 20
PROD_SEM = Semaphore(BUFF_SIZE)
CONS_SEM = Semaphore(0)
BUFF_lock = Lock()



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
    global CON_ADDR
    msg_enc, addr = rsock.recvfrom(1024)
    CON_ADDR = addr
    sendAndWaitForRep("ack".encode(),addr,rsock,"ack")
    #if we dont receive an ack, that is okay, we assume the client
    #got the message
    #print(addr)
    return


def command_recv():
    while True:
        msg_enc, _ = rsock.recvfrom(1024)
        print(gzip.decompress(msg_enc))
    pass

def frame_send():
    while True:
        CONS_SEM.acquire()
        BUFF_lock.acquire()
        rsock.sendto(gzip.compress(FRAME_SEG_BUFF.pop()), CON_ADDR)
        # rsock.sendto(FRAME_SEG_BUFF.pop(), CON_ADDR)
        BUFF_lock.release()
        PROD_SEM.release()
    pass

def frame_produce():
    #print("got here")
    camera = PiCamera(resolution='100x70', framerate=15)
    rawCapture = PiRGBArray(camera)
    time.sleep(0.1) #allow camera to warm up
    while True:
        camera.capture(rawCapture, format="bgr", use_video_port=True)
        image = rawCapture.array
        npimg = np.asarray(image, dtype=np.int32)
        npimg = np.mean(npimg, axis=2)
        npimg = npimg.astype(np.int)
        imgshape = npimg.shape
        npimg = npimg.flatten()
        for i in range(0,len(npimg),SEG_SIZE):
            PROD_SEM.acquire()
            seg = np.insert(npimg[i:i+SEG_SIZE],0,[i,len(imgshape)])
            seg = np.insert(seg, 2, imgshape)
            FRAME_SEG_BUFF.insert(0, seg.tobytes())
            #print(seg[0])
            CONS_SEM.release()
        rawCapture.truncate(0)


if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Usage: python3 rover.py <rover_ip>")

    IP = sys.argv[1]

    rsock = socket(AF_INET, SOCK_DGRAM)
    #rover will be sending and receiving so we need to bind
    rsock.bind((IP, PORT))
    rsock.setsockopt(SOL_SOCKET, SO_REUSEADDR,1)
    rsock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    connthread = Thread(target=connect, name="conn_thread")
    cthread = Thread(target=command_recv, name="command_thread")
    fthread1 = Thread(target=frame_send, name="frame_thread1")
    fthread2 = Thread(target=frame_send, name="frame_thread2")
    fthread3 = Thread(target=frame_send, name="frame_thread2")
    prodthread = Thread(target=frame_produce, name="producer")

    #set up the camera
    # camera = PiCamera()
    # rawCapture = PiRGBArray(camera)

    # time.sleep(0.1)

    # camera.capture(rawCapture, format="bgr")
    # image = rawCapture.array
    # print(image)
    # npimg = np.asarray(image, dtype=np.int8)

    # print(np.frombuffer(npimg.tobytes(), dtype=np.int8))

    connthread.start()
    connthread.join()
    cthread.start()
    fthread1.start()
    fthread2.start()
    fthread3.start()
    prodthread.start()