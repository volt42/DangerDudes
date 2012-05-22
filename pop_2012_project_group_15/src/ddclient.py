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
###########################################################################
from erlport import Protocol, Port, String



class ddclient(Protocol):
    #internal variables
    _world = {}
    _objects = {}
    _width = 0
    _height = 0
    _port=0
    _name=""

    #Outgoing functions
    def connect(self,address):
        print('Lets do this later when we know how to!')
        
    def actionrequest(self,action):
        print('define the actionrequest function')
        global player_action
        player_action=action

    def init(self,port,name):
        self._port=port
        self._name=name
        print str(name) + ' ' +str(self._name)

    def handleworldinfo(self,worldinfo):
        print("Handle the new environment information")
        _world=worldinfo
    
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
    client=ddclient()
    client.connect(serveraddress)
    
    


if __name__ == "__main__":
    main()
