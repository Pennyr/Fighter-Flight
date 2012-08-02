import os, sys, datetime
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Canvas(QGraphicsScene):
    def __init__(self):
        super(Canvas,self).__init__()

        plane = Sprite()
        self.addItem(plane)

    def keyPressEvent(self, e):
        print 'pressed', e.key()
        if e.key() == Qt.Key_Up:
            print 'press up'
            plane.up(True)

    def keyReleaseEvent(self, e):
        print 'released', e.key()
        if e.key() == Qt.Key_Up:
            print 'rel up'
            plane.up(False)

class Sprite(QGraphicsPixmapItem):
    def __init__(self):
        super(Sprite,self).__init__()
        self.upPressed = False
        self.x = 50
        self.y = 100
        self.setOffset(self.x, self.y)

    def up(self, isPressed):
        self.upPressed = isPressed

    
        
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    c = Canvas()
    w = QGraphicsView(c)
    w.show()
    sys.exit(app.exec_())

