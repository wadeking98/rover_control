#!/usr/bin/env python3
from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
import time

rsock = socket(AF_INET, SOCK_DGRAM)
#rover will be sending and receiving so we need to bind
rsock = socket.bind(("127.0.0.1", 5555))