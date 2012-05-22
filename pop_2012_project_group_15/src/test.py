import ddserver,ddclient,time,gamerules,random
import os,sys,subprocess

reload(ddserver)
reload(ddclient)
reload(gamerules)

d=ddserver.ddserver()
d.init(100,50)
d.clearprint()


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
            
            
def pyloop():
    x={}
    child = subprocess.Popen(["python", "danger_dudes.py"],stdin=subprocess.PIPE)
    for i in xrange(0,int(t/f)):
        x[i]=d.handleconnect(1)
        for ii in xrange(0,i):
            d.setaction(x[ii],"MOVE "+str(int(random.random()*4-2))+' '+str(int(random.random()*4-2)))
        child.stdin.write(d.maptopygame())
        d.tic()
        time.sleep(f)
