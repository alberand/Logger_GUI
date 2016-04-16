#!/usr/bin/env python
# coding=utf-8

import sys

import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
from pyqtgraph.Qt import QtGui, QtCore

from pscene.sceneView import SceneView
from plot_ui import Plot

app = pg.mkQApp()

class View(QtGui.QWidget):

    # Test signal for buttons
    signal = QtCore.Signal(str, str)

    def __init__(self):
        QtGui.QWidget.__init__(self, parent=None)

        self.queue = None

        self.setWindowTitle('Magnetometer scope')

        self.grid = QtGui.QGridLayout()

        self.initScene()

        self.setLayout(self.grid)
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0,0,0,0)

        self.showFullScreen()

    #==========================================================================
    # Gui initialization
    #==========================================================================
    def center(self):
        '''
        Put application window in a center of the screen.
        '''
        screen = QtGui.QDes0ktopWidget().screenGeometry()
        size = self.geometry()

        self.move(
            (screen.width() - size.width()) / 2,
            (screen.height() - size.height()) / 2
        )

    def initScene(self):
        '''
        Initialize plot widget.
        '''
        self.plot = Plot()
        self.plot.layout().setSpacing(0);
        self.plot.layout().setContentsMargins(0,0,0,0);

        self.grid.addWidget(self.plot, 1, 0)

    #==========================================================================
    # Functionality 
    #==========================================================================
    def updatePlot(self):
        '''
        Update plot widget.
        '''
        if not self.queue.empty():
            value = self.queue.get()
            self.plot.addValue(value)

        self.plot.update()

    def setQueue(self, queue):
        '''
        Set queue with data for plotting.
        '''
        if queue:
            self.queue = queue

    #==========================================================================
    # Events and signals
    #==========================================================================
    def emitSignal(self, command, value):
        '''
        Emit signals for buttons.
        '''
        self.signal.emit(command, value)

    def closeEvent(self, event):
        '''
        Proceed close event.
        '''
        self.emitSignal('quit', 'title')
        event.accept()
