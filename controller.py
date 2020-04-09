#!/usr/bin/env python3
from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
import time

csock = socket(AF_INET, SOCK_DGRAM)
#controller will be sending and receiving so we need to bind
csock = socket.bind(("127.0.0.1", 5555))

def command_send_thread():
    pass

