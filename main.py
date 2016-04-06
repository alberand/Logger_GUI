#!/usr/bin/env python
# coding=utf-8

import sys

from pyqtgraph import QtGui
import pyqtgraph as pg

from view import View
from presenter import Presenter


if __name__ == '__main__':
    app = pg.mkQApp()
    gui = View()
    presenter = Presenter(gui)

    gui.show()
    sys.exit(app.exec_())
