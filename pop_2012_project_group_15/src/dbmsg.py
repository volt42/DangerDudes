import sys
from Tkinter import *

x=sys.stdin.readline()
root = Tk()
Label(root, text=x).pack()
root.mainloop()
