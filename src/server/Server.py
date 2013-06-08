from DatabaseManager import *
from MyParser import MyParser
from TCPServ import *

class Server:
	def __init__(self):
		try:
			initialiseDatabase()
		except:
			print "initDB"
		try:
			self.server = MyTCPServer('',9999)
			print "9999"
		except:
			self.server = MyTCPServer('',9998)
			print "9998"
		self.server.start()
	

if __name__ == "__main__":
	Server()
