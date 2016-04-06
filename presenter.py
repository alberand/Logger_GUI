#!/usr/bin/env python
# coding=utf-8

import time
from random import randint

from model import Model


class Presenter:

    def __init__(self, view):
        self.__model = Model()
        self.__view = view

        self.__view.setQueue(self.__model.getQueue())

        self.__view.signal.connect(self.processSignal)

        # This signal is used once and just set offsets values in legend
        self.__model.data_ready.connect(self.__view.updatePlot)
        self.__model.offsets_ready.connect(self.__view.plot.setLegends)

        self.__model.start()

    def processSignal(self, command, value):
        if command == 'quit':
            self.__model.stop()
            time.sleep(0.5)
            self.__view.close()

        elif command == 'update':
            # Test. It should not be there
            # self.__view.plot.addValue(randint(1, 10))
            self.__view.plot.update()
            # self.__model.update()

        elif command == 'start_model':
            print('Start model signal received.')
            self.__model.start()
