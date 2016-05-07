#!/usr/bin/env python
# coding=utf-8

import sys
import time
import queue
import struct
import socket
import select
import pickle
import datetime
import os
from random import randint

import numpy as np
from PySide.QtCore import QThread, Signal

from utils import calculateDensity
from settings import config

class Model(QThread):

    data_ready = Signal()
    offsets_ready = Signal(list)

    def __init__(self):
        QThread.__init__(self)
        
        self.running = True
        self.queue = queue.Queue()

        # If we have internet connetction we can receive dat from server
        self.data_from_server = True

        # Offsets period
        self.p_offsets = config['p_offsets']
        # Offsets stack size
        self.n_samples = config['o_buffer']
        # Offsets list
        self.offsets = None

        # Socket
        self.sock_con = None

        # Graph density. Send to pipeline every n-th sample
        self.density = calculateDensity(config['time_axe_range']) # self.calculateDensity(2) 

        # Data server
        if self.data_from_server:
            self.host = config['host']
            # self.host = 'localhost'
            self.port = config['port']


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
        j = 0

        offsets_save_time = datetime.datetime.now()

        # Start main loop
        while self.running:
            if not self.queue.full():
                # Get sample
                sample = self.getSample()
                if not sample:
                    continue
                
                # Choose all values except date
                sample = [value for value in sample[0:3]]
                i += 1

                print('Sample number ' + str(i) + ' is ' + str(sample))

                # If we haven't enough samples continue add them to list
                print(self.offsets)
                if not self.offsets:
                    try_load_offsets = self.loadOffsets()
                    if not try_load_offsets:
                        print('Fail to load offsets from file.')
                        if len(samples_list) < self.n_samples:
                            print('There now enough sample in list for' +
                                    'calculating offsets. Add new sample and' + 
                                    'continue.')
                            samples_list.append(sample)
                            continue
                        # Else calculate offsets
                        else:
                            self.offsets = [value/self.n_samples for value in 
                                    self.calculateOffsets(samples_list)]
                            print('Offstes is ' + str(self.offsets))
                            self.saveOffsets(self.offsets)
                    else:
                        self.offsets = try_load_offsets
                self.offsets_ready.emit(self.offsets)

                # Density. If we take only n-th sample continue
                j += 1
                if j % self.density != 0:
                    continue


                if len(samples_list) < self.n_samples:
                    samples_list.append(sample)
                # Add new sample to the list for calculating offsets
                if len(samples_list) > self.n_samples:
                    samples_list.pop()
                    samples_list.insert(0, sample)

                # If it's new day than recalculate offsets
                if datetime.datetime.now().day > offsets_save_time.day and \
                        len(samples_list) >= self.n_samples:
                    print('Day offset update.')
                    self.offsets = [value/self.n_samples for value in 
                            self.calculateOffsets(samples_list)]
                    # Emit signal that offsets are ready
                    self.offsets_ready.emit(self.offsets)
                    offsets_save_time = datetime.datetime.now()

                # Substract offsets from sample
                data = [a - b for a, b in zip(sample, self.offsets)]

                # Add date to data
                data.append(time.time())

                self.queue.put(data)
                # Emit signal that data is ready.
                self.data_ready.emit()

            # time.sleep(0.5)
        # self.running = True

    def getSample(self):
        # Get data from socket and put it in the queue.
        if self.data_from_server:
            sample = self.getDataFromSocket(self.sock_con)
        else:
            sample = np.array([
                randint(0,1010), randint(2000,2010), 
                randint(3000,3010), randint(0, 100)
            ])

        return sample

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
            data = b''
            try:
                s.send(b's\n')
                # data = s.recv(config['data_l']) # 54
                sym = s.recv(1)
                while sym != '\n':
                    data += sym
                    sym = s.recv(1)
            except socket.timeout:
                print('Socket timeout while received sample.')
            except Exception as e:
                print('Broken pipe occured. Try to open new connection.')
                print(e)
                self.sock_con.close()
                self.sock_con = None
                self.connect_to_server()
        else:
            print('Socket is not initialized.')
            return None

        if not data:
            return None
        else:
            res =  self.formatData(data)
            if res:
                return res
            else: 
                return None

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
        data = data.decode('ascii')
        print('Received data ' + str(data.split(';')))
        try:
            return [float(value) for value in data.split(';')]
            # return [int(value) for value in data.split('\r')[1:-1]]
        except Exception:
            return None

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
                    self.sock_con.settimeout(1)

                    connected = True
                except (OSError, socket.error):
                    print('Can\'t open socket. Maybe there is no internet ' + \
                            'connection. Try \'ping 8.8.8.8\'.')

    def stop(self):
        '''
        Stop while loop in 'self.run' function.
        '''
        print('Call stop thread function.')
        if self.data_from_server:
            self.sock_con.close()

        self.running = False

    def getQueue(self):
        '''
        Return:
            quqeue.queue: Queue which is used to send data for plotting.
        '''
        return self.queue

    def saveOffsets(self, data):
        print('Save offsets.')
        with open(config['off_filename'], 'w+b') as f:
                pickle.dump(data, f)

    def loadOffsets(self):
        print('Load offsets.')
        result = list()
        if os.path.exists(config['off_filename']):
            with open(config['off_filename'], 'r+b') as f:
                    result = pickle.load(f)
        else:
            return None

        print('Result of loading offsets is ' + str(result))
        return result
