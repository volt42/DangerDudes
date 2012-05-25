import sys,time
from Tkinter import *

def msg(message):
    message= str(time.time()) +':' + message
    root = Tk()
    Label(root, text=message).pack()
    root.mainloop()
