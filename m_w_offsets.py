#!/usr/bin/env python
# coding=utf-8

import time
import queue
import socket
from random import randint

import numpy as np
from PySide.QtCore import QThread, Signal

class Model(QThread):

    data_ready = Signal()

    def __init__(self):
        QThread.__init__(self)
        
        self.running = True
        self.data_from_server = False
        self.queue = queue.Queue()

        # Data server
        if self.data_from_server:
            self.host = '188.244.51.15'
            self.port = 5000

    def run(self):
        '''
        Main loop of this thread. First create a socket and connect to the
        server self.host:self.port. Then read data from this socket and send it
        to queue 'self.queue'.
        '''
        # Create socket
        if self.data_from_server:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))

        num_samples = 0
        samples_list = np.array([0, 0, 0])
        offsets_ave_num = 5
        offsets_ready = False
        offsets = np.array([0, 0, 0])

        # Start main loop
        while self.running:
            if not self.queue.full():
                # Get data from socket and put it in the queue.
                if self.data_from_server:
                    sample = (self.getDataFromSocket(s)).append(
                            time.strftime("%H:%M:%S"))
                else:
                    sample = np.array([
                        int(randint(1000,1010)), int(randint(2000,2010)), 
                        int(randint(3000,3010)), time.strftime("%H:%M:%S")
                    ])
                
                sample = np.array([int(value) for value in sample[0:3]])
                print('='*80)
                print('Number of samples is ' + str(num_samples))
                print('samples_list is ' + str(samples_list))
                print('Offsets list is ' + str(offsets))
                print('Sample is ' + str(sample[0:3]))
                print('='*80)

                if num_samples == offsets_ave_num:
                    offsets_ready = True
                    offsets = samples_list/offsets_ave_num
                    data = sample - offsets

                if not offsets_ready:
                    samples_list = np.sum([samples_list, sample], axis=0)
                    num_samples += 1


                # print(data)
                if offsets_ready:
                    self.queue.put(data)
                    # Emit signal that data is ready.
                    self.data_ready.emit()
            time.sleep(0.5)

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
        if s:
            s.send(b's')
            data = s.recv(54)
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
        return [int(value) for value in data.split('\r')[1:-1]]

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
