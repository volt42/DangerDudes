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
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((255, 255, 255))

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
    _port = None
    _hero = DD(200,200)
    allsprites = pygame.sprite.RenderPlain(_hero)
    mleft=0
    mright=0
    mdown=0
    mup=0

    def sendRequest(self,action):
        if self._port:
            if action == 'MOVE':
                ud=2*(self.mup-self.mdown)
                rl=2*(self.mright-self.mleft)
                self._port.write("MOVE "+str(rl)+' '+str(ud))
            else:
                self._port.write(action)
        
    def handle(self, port, message):
        if(Atom(message[0]) == "init"):
            self._port=port  
        else:
            self.handle_worldinfo(message[1])

    def handle_worldinfo(self,worldinfo):
  #      msg("Client.worldinfo: "+String(worldinfo))
        world=String(worldinfo).splitlines()
        if not world[0]=='CONTINUE':
            self.allsprites.empty()
#            self._hero.add(self.allsprites)

    
        player=Player()
        stone=Stone()
        bomb=Bomb()
 
       # err(str(world))
        for i in world:        
            if i=='CONTINUE':
                continue
            if player.isPlayer(i):
                player.fromString(i)
                obj=DD(player.x,player.y)                
                
            elif stone.isStone(i):

                stone.fromString(i)
               # if stone.x>200 or stone.y>200:
                #    err("BAD stone: "+stone.toString())
                obj=Block(stone.x,stone.y,stone.imageId)

            elif bomb.isBomb(i):
                bomb.fromString(i)
                #Change this obj!
                obj=DD(bomb.x,bomb.y)
            elif i=='END':
                screen.blit(background, (0, 0)) 
                client.allsprites.draw(screen)
                pygame.display.flip()
            else:
                err("handle_worldinfo got some crap:\n"+i)
                continue
            obj.add(self.allsprites)




       # err(str(world))
       
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
                client.mup=1
                client.sendRequest('MOVE')
            elif event.type == KEYDOWN and event.key == K_RIGHT:
                client.mright=1
                client.sendRequest('MOVE')
            elif event.type == KEYDOWN and event.key == K_DOWN:
                client.mdown=1
                client.sendRequest('MOVE')
            elif event.type == KEYDOWN and event.key == K_LEFT:
                client.mleft=1
                client.sendRequest('MOVE')
            elif event.type == KEYUP and event.key == K_UP:
                client.mup=0
                client.sendRequest('MOVE')
            elif event.type == KEYUP and event.key == K_RIGHT:
                client.mright=0
                client.sendRequest('MOVE')
            elif event.type == KEYUP and event.key == K_DOWN:
                client.mdown=0
                client.sendRequest('MOVE')
            elif event.type == KEYUP and event.key == K_LEFT:
                client.mleft=0
                client.sendRequest('MOVE')
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pass
               # msg(str(pygame.mouse.get_pos()))
    
 #       screen.blit(background, (0, 0)) 
 #       client.allsprites.draw(screen)
 #       pygame.display.flip()

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
