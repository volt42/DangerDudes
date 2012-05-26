import sys,time,os
from Tkinter import *

def msg(message):
    x=time.gmtime()
    x=str(os.getpid())+', '+str(x[3])+'.'+str(+x[4])+'.'+str(x[5])+': '
    message=x + message
    root = Tk()
    Label(root, text=message).pack()
    root.mainloop()

class popup():
    _msg =""    
    def __add__(self,msg):
        x=time.gmtime()
        x=str(x[3])+'.'+str(x[4])+'.'+str(x[5])+': '
        self._msg+=x+msg+'\n'
        
    def __eq__(self,msg):
        self._msg=""
        self.__add__(msg)
