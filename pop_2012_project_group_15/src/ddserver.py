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
import random, math, os
from erlport import Port,Protocol,String
import threading,sys

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
		
    def listener(self):
        self.run(Port(use_stdio=True))

    def sendworldinfo(self,target,x,y):
        send_to_client(self.worldinfo(x,y,200,200))

    #Incomming functions

    def handle(self,port,message):
        if(Atom(message) == "set_output"):
            self._outPort = port
        elif(Atom(message) == "stop"):
            running = False

        msg=message.splitlines()
        if len(msg) <2:
            _outPort.write("Tell me more")
        elif msg[0] == "CONNECT":
            self.handleconnect()
        port.write("I am very greatful for: " + msg[len(msg)-1])

    #This function needs to be fixed
    def init(self,width,height):
        self._width =width
        self._height=height
        self._world={}
        self._objects={}
              
    def handleconnect(self,port):
        obj = gameobject()
        obj.health=100
        obj.type ='PLAYER'
        obj.action="IDLE"

        for i in xrange(ord('A'),ord('z')):
            if not self._objects.has_key(chr(i)):
                obj.id=chr(i)
                self._objects[chr(i)]=obj
                break

        #if client is unlucky he will not get a spot but no inf loops here at least
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
                if len(i) != 3:
                    return 'BAD MOVE '+i
                self.moveobject(self._objects[id].id,int(i[1]),int(i[2]))

            

    def setaction(self,id,action):
        if not self._objects.has_key(id):
            return False
        self._objects[id].action = action

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
                
                #print 'Distance ' +str(self._world[i])+'<->'+str(id)+' '+str(int(dist))+' '+str(Size[self._objects[id].type])+','+str(Size[self._objects[targetsquare[i]].type])
                if dist < (Size[self._objects[id].type]+Size[self._objects[targetsquare[i]].type])/2:
                    #print str(i)+' x,y:'+str(x)+','+str(y)+';'+str(i)+'dist= '+str(dist)
                    return True
        return False

    def handlemoverequest(self,obj,x,y):
        if objectrules.has_key(obj) == True:
            for i in self._world.keys():
                if self._world[i]==id:
                    maxspeed=objectrules[self._world[i]]['SPEED']
                    speed= math.sqrt((x-i[0])*(x-i[0]) +(y-i[1])*(y-i[1]))
                    if speed > maxspeed:
                        return False
                    else:                    
                        self.addobject(obj,x,y)
                    self._world.pop(i)
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
#                        print str(x) +' '+str(y)
                        s+=self._world[(x,y)][0]
                else:
                    s+=' '
            print('#'+s+'#')
        print '#'*(self._width+2)

    def clearprint(self):
        os.system('clear')
        self.printworld()
    

    def tic(self):
        #update every object
        for i in self._objects.keys():
            self.executeaction(self._objects[i].id)

    
if __name__ == "__main__":
    proto = ddserver()
    # Run protocol with port open on STDIO
    proto.init(1000,1000)
    proto.startListener()
	
    while(proto.running == True):
        proto.tic()
