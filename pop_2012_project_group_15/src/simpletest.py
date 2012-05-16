from erlport import Port, Protocol, String
import time

# Inherit custom protocol from erlport.Protocol
class HelloProtocol(Protocol):

	def wait(self):
		var = 0

    # Function handle_NAME will be called for incoming tuple {NAME, ...}
	def handle(self, port, n):
		# String wrapper forces name to be a string instead of a list
		
		port.write([0,130,243,179,54])
		x = 5
		while(x > 0):
			port.write([1,"hello"])
			x -= 1
			time.sleep(1)


if __name__ == "__main__":

	proto = HelloProtocol()
	# Run protocol with port open on STDIO
	proto.run(Port(use_stdio=True))