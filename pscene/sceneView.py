#!/usr/bin/env python
# coding=utf-8

from PySide import QtGui, QtCore

from .graphicsScene import graphicsScene


class SceneView(QtGui.QGraphicsView):

    def __init__(self, parent):
        QtGui.QGraphicsView.__init__(self, parent)

        self.setDragMode(1)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setRenderHints(
            QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform
        )

        self.size = 50000
        self.relativePos = self.size / 2 - 1
        self.scene = graphicsScene(self, self.size)
        self.centerPoint()
        # self.scene.gPoint(self.relativePos, self.relativePos)

        self.setScene(self.scene)
        self.centerOn(QtCore.QPoint(self.size / 2 - 1, self.size / 2 - 1))

        # Some tests
        # self.addPoint('First item', 50, 50, 20)
        # self.addPoint('Second item', 100, 70, 30)
        # self.addPoint('Third item', 200, 100, 100)

        # self.scene.connectPoints(0, 2)

    def addPoint(self, title, posX=0, posY=0, size=20):
        point = self.mapToScene(self.centerPointX, self.centerPointY)
        posX = point.x() - self.relativePos
        posY = point.y() - self.relativePos

        self.centerPoint()
        print(self.centerPointX, self.centerPointY)
        print(posX, posY)
        self.scene.addPoint(
            title,
            self.relativePos + posX,
            self.relativePos + posY,
            size
        )

    def centerPoint(self):
        size = self.geometry().size()

        self.centerPointX = size.width() / 2
        self.centerPointY = size.height() / 2
