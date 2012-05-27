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
import threading,sys
from dbmsg import err, exc

class ddserver(Protocol):
    #internal variables
    _world = {}
    _objects = {}
    _width = 0
    _height = 0
	
    running = True
	
    _outPort = None
	
    # Outgoing functions
    def startListener(self):
        listen = threading.Thread(target=self.listener)
        listen.daemon = True
        listen.start()
		
    def listener(self):
        self.run(Port(use_stdio=True))

    def send(self,id,msg):
        if self._outPort:
            err("Sending ID: "+str(id)+". msg: "+str(msg)+"\n")
            self._outPort.write([id,msg])

    def sendworldinfo(self,target,x,y):
        send_to_client(self.worldinfo(x,y,200,200))

    #Incomming functions
        
    def handle(self,port,message):
        if Atom(message[0]) == "init":
            self._outPort = port
        elif Atom(message[0]) =="connect":
            self.connect(message[1])
        elif Atom(message[0])=="data":
            err(str(message[2])+'\n'+str(message[1])+'\n'+str(message[0])+'\n'+str(message))
            self.setaction(int(message[1]),message[2])
        else:
            err("Server:handle() got something it did not understand: "+str(message))
   
     #This function needs to be fixed
    def init(self,width,height):
        self._width =width
        self._height=height
        self._world={}
        self._objects={}
              
    def connect(self,id):
        obj = gameobject()
        obj.health=100
        obj.type ='PLAYER'
        obj.action="IDLE"
        obj.id=id
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
            print 'bad key'
            return False
        x=self._objects[id].action.splitlines()
        while x != []:
            i=x.pop().split(' ')
            if i[0]=='IDLE':
                continue
            elif i[0]=='MOVE':
                try:
                    self.moveobject(self._objects[id].id,int(i[1]),int(i[2]))
                except:
                    print 'Bad values'
                    
    def setaction(self,id,action):
        err("Setting new action: "+str(id)+' '+str(action))
        try:
            if not self._objects.has_key(id):
                return False
            i=action.split(' ')
            if i[0] =='MOVE':
                speed=math.sqrt((int(i[1]))**2 + (int(i[2]))**2)
                if speed < MaxSpeed[self._objects[id].type]:
                    self._objects[id].action = action
        except:
            pass
            err('this is bullshit, send better stuff to setaction!')

    #Internal functions
    def moveobject(self,id,dx,dy):
        if(type(id)!=type('a')):
            return False
        x=self._objects[id].x+dx
        y=self._objects[id].y+dy
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
        
        
    def addobject(self,obj,x,y): 
        if(self.collision(obj,x,y) == False):
            self._world[(x,y)] = obj
            return True
        return False

    def collision(self,id,x,y,radius=5):
        if not (self._objects.has_key(id) and 0<=x<self._width and 0<=y<self._height):
            return 'Bad argument'
        size=Size[self._objects[id].type]
        targetsquare=self.worldinfo(int(x-radius),int(y-radius),int(x+radius),int(y+radius))
        #test distance to all objects within the radius
        for i in targetsquare.keys():
            if targetsquare[i] == id:
                #print i
                continue
            else:
                #Square collision detection
                #dist = abs(x-i[0])+abs(y-i[1])
                #Circular collision detection
                dist= math.sqrt((x-i[0])**2+(y-i[1])**2)
                if dist < (Size[self._objects[id].type]+Size[self._objects[targetsquare[i]].type])/2:
                    return True
        return False

    def world(self):
        return self._world

    def subworld(self,x,y,width,height):
        values=self.worldinfo(x,y,width,height)
        returnvalue=""
        for i in values.keys():
            returnvalue+='Player'+' '+str(i[0])+' '+str(i[1])+'\n'
        return returnvalue
            
    def worldinfo(self,x,y,width,height):
        value={}

        # This is not effective at all, but it works
        for i in self._world.iterkeys():
            if x <= i[0] <= x+width and y <= i[1] <= x+height:
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
    

    def tic(self):
        for i in self._objects.keys():
            obj=self._objects[i]
            self.executeaction(self._objects[i].id)
            self.send(obj.id,self.subworld(obj.x-100,obj.y-100,200,200))
    
if __name__ == "__main__":
    proto = ddserver()
    proto.init(1000,1000)
    proto.startListener()
    while(proto.running == True):
        t=time.time()
        proto.tic()
        t+=5-time.time()
        if t>0:
            time.sleep(t)
        else:
            pass
            err('Server overload, add more servers!')
