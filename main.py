import os, sys, datetime
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Canvas(QGraphicsScene):
    def __init__(self):
        super(Canvas,self).__init__()

        self.setSceneRect(0, 0, 1000, 1000)

        self.plane = Sprite()
        self.addItem(self.plane)

        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(100)

    def update(self):
        self.plane.move()
        for item in self.items():
            item.move()

    
    def keyPressEvent(self, e):
        print 'press'
        if e.key() == Qt.Key_Up:
            self.plane.dirsPressed[0] = True
        elif e.key() == Qt.Key_Down:
            self.plane.dirsPressed[1] = True
        elif e.key() == Qt.Key_Left:
            self.plane.dirsPressed[2] = True
        elif e.key() == Qt.Key_Right:
            self.plane.dirsPressed[3] = True

    def keyReleaseEvent(self, e):
        print 'rel'
        if e.key() == Qt.Key_Up:
            self.plane.dirsPressed[0] = False
        elif e.key() == Qt.Key_Down:
            self.plane.dirsPressed[1] = False
        elif e.key() == Qt.Key_Left:
            self.plane.dirsPressed[2] = False
        elif e.key() == Qt.Key_Right:
            self.plane.dirsPressed[3] = False

class Sprite(QGraphicsPixmapItem):
    def __init__(self):
        super(Sprite,self).__init__()
        self.dirsPressed = [False for i in xrange(4)]
        self.x = 50
        self.y = 100
        print self.x, self.y
        #self.setPos(self.x, self.y)

        self.pix = QPixmap("sprites/Multiple Views/F-22B.PNG")
        self.setPixmap(self.pix)
        print self.pix, self.pix.isNull(), self.pix.load("sprites/Multiple Views/F-22B.PNG")
        print self.pix.width()

    def move(self):
        if self.dirsPressed[0]:
            self.y -= 1
        if self.dirsPressed[1]:
            self.y += 1
        if self.dirsPressed[2]:
            self.x -= 1
        if self.dirsPressed[3]:
            self.x += 1
        self.setPos(self.x, self.y)

    #def paint(self, painter, option, widget):
    #    print 'paint'
    #    super(Sprite,self).paint(painter, option, widget)

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    c = Canvas()
    w = QGraphicsView(c)
    w.show()
    sys.exit(app.exec_())

