###########################################################################
#                                                                         #
#                                                                         #
#                               ddserver                                  #
#                                                                         #
#                                                                         #
###########################################################################
#                                                                         #
#    Game server. Handles the game world and all active objects living    #
#    in the world.                                                        #
#                                                                         #
###########################################################################    
#                                                                         #
#   Communication to ddobject                                             #
#                                                                         #
#      EnvInfo()                                                          #
#                                                                         #
#                                                                         #
###########################################################################
#                                                                         #
#   Internal architecture                                                 #
#    * The world map is a represented as a list of non-empty map squares  #
#                                                                         #
###########################################################################
from gamerules import *
import random, math, os,time
from erlport import Port,Protocol,String,Atom
import threading,sys, dbmsg
from dbmsg import err, exc, msg

class ddserver(Protocol):
    #internal variables
    _world = {}
    _objects = {}
    _width = 0
    _height = 0
    running = True
	
    _outPort = None
	
    #Outgoing functions
    def startListener(self):
        listen = threading.Thread(target=self.listener)
        listen.daemon = True
        listen.start()
		
    def listener(self):
        self.run(Port(use_stdio=True))

    def send(self,id,info):
        if self._outPort:
            x=info.splitlines()
            if(len(x)>7):
                part=""
                for i in xrange(0,7):
                    part+=x[i]+'\n'
                err(str(part))
                self._outPort.write([id,part])
                part="CONTINUE\n"
                for i in xrange(7,len(x)):
                    part+=x[+i]+'\n'
                time.sleep(0.025)
                self.send(id,part)
                return True
#            err('Send id: '+str(id))
#            err('Message Length: '+str(len(str(info))))
#            if(len(str(info)) >255):
#                err("to much data "+str(len(str(info))))
#                return False
            self._outPort.write([id,info])
            return True


    def sendworldinfo(self,target,x,y):
        send_to_client(self.worldinfo(x,y,200,200))

    #Incomming functions
        
    def handle(self,port,message):
        #msg(str(message))

        if Atom(message[0]) == "init":
            self._outPort = port
        elif Atom(message[0]) =="connect":
            self.connect(message[1])
        elif Atom(message[0])=="data":
            #msg(str(message))
            #err('handle: '+str(message[2])+'\n'+str(message[1])+'\n'+str(message[0])+'\n'+str(message))
            self.setaction(int(message[1]),message[2])
        else:
            err("Server:handle() got something it did not understand: "+str(message))

    #does no collision detection
    def addStone(self, x, y, size):
        obj = Stone()
        obj.x = x
        obj.y = y
        obj.image = random.randint(1,3)
        obj.size=size
        for i in range(200, 1000):
            if not self._objects.has_key(i):
               obj.id=i
               self.addobject(obj)
               break
   
    #This function needs to be fixed
    def init(self,width,height):
        self._width =width
        self._height=height
        self._world={}
        self._objects={}
        
        class count():
            x=100
            def next(self):
                self.x+=1
                return self.x
        c=count()
        for i in range(1,height,int(height/10)):
           # break
            stone=Stone()
            stone.x=1
            stone.y=i
            stone.size=75
            stone.id=c.next()
            self._world[(stone.x,stone.y)]=stone.id
            self._objects[stone.id]=stone

        for i in range(1,height,int(height/10)):
           # break
            stone=Stone()
            stone.x=self._width-1
            stone.y=i
            stone.size=75
            stone.id=c.next()
            self._world[(stone.x,stone.y)]=stone.id
            self._objects[stone.id]=stone


        for i in range(1,width,int(width/10)):
           # break
            stone=Stone()
            stone.x=i
            stone.y=self._height-1
            stone.size=75
            stone.id=c.next()
            self._world[(stone.x,stone.y)]=stone.id
            self._objects[stone.id]=stone
            
        for i in range(1,width,int(width/10)):
           # break
            stone=Stone()
            stone.x=i
            stone.y=1
            stone.size=75
            stone.id=c.next()
            self._world[(stone.x,stone.y)]=stone.id
            self._objects[stone.id]=stone

             
    def connect(self,id):
        obj = Player()
        obj.id=id
        obj.lastsent=""
        self._objects[id]=obj
        if not self._objects.has_key(obj.id):
            return False
        for i in xrange(0,50):
            x=int(random.random()*self._width)
            y=int(random.random()*self._height)
            if(self.collision(obj.id,x,y)==False):
                self._world[(x,y)]=obj.id
                self._objects[obj.id].x=x
                self._objects[obj.id].y=y
                return obj.id
        return False
    
    def executeaction(self,id):
        if not self._objects.has_key(id):
            err('bad key')
            return False
        
        x=self._objects[id].getCmd()
        if not x:
            return False
        if x[0]=='MOVE':
            self.moveobject(id,x[1],x[2])
            try:
                self._objects[id].angle=x[3]
            except:
                self._objects[id].angle=0
                
            return True
        if x[0]=='PLANTBOMB':
            return True
        if x[0]=='FIRE':
            return True
        if x[0]=='IDLE':
            return True

        msg("executeaction do not know how to handle:\n"+self._objects[id].action)
        return False
                    
    def setaction(self,id,action):
        err("Setting new action: "+str(id)+' '+str(action))
        if not self._objects.has_key(id):
            return False
        self._objects[id].setCmd(action)

    #Internal functions
    def moveobject(self,id,dx,dy):
        x=self._objects[id].x+dx
        y=self._objects[id].y-dy
        if not (0<x<self._width and 0<y<self._height):
            return False
        if not self.collision(id,x,y):
            if(self._world.values().count(id)>0):
                self._world.pop((self._objects[id].x,self._objects[id].y))
            self._objects[id].x=x
            self._objects[id].y=y
            self._world[(x,y)] =id
            return True
        return False
        
        
    def addobject(self,obj): 
        if(self.collision(obj,obj.x,obj.y) == False):
            self._world[(obj.x,obj.y)] = obj.id
            self._objects[obj.id]=obj
            return True
        return False

    def collision(self,id,x,y,radius=100):#radius tells us the size of the area we should check for collisions
        if not (self._objects.has_key(id) and 0<=x<self._width and 0<=y<self._height):
            return True
#        err("Collision test step 1 complete\n")
        size=self._objects[id].size
        targetsquare=self.worldinfo(int(x-radius),int(y-radius),int(x+radius),int(y+radius))
        #test distance to all objects within the radius
        for i in targetsquare.keys():
            if targetsquare[i] == id:
                #print i
                continue
            else:
                #Square collision detection:
                dist = abs(x-i[0])+abs(y-i[1])
#                err("dist: "+str(dist))
#                err("x,y= "+str(x)+', '+str(y))
#                err("i[0],i[1]= "+str(i[0])+', '+str(i[1]))
                #Circular collision detection:
                #dist= math.sqrt((x-i[0])**2+(y-i[1])**2)
                if dist < (self._objects[id].size+self._objects[targetsquare[i]].size)/2:
                    return True
        return False

    def world(self):
        return self._world

    def subworld(self,x,y,width,height):
        values=self.worldinfo(x,y,width,height)
#        err(str(values));
#        err("||||||||||\n")
#        err(str(self.worldinfo))
#        err("---------\n")
        returnvalue=""
        for i in values.keys():
            returnvalue+=self._objects[self._world[i]].toString(x,y)
   #     err(str(self._objects))
   #     err(returnvalue)
        return returnvalue
            
    def worldinfo(self,x,y,width,height):
        value={}

        # This is not effective at all, but it works
        for i in self._world.iterkeys():
            if x <= i[0] <= x+width and y <= i[1] <= y+height:
                value[i]=self._world[i]
        return value

    ##stuff pygame needs to know
    def mapsizetopygame(self):
        return str(self._width)+' '+str(self._height)
    def maptopygame(self):
        value=""
        for i in self._world.iterkeys():
            value +=self._objects[self._world[i]].type+ ' '+str(i[0])+' '+str(i[1])+' '+'\n'
        return value

    #debugprint
    def printworld(self):
        print '#'*(self._width+2)
        for y in xrange(0,self._height):
            s=''
            c=' '
            for x in xrange(0,self._width):
                if(self._world.has_key((x,y))):
                    if(type(self._world[x,y]) == type(1)):
                        s+='#'
                    else:
                        s+=self._world[(x,y)][0]
                else:
                    s+=' '
            print('#'+s+'#')
        print '#'*(self._width+2)

    def clearprint(self):
        os.system('clear')
        self.printworld()
    

    def tic(self,send=True):
        for i in self._objects.keys():
            obj=self._objects[i]

            if obj.type == "PLAYER":
                self.executeaction(self._objects[i].id)
                if send==True:
                    x=self.subworld(obj.x-200,obj.y-200,400,400)
                    if not x==self._objects[i].lastsent:
                        self._objects[i].lastsent=x
                        self.send(obj.id,x)
           # err("\nSubworld: " +self.subworld(obj.x-200,obj.y-200,400,400))
           # err("\nObj: x:"+ str(obj.x)+' y:'+str(obj.y)+' id:'+str(obj.id))
    
if __name__ == "__main__":
    proto = ddserver()
    proto.init(1000,1000)
    proto.startListener()
    x=0
    while(proto.running == True):
        t=time.time()
        t+=0.02-time.time()
        if x>5:
            proto.tic(True)
            x=0
        else:
            proto.tic(False)
            x+=1
        if t>0:
            time.sleep(t)
        else:
            pass
            err('Server overload, add more servers!')
