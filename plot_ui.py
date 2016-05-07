#!/usr/bin/env python
# coding=utf-8

import time
import datetime

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui

from settings import config
from utils import calculateDensity

class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_time = datetime.datetime.now()
    
    def tickStrings(self, values, scale, spacing):
        size = len(values)
        result = list()
        for i, value in enumerate(values):
            c_time = self.init_time + datetime.timedelta(
                    seconds=values[i])
            result.append(
                    datetime.datetime.fromtimestamp(
                            time.mktime(c_time.timetuple())
                    ).strftime(config['time_format'])
            )

        return result
        # return [datetime.datetime.fromtimestamp(value).strftime('%H:%M:%S') for value in values]

class Plot(QtGui.QWidget):
    '''
    This class is QWidget which contains PlotWidget from pyqtgraph.
    '''

    def __init__(self):
        QtGui.QWidget.__init__(self)

        # Set up layout
        __layout = QtGui.QVBoxLayout()
        self.setLayout(__layout)

        # x_array - data set.
        # stack_size - number of samples plotted at once.
        self.x_array = []
        self.stack_size = self.calculateStackSize(config['time_axe_range'])

        # Auto pan
        self.auto_pan = True

        # Graph density
        self.density = calculateDensity(config['time_axe_range'])

        print(self.stack_size)
        print(self.density)

        # Create main plot
        self.plot = pg.PlotWidget(title='Sensors values',
		axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.plot.addLegend()

        # Create buttons
        zoomInBtn = QtGui.QPushButton('Zoom in')
        zoomInBtn.setParent(self.plot)
        zoomOutBtn = QtGui.QPushButton('Zoom out')
        zoomOutBtn.setParent(self.plot)
        autoRangeBtn = QtGui.QPushButton('Auto range')
        autoRangeBtn.setParent(self.plot)

        # Set buttons positions
        x = self.size().width()
        y = self.size().height()
        zoomInBtn.move(x + 50, 70)
        zoomOutBtn.move(x + 50, 100)
        autoRangeBtn.move(x + 50, 130)

        # Connect buttons to slots
        zoomInBtn.clicked.connect(self.zoomIn)
        zoomOutBtn.clicked.connect(self.zoomOut)
        autoRangeBtn.clicked.connect(self.autoPan)

        # Add plot elements
        self.h = self.plot.plot(pen='r', name='Offset is 0.00e0', 
                clipToView=True, autoDownsample=True)
        self.z = self.plot.plot(pen='g', name='Offset is 0.00e0', 
                clipToView=True, autoDownsample=True)
        self.y = self.plot.plot(pen='b', name='Offset is 0.00e0', 
                clipToView=True, autoDownsample=True)

        self.h.setData(x=[0.0], y=[0.0])
        self.z.setData(x=[0.0], y=[0.0])
        self.y.setData(x=[0.0], y=[0.0])

        __layout.addWidget(self.plot)

    def update(self):
        '''
        Update plot widget. Plotted data can be changed by 'addValue' function.
        '''
        self.h.appendData([self.x_array[-1][0], self.x_array[-1][3]],
                self.density)
        self.z.appendData([self.x_array[-1][1], self.x_array[-1][3]],
                self.density)
        self.y.appendData([self.x_array[-1][2], self.x_array[-1][3]],
                self.density)
        #
        # KOSTIL
        #
        self.plot.hideAxis('bottom')
        self.plot.showAxis('bottom')

        if self.auto_pan:
            self.plot.autoRange(padding=0)

    def addValue(self, value):
        '''
        This function add value to the data set. Value should be a three items
        list.
        Args:
            value: three item list [123, 123, 123]
        '''
        if value is not None:
            self.x_array.append((value))
        else:
            print('Fail to add empty value.')

        while len(self.x_array) > self.stack_size:
            self.h.popData()
            self.y.popData()
            self.z.popData()
            self.x_array.pop(0)

    def calculateStackSize(self, hours):
        '''
        This function calculate density for given hours. Add to because we 
        show only 'stack_size - 2' samples.
        Args:
            hours: number of hours to display.
        Returns:
            Integer value which show that we need every n-th sample
        '''
        result =  hours*3600
        if result > config['min_stack_size']:
            return config['min_stack_size']
        else:
            return result

    def autoPan(self):
        '''
        Turn on/off between auto moving pan and static pan.
        '''
        self.auto_pan = not self.auto_pan

    def zoomIn(self):
        '''
        This function is used to increase stack_size which 
        '''
        self.stack_size -= int(self.stack_size/10)
        self.plot.autoRange(padding=0)

    def zoomOut(self):
        '''
        This function is used to decrease stack_size 
        '''
        self.stack_size += int(self.stack_size/10) or 1
        self.plot.autoRange(padding=0)


    def setLegends(self, offsets):
        '''
        Update legengs for plots using value from list 'offsets'.
        Args:
            offsets: list with offsets value for every plot.
        '''
        l_items = self.plot.getPlotItem().legend.items
        for i, item in enumerate(l_items):
            item[1].setText("Offset is {:8.2f} nT".format(offsets[i]*1e9))

    def clear(self):
        '''
        This function clear plot.
        '''
        self.plot.clear()
