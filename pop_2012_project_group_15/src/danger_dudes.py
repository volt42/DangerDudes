#Import Modules
import os, sys, pygame, random, subprocess, signal
from pygame.locals import *
from threading import Thread

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

def newactions():
    newaction = sys.stdin.readline()

    if newaction == "DOWN\n":
        pygame.event.post(pygame.event.Event(KEYDOWN, key=K_DOWN))
    elif newaction == "RIGHT\n":
        pygame.event.post(pygame.event.Event(KEYDOWN, key=K_RIGHT))
    elif newaction == "DOWN_0\n":
        pygame.event.post(pygame.event.Event(KEYUP, key=K_DOWN))
            
class listener(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            newactions()

#functions to create our resources
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

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', fullname
        raise SystemExit, message
    return sound


#classes for our game objects
class DD(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image1, self.rect1 = load_image('ddb.bmp', -1)
        self.image2, self.rect2 = load_image('ddf.bmp', -1)
        self.image = self.image1
        self.rect = self.rect1
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.punching = 0
        self.moveUP = 0
        self.moveUPok = 1
        self.moveRIGHT = 0
        self.moveRIGHTok = 1
        self.moveDOWN = 0
        self.moveDOWNok = 1
        self.moveLEFT = 0
        self.moveLEFTok = 1
        self.flip = 0
        self.direction = 0

    def update(self):       
        if self.moveUP:
            if self.direction:
                self.image = self.image1
                self.direction = 0
                pygame.time.wait(100)
            elif self.moveUPok:
                self.rect.move_ip(0, -2)
            if self.rect.top < self.area.top:
                self.rect.move_ip(0, 2)
                self.moveUP = 0
        if self.moveRIGHT:
            if self.moveRIGHTok:
                self.rect.move_ip(2, 0)
            if self.rect.right > self.area.right:
                self.rect.move_ip(-2, 0)
                self.moveRIGHT = 0
        if self.moveDOWN:
            if not self.direction:
                self.image = self.image2
                self.direction = 1
                pygame.time.wait(100)
            elif self.moveDOWNok:
                self.rect.move_ip(0, 2)
            if self.rect.bottom > self.area.bottom:
                self.rect.move_ip(0, -2)
                self.moveDOWN = 0
        if self.moveLEFT:
            if self.moveLEFTok:
                self.rect.move_ip(-2, 0)
            if self.rect.left < self.area.left:
                self.rect.move_ip(2, 0)
                self.moveLEFT = 0

    def flipImage(self):
        self.image = pygame.transform.flip(self.image, 1, 0)
        self.image1 = pygame.transform.flip(self.image1, 1, 0)
        self.image2 = pygame.transform.flip(self.image2, 1, 0)

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, name):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(name, (255,255,255))
        self.rect.topleft = x, y
        
class Chimp(pygame.sprite.Sprite):
    """moves a monkey critter across the screen. it can spin the
       monkey when it is punched."""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.image, self.rect = load_image('chimp.bmp', -1)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = 250, 250
        self.dizzy = 0

    def update(self):
        "walk or spin, depending on the monkeys state"
        if self.dizzy:
            self._spin()
        else:
            if random.randint(0, 1):
                if random.randint(0, 1):
                    self._walk()

    def _walk(self):
        "move the monkey"
        self.rect.move_ip(random.randint(-3, 3), random.randint(-3, 3))
        
        if self.rect.left < self.area.left:
            self.rect.move_ip(10, 0)
        if self.rect.right > self.area.right:
            self.rect.move_ip(-10, 0)
        if self.rect.top < self.area.top:
            self.rect.move_ip(0, 10)
        if self.rect.bottom > self.area.bottom:
            self.rect.move_ip(0, -10)

    def _spin(self):
        "spin the monkey image"
        center = self.rect.center
        self.dizzy = self.dizzy + 12
        if self.dizzy >= 360:
            self.dizzy = 0
            self.image = self.original
        else:
            rotate = pygame.transform.rotate
            self.image = rotate(self.original, self.dizzy)
        self.rect = self.image.get_rect(center=center)
        
    def punched(self):
        "this will cause the monkey to start spinning"
        if not self.dizzy:
            self.dizzy = 1
            self.original = self.image       

def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
#Initialize Everything
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Danger Dudes')
    pygame.mouse.set_visible(0)

#Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))
    background.set_colorkey((255,255,255))

    background2 = pygame.Surface(screen.get_size())
    background2 = background2.convert()
    background2.fill((250, 250, 250))

#Display The Background
    screen.blit(background, (0, 0))
    pygame.display.flip()

#Prepare Game Objects
    clock = pygame.time.Clock()
    chimp = Chimp()
    dd = DD()
    block1 = Block(100, 100, 'block_square.bmp')
    block2 = Block(500, 200, 'block_square.bmp')
    block3 = Block(300, 300, 'block_circle.bmp')
    blocks = [block1.rect, block2.rect, block3.rect]
    allsprites = pygame.sprite.RenderPlain((dd, chimp, block1, block2, block3))
    view = pygame.Surface((40, 40))
    view = view.convert()
    view.fill((255,255,255))

    
#Main Loop
    while 1:
        clock.tick(60)
          
    #Handle Input Events
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == KEYDOWN and event.key == K_UP:
                dd.moveUP = 1
            elif event.type == KEYDOWN and event.key == K_RIGHT:
                dd.moveRIGHT = 1
                if dd.flip:
                    dd.flip = 0
                    dd.flipImage()
            elif event.type == KEYDOWN and event.key == K_DOWN:
                dd.moveDOWN = 1
            elif event.type == KEYDOWN and event.key == K_LEFT:
                dd.moveLEFT = 1
                if not dd.flip:
                    dd.flip = 1
                    dd.flipImage()
            elif event.type == KEYUP and event.key == K_UP:
                dd.moveUP = 0
            elif event.type == KEYUP and event.key == K_RIGHT:
                dd.moveRIGHT = 0
            elif event.type == KEYUP and event.key == K_DOWN:
                dd.moveDOWN = 0
            elif event.type == KEYUP and event.key == K_LEFT:
                dd.moveLEFT = 0 

        hitbox = dd.rect
        
        if dd.moveUP:
            if hitbox.move(0, -5).collidelist(blocks) != -1:
                dd.moveUPok = 0
            else:
                dd.moveUPok = 1
                
        if dd.moveDOWN:
            if hitbox.move(0, 5).collidelist(blocks) != -1:
                dd.moveDOWNok = 0
            else:
                dd.moveDOWNok = 1

        if dd.moveRIGHT:
            if hitbox.move(5, 0).collidelist(blocks) != -1:
                dd.moveRIGHTok = 0
            else:
                dd.moveRIGHTok = 1
                
        if dd.moveLEFT:
            if hitbox.move(-5, 0).collidelist(blocks) != -1:
                dd.moveLEFTok = 0
            else:
                dd.moveLEFTok = 1

        background.blit(view, dd.rect)
        
        if dd.moveUP:
            if dd.moveRIGHT:
                background.blit(view, dd.rect.move(30, -30))
            elif dd.moveLEFT:
                background.blit(view, dd.rect.move(-30, -30))
            else:
                background.blit(view, dd.rect.move(0, -40))
        elif dd.moveDOWN:
            if dd.moveRIGHT:
                background.blit(view, dd.rect.move(30, 30))
            elif dd.moveLEFT:
                background.blit(view, dd.rect.move(-30, 30))
            else:
                background.blit(view, dd.rect.move(0, 40))
        elif dd.moveRIGHT:
            background.blit(view, dd.rect.move(40, 0))
        elif dd.moveLEFT:
            background.blit(view, dd.rect.move(-40, 0))
                
        hitbox = dd.rect.inflate(-5, -5)
        if hitbox.colliderect(chimp.rect):
            chimp.punched()          
        
        allsprites.update()

    #Draw Everything
        screen.blit(background2, (0, 0))
        allsprites.draw(screen)
        screen.blit(background, (0, 0))
        pygame.display.flip()

#Game Over


#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    listener = listener()
    listener.start()
    main()
