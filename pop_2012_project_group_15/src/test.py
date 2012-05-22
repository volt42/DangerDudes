import ddserver,ddclient,time,gamerules,random
import os,sys,subprocess
from threading import Thread

reload(ddserver)
reload(ddclient)
reload(gamerules)

d=ddserver.ddserver()
d.init(100,50)
#d.clearprint()


def loop(t=5,f=0.25):
    x={}
    
    for i in xrange(0,int(t/f)):
        x[i]=d.handleconnect(1)
        for ii in xrange(0,i):
            d.setaction(x[ii],"MOVE "+str(int(random.random()*4-2))+' '+str(int(random.random()*4-2)))
        d.clearprint()
        d.tic()
        time.sleep(f)
    

def coordcheck():
    worldvalues=d._world.values()
    for i in d._objects.iterkeys():
        if not i in worldvalues:
            print 'World position missing: ' + str(i)
        (x,y)=(d._objects[i].x,d._objects[i].y)
        if not i == d._world[(x,y)]:
            print 'Coords do not match: '
            print '_objects[i]: '+str(d._objectx[i].id)+' ' +str(d._objectx[i].x)+' '+str(d._objectx[i].y)
            print '_world[(x,y)]: ' +str(d._world[(x,y)].id)
            
         

def pyloop(t=5,f=0.2):
    bluff=[]
    child=subprocess.Popen(["python", "danger_dudes.py"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    x={}

    class listener(Thread):
        def __init__(self):
            Thread.__init__(self)
            def run(self):
                while True:
                    if len(bluff) >0:
                        print 'hej'
                        bluff.pop
                        bluff.append(child.stdin.readline())

    listen=listener()
    listen.daemon=True
    listen.start()

    for i in xrange(0,int(t/f)):
        x[i]=d.handleconnect(1)
        for ii in xrange(0,i):
            d.setaction(x[ii],"MOVE "+str(int(random.random()*4-2))+' '+str(int(random.random()*4-2)))
            
        child.stdin.write(d.maptopygame())
        if(len(bluff)>0):
            print bluff
            bluff.pop
        d.tic()
        time.sleep(f)
    child.kill()
