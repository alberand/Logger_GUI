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
        result = list()
        size = len(values)
        # print(values)
        # for i in range(len(values)):
            # c_time = datetime.datetime.now() - datetime.timedelta(
                    # seconds=values[int(size - i - 1)])
            # result.append(
                    # datetime.datetime.fromtimestamp(
                            # time.mktime(c_time.timetuple())
                    # ).strftime('%H:%M:%S')
            # )

        # return result
        result = list()
        for i, value in enumerate(values):
            c_time = self.init_time + datetime.timedelta(
                    seconds=values[i])
            result.append(
                    datetime.datetime.fromtimestamp(
                            time.mktime(c_time.timetuple())
                    ).strftime('%H:%M:%S')
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
        zoomInBtn.clicked.connect(
                self.zoomIn
        )
        zoomOutBtn.clicked.connect(
                self.zoomOut
        )
        autoRangeBtn.clicked.connect(
                self.autoPan
        )

        # Add plot elements
        self.h = self.plot.plot(pen='r', name='Red plot ', clipToView=True,
                autoDownsample=True)
        self.h.setData(x=[0.0], y=[0.0])
        self.z = self.plot.plot(pen='g', name='Green plot ', clipToView=True,
                autoDownsample=True)
        self.z.setData(x=[0.0], y=[0.0])
        self.y = self.plot.plot(pen='b', name='Blue plot ', clipToView=True,
                autoDownsample=True)
        self.y.setData(x=[0.0], y=[0.0])

        __layout.addWidget(self.plot)

    def update(self):
        '''
        Update plot widget. Plotted data can be changed by 'addValue' function.
        '''
        # x_axe = [item[3] for item in self.x_array], 
        # self.h.setData(
                # x=x_axe[0],
                # y=[item[0] for item in self.x_array])
        # self.z.setData(
                # x=x_axe[0],
                # y=[item[1] for item in self.x_array])
        # self.y.setData(
                # x=x_axe[0],
                # y=[item[2] for item in self.x_array])
        print(self.x_array[-1][3])
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
            # self.h.clear()
            # self.z.clear()
            # self.y.clear()
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
        if result > 700:
            return 700
        else:
            return result
        # result = hours*3600/800

    def autoPan(self):
        self.auto_pan = not self.auto_pan

    def zoomIn(self):
        # sizes = self.plot.viewRange()[0]
        # dif = sizes[1] - sizes[0]
        # self.plot.setXRange(sizes[0] + dif/10, sizes[1] - dif/10)

        self.stack_size -= int(self.stack_size/10)
        self.plot.autoRange(padding=0)

    def zoomOut(self):
        # sizes = self.plot.viewRange()[0]
        # dif = sizes[1] - sizes[0]
        # self.plot.setXRange(sizes[0] - dif/10, sizes[1] + dif/10)

        self.stack_size += int(self.stack_size/10) or 1
        self.plot.autoRange(padding=0)


    def setLegends(self, offsets):
        l_items = self.plot.getPlotItem().legend.items
        for i, item in enumerate(l_items):
            item[1].setText("Offset is " + str(offsets[i]))

    def clear(self):
        '''
        This function clear plot.
        '''
        self.plot.clear()
