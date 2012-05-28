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
import os, sys, pygame
from erlport import *
from threading import Thread
from pygame.locals import *
from dbmsg import err, exc,msg
from gamerules import *

pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption('Danger dudes')
pygame.mouse.set_visible(0)

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

    def __init__(self, x, y):
        self.y=y
        self.x=x
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('ddf.bmp', -1)
        self.rect.topleft = x, y
       # err("DD__init__: "+str(x)+' '+str(y))

    def move(self,x,y):
        self.x=x
        self.y=y
        self.rect.topleft = x, y
       # err("DD.move: "+str(self.x)+' '+str(self.y))

    def update(self):
        pass

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, name):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(name, (255,255,255))
        self.rect.topleft = x, y

    def update(self):
        pass
        
class ddclient(Protocol):
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
#        err("Client.worldinfo: "+String(worldinfo))
        self.allsprites.empty()
        world=String(worldinfo).splitlines()
    
        player=Player()
        stone=Stone()
        bomb=Bomb()

        for i in world:            
            if player.isPlayer(i):
                player.fromString(i)
                obj=DD(player.x,player.y)                
                
            elif stone.isStone(i):
                stone.fromString(i)
                #change this obj!
                obj=DD(stone.x,stone.y)

            elif bomb.isBomb(i):
                bomb.fromString(i)
                #Change this obj!
                obj=DD(bomb.x,bomb.y)
            else:
                msg("handle_worldinfo got some crap:\n"+i)
                continue
            obj.add(self.allsprites)

       
class listener(Thread):
    _client = None
    def __init__(self, client):
        self._client = client
        Thread.__init__(self)

    def run(self):
        self._client.run(Port(use_stdio=True))

def main():  
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((255, 255, 255))
    screen.blit(background, (0, 0))
    pygame.display.flip()

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
    
        screen.blit(background, (0, 0)) 
        client.allsprites.draw(screen)
        pygame.display.flip()
        
if __name__ == "__main__":
    client = ddclient()
    listener = listener(client)
    listener.daemon = True
    listener.start()

    main()
