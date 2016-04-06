#!/usr/bin/env python
# coding=utf-8

from PySide import QtGui, QtCore


class graphicsScene(QtGui.QGraphicsScene):

    def __init__(self, parent, size):
        QtGui.QGraphicsScene.__init__(self, parent)

        self.setSceneRect(QtCore.QRectF(0, 0, size, size))
        self.setBackgroundBrush(
            QtGui.QBrush(
                QtGui.QColor(255, 255, 255, 255),
                QtCore.Qt.SolidPattern
            )
        )

    def viewUpdate(self):
        self.update(20000, 20000, 10000, 10000)

    def mouseMoveEvent(self, event):
        self.viewUpdate()
        QtGui.QGraphicsScene.mouseMoveEvent(self, event)
