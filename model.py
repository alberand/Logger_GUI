#!/usr/bin/env python
# coding=utf-8

import sys
import time
import queue
import struct
import socket
import select
from random import randint

import numpy as np
from PySide.QtCore import QThread, Signal

class Model(QThread):

    data_ready = Signal()
    offsets_ready = Signal(list)

    def __init__(self):
        QThread.__init__(self)
        
        self.running = True
        self.queue = queue.Queue()

        # If we have internet connetction we can receive dat from server
        self.data_from_server = False

        # Offsets period
        self.p_offsets = 1
        # Offsets stack size
        self.n_samples = 5

        # Socket
        self.sock_con = None

        # Graph density. Send to pipeline every n-th sample
        # self.density = self.calculateDensity(1) 

        # Data server
        if self.data_from_server:
            # self.host = '188.244.51.15'
            self.host = 'localhost'
            self.port = 5000


    def run(self):
        '''
        Main loop of this thread. First create a socket and connect to the
        server self.host:self.port. Then read data from this socket and send it
        to queue 'self.queue'.
        '''
        # Create socket
        if self.data_from_server:
            self.connect_to_server()

        samples_list = []
        i = 0
        # j = 0

        # Start main loop
        while self.running:
            if not self.queue.full():
                # Get data from socket and put it in the queue.
                if self.data_from_server:
                    sample = self.getDataFromSocket(self.sock_con)
                    if not sample:
                        continue
                else:
                    sample = np.array([
                        randint(1000,1010), randint(2000,2010), 
                        randint(3000,3010)
                    ])
                
                # Choose all values except date
                sample = [value for value in sample[0:3]]
                print('Sample number ' + str(i) + ' is ' + str(sample))
                i += 1

                # If we haven't enough samples continue add them to list
                if len(samples_list) < self.n_samples:
                    samples_list.append(sample)
                    continue
                # Else calculate offsets
                else:
                    offsets = self.calculateOffsets(samples_list)
                    print('Offstes is ' + str(
                                [value/self.n_samples for value in offsets]
                            )
                    )

                # If it's n-th sample add it (period)
                if i % self.p_offsets == 0:
                    print('i is equal to ' + str(i) + '. And we call recalculation for offsets.')
                    samples_list.pop()
                    samples_list.insert(0, sample)
                    offsets = self.calculateOffsets(samples_list)
                    # Emit signal that offsets are ready
                    self.offsets_ready.emit(offsets)


                # Density.
                # j += 1
                # if j % self.density != 0:
                    # continue

                # Substract offsets from sample
                data = [a - b/self.n_samples 
                        for a, b in zip(sample, offsets) ]

                # Add date to data
                data.append(time.time())

                self.queue.put(data)
                # Emit signal that data is ready.
                self.data_ready.emit()

            time.sleep(0.5)
        self.running = True

    def calculateOffsets(self, samples_list):
        """
        """
        offsets = [0, 0, 0]

        for i in range(3):
            for j in range(len(samples_list)):
                offsets[i] += samples_list[j][i]

        return offsets

    def getDataFromSocket(self, s):
        '''
        This function connect to the socket 's' and read data from it. Than
        convert byte string to list with integer values of sensor.

        Args:
            s: socket.socket objects which represent connection to the server.
            From which we will be receiving data.
        Return:
            [12345, 12345, 12345, 12345]
        '''
        data = None
        if s:
            try:
                s.send(b's')
                data = s.recv(67) # 54
            except socket.timeout:
                print('Socket timeout while received sample.')
            except Exception as e:
                print('Broken pipe occured. Try to open new connection.')
                self.sock_con.close()
                self.sock_con = None
                self.connect_to_server()
        else:
            print('Socket is not initialized.')
            return None

        if not data:
            return None
        else:
            return self.formatData(data)

    def formatData(self, data):
        '''
        This function convert byte string received from server to list with
        integers values.

        Args:
            data: string which containt date and 4 data values which are
            separeted by a '\r' symbol.
        Return:
            [12345, 12345, 12345, 12345] list with integer values.
        '''
        data = data.decode('UTF-8')
        print('Received data ' + str([float(value) for value in data.split(';')]))
        return [float(value) for value in data.split(';')]

    def connect_to_server(self):
        '''
        This function create connection to address 'self.host' with port
        'self.port'. Socket is saved to 'self.sock_con'.
        '''
        if not self.sock_con:
            connected = False
            while not connected:
                try:
                    # Create socket
                    self.sock_con = socket.socket(socket.AF_INET, 
                            socket.SOCK_STREAM)
                    self.sock_con.connect((self.host, self.port))

                    # Set non-blocking mode and 5 seconds timeout
                    self.sock_con.setblocking(False)
                    self.sock_con.settimeout(5)

                    connected = True
                except (OSError, socket.error):
                    print('Can\'t open socket. Maybe there is no internet ' + \
                            'connection. Try \'ping 8.8.8.8\'.')

    def stop(self):
        '''
        Stop while loop in 'self.run' function.
        '''
        print('Call stop thread function.')
        self.running = False

    def getQueue(self):
        '''
        Return:
            quqeue.queue: Queue which is used to send data for plotting.
        '''
        return self.queue