from erlport import Port, Protocol, String
import time

# Inherit custom protocol from erlport.Protocol
class HelloProtocol(Protocol):

	def wait(self):
		var = 0

	def handle(self, port, n):
			port.write([1,"hello"])
			time.sleep(1)


if __name__ == "__main__":

	proto = HelloProtocol()
	# Run protocol with port open on STDIO
	proto.run(Port(use_stdio=True))