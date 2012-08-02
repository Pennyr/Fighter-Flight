import os, sys, datetime
from PyQt4.QtCore import *
from PyQt4.QtGui import *

screenWidth = 800
screenHeight = 800
class Canvas(QGraphicsScene):
    def __init__(self):
        super(Canvas,self).__init__()

        self.setSceneRect(0, 0, screenWidth, screenHeight)
    
        pix = QPixmap("sprites/leafchange2_lg.jpg")
        if pix.isNull():
            print 'Error loading background'
        pix2 = QPixmap.fromImage(pix.toImage().mirrored(False, True))
        self.bgs = [self.addPixmap(p) for p in [pix, pix2]]
        [bg.setZValue(-100) for bg in self.bgs]
        self.bgheight = self.bgs[0].pixmap().height()
        self.bgs[0].setPos(0, self.height() - self.bgheight)
        self.bgs[1].setPos(0, self.bgs[0].y() - self.bgheight)

        self.scoreItem = self.addText('0', QFont('Times', 25, QFont.Bold))
        self.scoreItem.setZValue(1000.0)
        self.score = 0

        bpix = QPixmap("sprites/bullets.png")
        sz = 32
        t = QTransform().rotate(90)
        bpixrows = [bpix.copy(0,i*sz,8*sz,sz) for i in xrange(8)]
        self.bulletpix = [[row.copy(j*sz,0,sz,sz).transformed(t) for j in xrange(8)] for row in bpixrows]

        self.plane = Plane()
        self.addItem(self.plane)

        self.bullets = []
        self.explosions = []
        self.fire_on = False
        self.fire_cnt = 0
        self.missle_on = False
        self.missle_cnt = 0

        self.enemies = []
        [self.addEnemy(i*50) for i in xrange(10)]

        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(10)

    def removeSprites(self, sprites):
        [self.removeItem(s) for s in sprites if s.shouldRemove]
        return [s for s in sprites if not s.shouldRemove]

    def addEnemy(self, x = 50, y = 100):
        enemy = Enemy(x, y)
        self.enemies.append(enemy)
        self.addItem(enemy)

    def update(self):
        [bg.setPos(bg.x(), bg.y() + 2) for bg in self.bgs]
        if self.bgs[0].y() > self.height():
            self.bgs.reverse()
            self.bgs[1].setPos(0, self.bgs[0].y() - self.bgheight)

        self.plane.move()

        for i,bullet in enumerate(self.bullets):
            bullet.move()
        self.bullets = self.removeSprites(self.bullets)

        for enemy in self.enemies:
            enemy.move()
    
        if self.fire_on:
            if self.fire_cnt >= 5:
                #print 'FIRE'
                bullet = Bullet(self.plane.x + self.plane.width / 2, self.plane.y, self.bulletpix[4][7])
                self.addItem(bullet)
                self.bullets.append(bullet)
                self.fire_cnt = 0
        elif self.missle_on:
            if self.missle_cnt >= 100:
                #print 'FIRE'
                bullet = Bullet(self.plane.x + self.plane.width / 2, self.plane.y, self.bulletpix[4][0], 10)
                self.addItem(bullet)
                self.bullets.append(bullet)
                self.missle_cnt = 0
        self.fire_cnt += 1
        self.missle_cnt += 1


        # update explosions and remove completed
        [e.move() for e in self.explosions]
        self.explosions = self.removeSprites(self.explosions)

        # check for bullet hits
        for b in self.bullets:
            ehit = [e for e in self.collidingItems(b) if type(e) == Enemy][:1]
            if len(ehit) > 0:
                ehit[0].hit(b.power)
                b.shouldRemove = True
                e = Explosion(b.x, b.y, self.bulletpix[6][7])
                self.addItem(e)
                self.explosions.append(e)
        self.bullets = self.removeSprites(self.bullets)

        # remove any killed enemies
        for e in self.enemies:
            if e.shouldRemove:
                # TODO: create explosion animation
                self.score += 100

        self.enemies = self.removeSprites(self.enemies)

        self.scoreItem.setPlainText(str(self.score))

    def keyPressEvent(self, e):
        if e.isAutoRepeat():
            return

        if e.key() == Qt.Key_Space:
            self.fire_on = True
            self.fire_cnt = 5
        if e.key() == Qt.Key_Shift:
            self.missle_on = True
        
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
        if e.key() == Qt.Key_Shift:
            self.missle_on = False

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
        self.setPos(x,y)
        self.shouldRemove = False

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

class Explosion(Sprite):
    def __init__(self, x = 50, y = 100, pix = None):
        super(Explosion,self).__init__(x,y)
    
        if pix != None:
            self.setPixmap(pix)
        self.cnt = 0

    def on_move(self):
        self.cnt += 1
        if self.cnt > 3:
            self.shouldRemove = True


class Bullet(Sprite):
    def __init__(self, x = 50, y = 100, pix = None, power = 1):
        super(Bullet,self).__init__(x,y)

        if pix == None:
            pix = QPixmap("sprites/Multiple Views/F-22B.PNG").copy(0,0,3,3)
        self.setPixmap(pix)
        self.x = x - pix.width() / 2
        self.y = y - pix.height()
        self.setPos(self.x, self.y)

        self.power = power
    
    def on_move(self):
        self.y -= 5
        if self.y < 0:
            self.shouldRemove = True


class Enemy(Sprite):
    def __init__(self, x = 50, y = 100, hp = 10):
        super(Enemy,self).__init__(x,y)
    
        pix = getTransparentPix("sprites/Multiple Views/MiG-X3.PNG")
        sz = 64
        self.pix = [pix.copy(i*sz,0,sz,sz).transformed(QTransform().rotate(90)) for i in xrange(5)]
        self.setPixmap(self.pix[2])

        self.hp = hp

    def hit(self, power):
        print 'HIT', power
        self.hp -= power
        if self.hp <= 0:
            self.shouldRemove = True


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

        self.xspeed = 3
        self.yspeed = 1

    def on_move(self):
        # y axis
        if self.dirsPressed[0]:
            self.y -= self.yspeed
        elif self.dirsPressed[1]:
            self.y += self.yspeed

        # x axis
        if self.dirsPressed[2]:
            self.x -= self.xspeed
            self.cnt[0] += 1
            self.cnt[1] = 0
            if self.cnt[0] < 50:
                self.setPixmap(self.pixs[1])
            else:
                self.setPixmap(self.pixs[2])
        elif self.dirsPressed[3]:
            self.x += self.xspeed
            self.cnt[1] += 1
            self.cnt[0] = 0
            if self.cnt[1] < 50:
                self.setPixmap(self.pixs[3])
            else:
                self.setPixmap(self.pixs[4])
        else:
            self.cnt = [0,0]
            self.setPixmap(self.pixs[0])

        self.x = max(0, min(self.x, screenWidth - self.pixmap().width()))
        self.y = max(0, min(self.y, screenHeight - self.pixmap().height()))

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    c = Canvas()
    w = QGraphicsView(c)
    w.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    w.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    w.show()
    sys.exit(app.exec_())

