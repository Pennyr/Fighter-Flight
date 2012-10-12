
function Ship(pos, hp, color) 
{
    // controls
    this.up = false;
    this.down = false;
    this.left = false;
    this.right = false;

    // speed
    this.hSpeed = 0.4;
    this.vSpeed = 0.2;
    
    this.currAngle = 0;
    this.flipSign = 1;

    this.radius = 20;

    this.hp = hp;

    // build the graphic
    this.g = new Kinetic.Group(pos);
    //this.g.add(new Kinetic.Circle({radius:this.radius, fill:"blue", alpha:0.2}));
    this.gun = new Kinetic.Circle({x:0, y:-22, radius:1, fill:"blue", alpha:0.2})
    this.g.add(this.gun);
    this.jetL = new Kinetic.Circle({x:-8, y:18, radius:3, fill:"orange", scale:[1,2]});
    this.jetR = new Kinetic.Circle({x:8, y:18, radius:3, fill:"orange", scale:[1,2]});
    this.g.add(this.jetL);
    this.g.add(this.jetR);
    this.hull = new Kinetic.Path({fill:color||"#444444", stroke:"black", strokeWidth:1, lineJoin:"round",
        data: "m 0,-22 c -15,10 -15,25 -15,38 c 2.5,5 28,5 30,0 c 0,-10 0,-25 -15,-38 z" });
    this.g.add(this.hull);
    this.cockpit = new Kinetic.Circle({x:0, y:0, radius:6, fill:"black", scale:[1,2]});
    this.g.add(this.cockpit);

    // update the animation
    this.update = function(timeDiff) 
    {
        var pos = this.g.getPosition();

        var xmove = this.hSpeed * timeDiff;
        if (this.left && pos.x - xmove >= 0) 
            this.g.move(-xmove,0);
        else if (this.right && pos.x + xmove <= width) 
            this.g.move(xmove,0);

        var ymove = this.vSpeed * timeDiff;
        if (this.up && pos.y - ymove >= 0) 
            this.g.move(0,-ymove);
        else if (this.down && pos.y + ymove <= height) 
            this.g.move(0,ymove);

        var thrusterY = (this.up ? 23 : 18);
        this.jetL.setY(thrusterY);
        this.jetR.setY(thrusterY);

        this.roll();

    };

    this.flip = function() { this.flipSign *= -1; this.g.setRotation(Math.PI); };

    this.collidesWith = function(obj)
    {
        var opos = obj.g.getPosition();
        var pos = this.g.getPosition();
        var dx = opos.x - pos.x;
        var dy = opos.y - pos.y;
        d = Math.sqrt(dx * dx + dy * dy);
        if (d < obj.radius + this.radius)
            return true;
        else
            return false;
    };

    this.frontPos = function() { return this.gun.getAbsolutePosition(); };

    // roll the plane
    this.roll = function()
    {
        var pi = Math.PI;
        if (this.left)
            this.currAngle -= 0.03 * pi * this.flipSign;
        else if (this.right)
            this.currAngle += 0.03 * pi * this.flipSign;
        else
            this.currAngle = 0;
        this.currAngle = Math.max(-pi/2, Math.min(this.currAngle, pi/2));

        var angle = this.currAngle % (2 * pi);
        var absangle = Math.abs(angle);
        
        this.hull.setScale([0.5 + 0.5 * Math.abs(absangle - pi) / pi, 1]);
        
        this.cockpit.setX(8 * Math.sin(angle));
        if (absangle > 0.5 * pi && absangle < 1.5 * pi)
            this.cockpit.moveToBottom();
        else
            this.cockpit.moveToTop();
        
        var d = Math.abs(absangle - pi/2) / (pi/2);
        this.jetL.setX(-8 * d);
        this.jetR.setX(8 * d);
    };
}

function Cloud(pos)
{
    var g = new Kinetic.Group(pos);
    for (var i=0; i<5; i++)
    {
        var r = Math.random()*30+40;
        g.add(new Kinetic.Circle({x:Math.random()*100, y:Math.random()*100, radius:r, 
            fill: {start: {x:0,y:0,radius:10}, end: {x:0,y:0,radius:r}, colorStops: [1,'white', 0,'#EEEEEE']}}));
            //fill:"white"}));
    }
    //g.setAlpha(0.99);
    return g;
}

function Bullet(pos, color) 
{
    this.speed = 0.5; // pixels per ms
    this.radius = 3;
    this.power = 1;
    this.finalY = pos.y - 0.5 * height
    this.g = new Kinetic.Circle({x:pos.x, y:pos.y, radius:this.radius, fill:color||"black"});
    this.update = function(timeDiff) { this.g.move(0,-this.speed * timeDiff); };
}

window.onload = function() 
{
    width = 800;
    height = 600;
    var stage = new Kinetic.Stage({ container: "container", width: width, height: height });
    var background = new Kinetic.Layer();
    background.add(new Kinetic.Rect({width:width, height:height, 
        //fill:"green"
        fill:{start:{x:0,y:0},end:{x:width,y:0}, colorStops:[0,'green',0.7,'#22CC22',1,'green']}
    }));
    stage.add(background);

    var sounds = {'shot':0, 'rocket':0, 'battle004':0}
    for (var s in sounds)
        sounds[s] = new Audio("sounds/" + s + ".wav");

    var layer = new Kinetic.Layer();
    
    var gradient = {start: {x:-20,y:0}, end: {x:20,y:0}, colorStops: [0,'#444444', 0.5,'#999999', 1,'#444444']};
    var ship = new Ship({x:0.5*width,y:0.9*height}, 0, gradient);
    layer.add(ship.g);
    ship.g.setZIndex(0);

    var bullets = [];

    var enemies = [];
    var x = 50;
    var enemyHP = 3;
    var gradient2 = {start: {x:-20,y:0}, end: {x:20,y:0}, colorStops: [0,'darkred', 0.5,'red', 1,'darkred']};
    while (x < width)
    {
        e = new Ship({x:x, y:-x}, enemyHP, gradient2);
        e.flip();
        e.hSpeed = Math.random() * 0.1 + 0.05;
        e.update2 = function(timeDiff) 
        { 
            this.g.move(0, 0.1 * timeDiff); 
            if (this.g.getPosition().y > height + 100)
            {
                this.g.setY(-300);
                this.hp = enemyHP;
            }
        }
        enemies.push(e);
        layer.add(e.g);
        e.g.setZIndex(0);

        x += 50;
    }

    var clouds = [];
    for (var i=0; i<20; i++)
    {
        var cloud = Cloud({x:Math.random() * width, y:-Math.random() * 3000 + height});
        layer.add(cloud);
        cloud.setZIndex(Math.random() * 2000 - 1000);
        clouds.push(cloud);
    }

    var points = 0;
    var pointText = new Kinetic.Text({x:20, y:20, text:"0", fontSize:20, textFill:"black", 
        stroke: "black", strokeWidth:4, fill:"white", padding:6, cornerRadius:5, width:100, align:"right"});
    layer.add(pointText);

    var gameOver = new Kinetic.Text({x:0, y:0.45*height, text:"Game\nOver", fontSize:40, width:width, textFill:"black", align:"center"});
    layer.add(gameOver);
    gameOver.hide();

    var lives = [];
    for (var i=0; i<4; i++)
    {
        l = new Ship({x:150 + i*20, y:40}, 0, gradient);
        l.g.setScale(0.5);
        lives.push(l);
        layer.add(l.g);
    }

    stage.add(layer);


    addEventListener("keydown", function(evt) 
    {
        var code = evt.charCode ? evt.charCode : evt.keyCode;
        switch (code) {
            case 38: // up
                ship.up = true;
                break;
            case 40: // down
                ship.down = true;
                break;
            case 37: // left
                ship.left = true;
                break;
            case 39: // right
                ship.right = true;
                break;
            case 32: // space
                ship.fire = true;
                break;
        }
    });
    addEventListener("keyup", function(evt) 
    {
        var code = evt.charCode ? evt.charCode : evt.keyCode;
        switch (code) {
            case 38: // up
                ship.up = false;
                break;
            case 40: //down
                ship.down = false;
                break;
            case 37: // left
                ship.left = false;
                break;
            case 39: // right
                ship.right = false;
                break;
            case 32: // space
                ship.fire = false;
                break;
        }
    });

    // our update loop goes here
    var bdiff = 100;
    var ediff = 1000;
    stage.onFrame(function(frame) 
    {
        td = frame.timeDiff;

        ship.update(td);
        
        bdiff += td;
        if (bdiff >= 100 && ship.fire && ship.checkCollisions)
        {
            bdiff = 0;
            b = new Bullet(ship.frontPos());
            bullets.push(b);
            layer.add(b.g);
            b.g.setZIndex(0);

            sounds['shot'].currentTime = 0;
            sounds['shot'].play();
        }

        ediff += td;
        if (ediff > 1000)
        {
            ediff = 0;
            for (var i=0; i<enemies.length; i++)
            {
                var r = Math.random();
                var e = enemies[i];
                e.left = e.right = false;
                if (r < 0.2) e.left = true;
                else if (r < 0.4) e.right = true;
                console.log('here',r);
            }
        }

        // update bullets... check for enemy hit and going off screen
        for (var i=0; i<bullets.length; i++)
        {
            var b = bullets[i];
            var shouldRemove = false;
            if (b.g.getPosition().y < b.finalY)
                shouldRemove = true;
            else
            {
                for (var j=0; j<enemies.length; j++)
                {
                    var e = enemies[j];
                    if (e.collidesWith(b))
                    {
                        shouldRemove = true;
                        e.hp -= b.power;
                        if (e.hp <= 0)
                        {
                            // destroyed
                            //layer.remove(e.g);
                            //enemies.splice(j,1);
                            //j--;
                            e.g.setY(-300);
                            e.hp = enemyHP;
                            points += 100;
                            console.log("killed...", points);
                            sounds['battle004'].currentTime = 0;
                            sounds['battle004'].play();
                        }
                    }
                }
            }

            if (shouldRemove)
            {
                layer.remove(b.g);
                bullets.splice(i,1);
                i--;
            }
            else
                b.update(td);
        }

        for (var i=0; i<enemies.length; i++)
        {
            enemies[i].update(td);
            enemies[i].update2(td);
            if (ship.checkCollisions && ship.collidesWith(enemies[i]))
                ship.hp -= 5;
        }

        if (ship.hp <= 0)
        {
            var l = lives.pop();
            layer.remove(l.g);
            if (lives.length <= 0)
            {
                gameOver.setText('Game\nOver');
                gameOver.show();
                gameOver.moveToTop();
                //updateScores(points);
                //scores.show();
                //ship.g.hide();
                stage.stop();
            }
            else
            {
                ship.g.setPosition({x:0.5*width,y:0.9*height});
                ship.g.setAlpha(0.3);
                ship.hp = 10;
                ship.checkCollisions = false;

                gameOver.setText('Get Ready: 3');
                gameOver.show();
                gameOver.moveToTop();

                setTimeout(function() {
                    ship.g.setAlpha(1);
                    ship.checkCollisions = true;
                    gameOver.hide();
                }, 3000);

                setTimeout(function() { gameOver.setText('Get Ready: 2'); }, 1000);
                setTimeout(function() { gameOver.setText('Get Ready: 1'); }, 2000);
            }
        }

        for (var i=0; i<clouds.length; i++)
        {
            clouds[i].move(0, 0.03 * td);
            if (clouds[i].getPosition().y > height + 200)
                clouds[i].move(0, -3000);
        }

        pointText.setText(points.toString());

        background.draw();
        layer.draw();
    });

    stage.start();
};

