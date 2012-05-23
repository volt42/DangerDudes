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
from erlport import Protocol, Port, String
from threading import Thread
import os, sys, pygame
from pygame.locals import *


pygame.init()
screen = pygame.display.set_mode((800, 600))
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
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('ddf.bmp', -1)
        self.rect.topleft = x, y
        
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
    #internal variables
    _world = {}
    _objects = {}
    _width = 0
    _height = 0
    _port=0
    _name=""
    _hero = DD(400,300)
    allsprites = pygame.sprite.RenderPlain(_hero)

    def sendRequest(action):
        self._port.write(action)
        
    #Outgoing functions
    def connect(self,address):
        print('Lets do this later when we know how to!')
        
    def actionrequest(self,action):
        print('define the actionrequest function')
        global player_action
        player_action=action

    def handle_init(self,port,name):
        self._port=port
        self._name=name
        print str(name) + ' ' +str(self._name)

    def handle_worldinfo(self,worldinfo):
        self.allsprites.empty()
        self._world=worldinfo
        world=worldinfo.splitlines()
        for i in world:            
            objectInfo = i.split(' ')
            newObject = objectInfo[0]
            x = int(objectInfo[1])
            y = int(objectInfo[2])

            if newObject == 'Player':
                player = DD(x, y)
                player.add(self.allsprites)
            elif newObject == 'Stone':
                stone = Block(x, y, 'block_circle.bmp')
                stone.add(self.allsprites)

        return "Hello, %s" % str(newObject) 
            
        
    
    ##stuff pygame needs to know
    def mapsizetopygame(self):
        return str(self._width)+' '+str(self._height)
    def maptopygame(self):
        value=""
        for i in self._world.iterkeys():
            value +=self._objects[self._world[i]].type+ ' '+str(i[0])+' '+str(i[1])+' '+'\n'
        return value
    #high level functions

    def move(self,dx,dy):
        speed=sqrt(dx*dx+dy*dy)
        if speed > 2: #speed test
            dx /= 2/speed
            dy /= 2/speed
        self.actionrequest('MOVE '+str(dx) +' '+ str(dy))
    def fire(self, type):
        self.actionrequest('FIRE '+str(type))

def main():   
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((255, 255, 255))

    screen.blit(background, (0, 0))
    pygame.display.flip()

    clock = pygame.time.Clock()

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == KEYDOWN and event.key == K_UP:
                client.sendRequest('UP')
            elif event.type == KEYDOWN and event.key == K_RIGHT:
                client.sendRequset('RIGHT')
            elif event.type == KEYDOWN and event.key == K_DOWN:
                client.sendRequset('DOWN')
            elif event.type == KEYDOWN and event.key == K_LEFT:
                client.sendRequset('LEFT')
            elif event.type == KEYUP and event.key == K_UP:
                client.sendRequset('UP_0')
            elif event.type == KEYUP and event.key == K_RIGHT:
                client.sendRequset('RIGHT_0')
            elif event.type == KEYUP and event.key == K_DOWN:
                client.sendRequset('DOWN_0')
            elif event.type == KEYUP and event.key == K_LEFT:
                client.sendRequset('LEFT_0')        
    
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
        
if __name__ == "__main__":
    client = ddclient()
    listener = listener(client)
    listener.daemon = True
    listener.start()
    main()
