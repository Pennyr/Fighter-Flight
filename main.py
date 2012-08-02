import os, sys, datetime
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Canvas(QGraphicsScene):
    def __init__(self):
        super(Canvas,self).__init__()

        self.setSceneRect(0, 0, 1000, 1000)

        self.plane = Plane()
        self.addItem(self.plane)

        self.bullets = []
        self.fire_on = False
        self.fire_cnt = 0

        self.enemies = []
        [self.addEnemy(i*50) for i in xrange(1)]

        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(10)

    def addEnemy(self, x = 50, y = 100):
        enemy = Enemy(x, y)
        self.enemies.append(enemy)
        self.addItem(enemy)

    def update(self):
        self.plane.move()

        todel = []
        for i,bullet in enumerate(self.bullets):
            bullet.move()
            if bullet.y < 0:
                print 'removing', i, 'out of', len(self.bullets), bullet.y
                self.removeItem(bullet)
                todel.append(bullet)

        self.bullets = [b for b in self.bullets if b.y >= 0]
        for b in todel:
            del b

        for enemy in self.enemies:
            enemy.move()
    
        if self.fire_on:
            if self.fire_cnt >= 5:
                #print 'FIRE'
                bullet = Bullet(self.plane.x + self.plane.width / 2, self.plane.y)
                self.addItem(bullet)
                self.bullets.append(bullet)
                self.fire_cnt = 0
            else:
                self.fire_cnt += 1

    def keyPressEvent(self, e):
        if e.isAutoRepeat():
            return

        if e.key() == Qt.Key_Space:
            self.fire_on = True
            self.fire_cnt = 5
        
        if e.key() == Qt.Key_Up:
            self.plane.dirsPressed[0] = True
        elif e.key() == Qt.Key_Down:
            self.plane.dirsPressed[1] = True
        elif e.key() == Qt.Key_Left:
            self.plane.dirsPressed[2] = True
        elif e.key() == Qt.Key_Right:
            self.plane.dirsPressed[3] = True

    def keyReleaseEvent(self, e):
        if e.isAutoRepeat():
            return
        
        if e.key() == Qt.Key_Space:
            self.fire_on = False

        if e.key() == Qt.Key_Up:
            self.plane.dirsPressed[0] = False
        elif e.key() == Qt.Key_Down:
            self.plane.dirsPressed[1] = False
        elif e.key() == Qt.Key_Left:
            self.plane.dirsPressed[2] = False
        elif e.key() == Qt.Key_Right:
            self.plane.dirsPressed[3] = False

class Sprite(QGraphicsPixmapItem):
    def __init__(self, x = 50, y = 100):
        super(Sprite,self).__init__()
        self.x = x
        self.y = y

    def on_move(self):
        pass

    def move(self):
        self.on_move()
        self.setPos(self.x, self.y)
        
def getTransparentPix(fn):
    pix = QPixmap(fn)
    if pix.isNull():
        print 'Error loading Plane pixmap'
        return

    bgcolor = QColor(pix.toImage().pixel(1,1))
    mask = pix.createMaskFromColor(bgcolor)
    pix.setMask(mask)
    return pix

class Bullet(Sprite):
    def __init__(self, x = 50, y = 100):
        super(Bullet,self).__init__(x,y)
        
        pix = QPixmap("sprites/Multiple Views/F-22B.PNG").copy(0,0,3,3)
        self.setPixmap(pix)
    
    def on_move(self):
        self.y -= 5

class Enemy(Sprite):
    def __init__(self, x = 50, y = 100):
        super(Enemy,self).__init__(x,y)
    
        pix = getTransparentPix("sprites/Multiple Views/MiG-X3.PNG")
        self.setPixmap(pix)


class Plane(Sprite):
    def __init__(self, x = 50, y = 100):
        super(Plane,self).__init__(x,y)

        self.dirsPressed = [False for i in xrange(4)]
        self.cnt = [0,0]

        pix = getTransparentPix("sprites/Multiple Views/F-22B.PNG")

        t = QTransform().rotate(-90)
        pix = pix.transformed(t)
        w = pix.width() / 3
        self.width = w
        self.pixs = [pix.copy(i * w, 0, w, pix.height()) for i in xrange(3)]
        t = QTransform().rotate(-180,Qt.XAxis)
        self.pixs.extend([QPixmap.fromImage(pix.toImage().mirrored(True, False)) for pix in self.pixs[1:]])
        self.setPixmap(self.pixs[0])

    def on_move(self):
        # y axis
        if self.dirsPressed[0]:
            self.y -= 1
        elif self.dirsPressed[1]:
            self.y += 1

        # x axis
        if self.dirsPressed[2]:
            self.x -= 1
            self.cnt[0] += 1
            self.cnt[1] = 0
            if self.cnt[0] < 50:
                self.setPixmap(self.pixs[1])
            else:
                self.setPixmap(self.pixs[2])
        elif self.dirsPressed[3]:
            self.x += 1
            self.cnt[1] += 1
            self.cnt[0] = 0
            if self.cnt[1] < 50:
                self.setPixmap(self.pixs[3])
            else:
                self.setPixmap(self.pixs[4])
        else:
            self.cnt = [0,0]
            self.setPixmap(self.pixs[0])

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    c = Canvas()
    w = QGraphicsView(c)
    w.show()
    sys.exit(app.exec_())

