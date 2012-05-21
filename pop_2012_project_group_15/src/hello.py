from erlport import Port, Protocol, String
import os, sys, subprocess

child = subprocess.Popen(["c://python27//python.exe", "danger_dudes.py"], stdin=subprocess.PIPE)

class HelloProtocol(Protocol):

	
    def handle_hello(self, name):
        if name == 'K_RIGHT':
            child.stdin.write('RIGHT\n')
        elif name == 'K_DOWN':
            child.stdin.write('DOWN\n')
        elif name == 'K_DOWN_0':
            child.stdin.write('DOWN_0\n')
                
        return "Hello, %s" % str(name)
    
if __name__ == "__main__":
    proto = HelloProtocol()
    proto.run(Port(use_stdio=True))
