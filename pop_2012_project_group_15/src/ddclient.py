###########################################################################
#                                                                         #
#                                                                         #
#                               ddclient                                  #
#                                                                         #
#                                                                         #
###########################################################################
#                                                                         #
#   Communication to ddserver                                             #
#      Connect()                                                          #
#      ActionRequest()                                                    #
#                                                                         #
###########################################################################
#                                                                         #
#   high level functions                                                  #
#      Move()                                                             #
#                                                                         #
############################################################################
import os, sys, pygame, math, time
from erlport import *
from threading import Thread
from pygame.locals import *
from dbmsg import err, exc,msg
from gamerules import *

pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption('Danger dudes')
pygame.mouse.set_visible(1)

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

class DD(pygame.sprite.Sprite):
    x=0
    y=0
    nr=-1
    angle = 0

    def __init__(self, x, y):
        self.y=y
        self.x=x
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('dd.bmp', -1)
        self.oriImage = self.image
        self.rect.topleft = x, y
       # err("DD__init__: "+str(x)+' '+str(y))

    def move(self,x,y,angle=0):
        self.x=x
        self.y=y
        self.rect.topleft = x, y
        self.angle=angle
       # err("DD.move: "+str(self.x)+' '+str(self.y))

    def update(self):
        pass

    def _angle(self, dx, dy):
        if dx == 0:
            if dy > 0:
                return 0.0
            else:
                return 180.0
        elif dy == 0:
            if dx > 0:
                return -90.0
            else:
                return 90.0
        elif dx > 0:
            if dy > 0:
                return -90 + math.degrees(math.atan(math.fabs(dy)/math.fabs(dx)))
            else:
                return -90 - math.degrees(math.atan(math.fabs(dy)/math.fabs(dx)))
        else:
            if dy > 0:
                return 90 - math.degrees(math.atan(math.fabs(dy)/math.fabs(dx)))
            else:
                return 90 + math.degrees(math.atan(math.fabs(dy)/math.fabs(dx)))


        
    def rotate(self, x, y):
        dx = x - 210
        dy = 210 - y
        self.angle = self._angle(dx, dy)

        offset = (math.fabs(self.angle) % 90)

        if offset > 45:
            offset = 90 - offset

        offset = offset / 5      
        self.image = pygame.transform.rotate(self.oriImage, self.angle)
        self.rect.topleft = 190-offset, 190-offset
        
        
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        name = "dd.bmp"
        if image == 1:
            name = "block_circle.bmp"
        elif image == 2:
            name = "block_square.bmp"
            
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(name, (255,255,255))
        self.rect.topleft = x, y

    def update(self):
        pass
        
class ddclient(Protocol):
    _objects={}
    _port = None
    _hero = DD(200,200)
    allsprites = pygame.sprite.RenderPlain(_hero)

    def sendRequest(self,action):
        if self._port:
            self._port.write(action)
        
    def handle(self, port, message):
        if(Atom(message[0]) == "init"):
            self._port=port  
        else:
            self.handle_worldinfo(message[1])

    def handle_worldinfo(self,worldinfo):
       # msg("Client.worldinfo: "+String(worldinfo))
        world=String(worldinfo).splitlines()

        
    
        player=Player()
        stone=Stone()
        bomb=Bomb()
 
        err("Number of rows received: "+str(len(world)))
        for i in world:  
            if i=='CONTINUE':
                continue
            if str(i.split(' ')[0])=='MVWORLD':
                s=i.split(' ')
                dx=int(s[1])
                dy=int(s[2])
                for i in self._objects.keys():
                    self._objects[i].x+=dx
                    self._objects[i].y+=dy
                    if not (0 < self._objects[i].x <400 or 0 < self._objects[i].y <400):
                        self._objects.pop(i)
            elif player.isPlayer(i):
                p=Player()
                p.fromString(i)
                self._objects[p.id]=p
            elif stone.isStone(i):
                s=Stone()
                s.fromString(i)
#                err("got stone: "+stone.toString())
 #               err("from : "+ str(i))
                self._objects[s.id]=s
            elif bomb.isBomb(i):
                b=Bomb()
                b.fromString(i)
                self._objects[b.id]=b
            else:
                msg("handle_worldinfo got some crap:\n"+i+str(i.split(' ')))
                continue
        self.pyprint()

    def pyprint(self):
        self.allsprites.empty()
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((255, 255, 255))
        
        for i in self._objects.keys():
            if self._objects[i].type=='PLAYER':
                obj=DD(self._objects[i].x,self._objects[i].y)
            if self._objects[i].type=='STONE':
                obj=Block(self._objects[i].x,self._objects[i].y,self._objects[i].image)
            if self._objects[i].type=='BOMB':
                obj=DD(self._objects[i].x,self._objects[i].y)                
            obj.add(self.allsprites)

        screen.blit(background, (0, 0)) 
        client.allsprites.draw(screen)
        pygame.display.flip()
               
class listener(Thread):
    _client = None
    def __init__(self, client):
        self._client = client
        Thread.__init__(self)

    def run(self):
        self._client.run(Port(use_stdio=True))

def main():  


    clock = pygame.time.Clock()

    while True:
        clock.tick(50)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == KEYDOWN and event.key == K_UP:
                client.sendRequest('MOVE 0 2')
            elif event.type == KEYDOWN and event.key == K_RIGHT:
                client.sendRequest('MOVE 2 0')
            elif event.type == KEYDOWN and event.key == K_DOWN:
                client.sendRequest('MOVE 0 -2')
            elif event.type == KEYDOWN and event.key == K_LEFT:
                client.sendRequest('MOVE -2 0')
            elif event.type == KEYUP and event.key == K_UP:
                client.sendRequest('MOVE 0 0')
            elif event.type == KEYUP and event.key == K_RIGHT:
                client.sendRequest('MOVE 0 0')
            elif event.type == KEYUP and event.key == K_DOWN:
                client.sendRequest('MOVE 0 0')
            elif event.type == KEYUP and event.key == K_LEFT:
                client.sendRequest('MOVE 0 0')
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pass
               # msg(str(pygame.mouse.get_pos()))
    
 

        cursorPos = pygame.mouse.get_pos()
        cursorX = cursorPos[0]
        cursorY = cursorPos[1]
        client._hero.rotate(cursorX, cursorY)

        
if __name__ == "__main__":
    client = ddclient()
    listener = listener(client)
    listener.daemon = True
    listener.start()

    main()
