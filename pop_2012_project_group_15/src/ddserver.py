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
    _lastsent ={}
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
                for i in xrange(0,8):
                    part+=x[i]+'\n'
                #err(str(part))
                self._outPort.write([id,part])
                part="CONTINUE\n"
                for i in xrange(8,len(x)):
                    part+=x[+i]+'\n'
                self.threadsendaftersleep(id,part,0.025)
                return True
            self._outPort.write([id,info])
            return True

    def mvworld(self,world,x,y):
        value={}
        for i in world.keys():
            value[(i[0]+x,i[1]+y)]=world[i]
        return value

    def sendtoplayer(self,id):
        lastx=self._lastsent[id][1]
        lasty=self._lastsent[id][2]
        curr=self._objects[id]
        currentworld=self.worldinfo(curr.x-200,curr.y-200,400,400)
        lastworld=self._lastsent[id][0]
        if lastworld==currentworld:
            return True

        sendinfo=""
        
        #compare to the moved version of the old world if appropriate
        if not (curr.x == lastx and curr.y==lasty):
            sendinfo+='MVWORLD '+str(lastx-curr.x)+' '+str(lasty-curr.y)+'\n'
            lastworld=self.mvworld(lastworld,lastx,lasty)
          #  err('lastworld: '+str(lastworld))
          #  err('currentworld ' +str(currentworld))
            if lastworld==currentworld:
                return self.send(id,sendinfo)
           # msg(sendinfo)

        self._lastsent[id][0]={}
        self._lastsent[id][1]=curr.x
        self._lastsent[id][2]=curr.y
        for i in currentworld.keys():
            if lastworld.has_key(i):
                if not currentworld[i]==lastworld[i]:
                    sendinfo+=self._objects[currentworld[i]].toString()
                self._lastsent[id][0][i]=currentworld[i]
            else:
                sendinfo+=self._objects[currentworld[i]].toString(curr.x-200,curr.y-200)
       # err("setting lastsent:  "+str(currentworld))
        self._lastsent[id][0]=currentworld
   #     err("||"+sendinfo)
        return self.send(id,sendinfo)

    def threadsendaftersleep(self,id,info,time):
        t=threading.Thread(target=self.sendaftersleep, args=(id,info,time,))
        t.start()

    def sendaftersleep(self,id,info,t):
        time.sleep(t)
        self.send(id,info)
    
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
        obj.size=50
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
                self._lastsent[id]=[{},x,y]
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
       # err("Setting new action: "+str(id)+' '+str(action))
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
 
    def worldtostring(self,world):
        returnvalue=""
        for i in world.keys():
            returnvalue+=self._objects[self._world[i]].toString()
        return returnvalue
        
    def subworld(self,x,y,width,height):
        values=self.worldinfo(x,y,width,height)
        returnvalue=""
        for i in values.keys():
            returnvalue+=self._objects[self._world[i]].toString(x,y)
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
                #MOVE EXECUTE ACTION UP ONE level!
                self.executeaction(self._objects[i].id)
                if send==True:
                    self.sendtoplayer(i)
                else:
                    pass
#                    self.send(i,self.subworld(self._objects[i].x-200,self._objects[i].y-200,400,400))
    
if __name__ == "__main__":
    proto = ddserver()
    proto.init(1000,1000)
    proto.startListener()
    x=0
    while(proto.running == True):
        t=time.time()
        t+=0.02-time.time()
        if x>2:
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
