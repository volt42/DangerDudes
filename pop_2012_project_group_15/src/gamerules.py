from dbmsg import msg

class Gameobj():
    id=-1
    type =""
    x=-1
    y=-1
    angle=0
    size=0
    maxspeed=0
    image=1
    action='IDLE'
    

class Player(Gameobj):
    health=100
    maxspeed=3
    image=1
    size=10
    type="PLAYER"

    def isPlayer(self,str):
        s=str.split(' ')
        if not s[0]=='PLAYER':
            return False
        return True
    def validCmd(self,cmd):
        c=cmd.split(' ')
        if c[0]=='IDLE':
            return True
        if c[0]=='MOVE':
            if type(int(c[1]))==type(1) and type(int(c[2]))==type(1):
                return True
            return False
        if c[0] =='PLANTBOMB':
            return True
        if c[0]=='FIRE':
            return True
        return False

    def setCmd(self,cmd):
        if self.validCmd(cmd):
            self.action=cmd
            return True
        return False

    def getCmd(self):
        s=self.action.split(' ')
        if s[0]=='MOVE':
            return [s[0], int(s[1]),int(s[2])]
        else:
            return [s[0]]

    def moveCmd(self,x,y):
        return 'MOVE '+str(x)+' '+str(y)
    def plantbombCmd(self):
        return 'PLANTBOMB '
    def firebulletCmd(self):
        return 'FIRE'

    def toString(self,xoffset=0,yoffset=0):
        value=self.type+' '
        value+=str(self.id)+' '
        value+=str(self.x-xoffset)+' '
        value+=str(self.y-yoffset)+' '
        value+=str(self.angle)+' '
        value+=str(self.health)+' '
        value+=str(self.image)+ '\n'
        return value

    def fromString(self,string):
        try:
            if not self.isPlayer(string):
                return False
            d=string.split(' ')
            self.type=d[0]
            self.id =int(d[1]) 
            self.x =int(d[2]) 
            self.y =int(d[3]) 
            self.angle=int(d[4])
            self.health =int(d[5]) 
            self.image =int(d[6]) 

            self.height =20
            self.width = 20
        except:
            msg("player:fromString got bad values: \n-|"+string+'|-')
        
    def __str__(self):
        return self.image

class Bomb(Gameobj):
    timeleft=150
    size=5
    image=1
    type='BOMB'

    def isBomb(self,str):
        s=str.split(' ')
        if not s[0]=='BOMB':
            return False
        return True

    def toString(self):
        value=self.type+' '
        value+=str(self.id)+' '
        value+=str(self.x)+' '
        value+=str(self.y)+' '
        value+=str(self.timeleft)+' '
        value+=str(self.image)+ '\n'
        return value

    def fromString(self,string):
        s=string.split(' ')
        if not s[0] == self.type:
            msg("bomb.fromString got something that was not a stone:\n"+string)
        self.id = int(s[1])
        self.x = int(s[2])
        self.y = int(s[3])
        self.timeleft = int(s[4])
        self.image = int(s[5])

class Stone(Gameobj):
    health=300
    size=50
    image=1
    type='STONE'

    def isStone(self,str):
        s=str.split(' ')
        if not s[0]=='STONE':
            return False
        return True

    def toString(self):
        value=self.type+' '
        value+=str(self.id)+' '
        value+=str(self.x)+' '
        value+=str(self.y)+' '
        value+=str(self.health)+' '
        value+=str(self.image)+ '\n'
        return value

    def fromString(self,string):
        s=string.split(' ')
        if not s[0] == self.type:
            msg("stone.fromString got something that was not a stone:\n"+string)
        self.id = int(s[1])
        self.x = int(s[2])
        self.y = int(s[3])
        self.health = int(s[4])
        self.image = int(s[5])



