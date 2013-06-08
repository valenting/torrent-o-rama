import SocketServer
import random
from Downloader import *
import os
from SocketServer import ThreadingMixIn,TCPServer
import socket
from DatabaseManager import *
from MyParser import MyParser
from TorrentParser import TorrentInfo

import __builtin__
__builtin__.TorrentDict = {}

from tempfile import NamedTemporaryFile

from threading import Lock
__builtin__.mymutex = Lock()

class PhonyLock():
	def __init__(self):
		pass
	def acquire(self):
		pass
	def release(self):
		pass

class MyTCPServer():
	def __init__(self,host,port):
		self.HOST = host
		self.PORT = port
		ThreadingTCPServer.allow_reuse_address = True
		ThreadingTCPServer.address_family = socket.AF_INET6
		self.server = ThreadingTCPServer((self.HOST,self.PORT),MyTCPHandler)
	def start(self):
		self.server.serve_forever()


class MyTCPHandler(SocketServer.StreamRequestHandler):
	def handle(self):
		self.data = self.recv()
		self.questions = {"What is the capital of Romania?":"Bucharest",
					"What is the answer to life, the Universe...":"42",
					"How many legs does a three legged dog have?":"3",
					"What is the colour of a rose?":"red",
					"What is 2+3?":"5",
					"Are cats better then dogs?":"Yes",
					"Always Coca...":"Cola"}
		print "%s wrote:" % self.client_address[0]
		print self.data
		if "info"==self.data:
			self.info()
		if "login"==self.data:
			self.login()
		if "registerQ"==self.data:
			self.registerQ()
		if "register"==self.data:
			self.register()
		if "addtorrent"==self.data:
			self.addtorrent()
		if "gettorrent"==self.data:
			self.gettorrent()
		if "gettorrentlist"==self.data:
			self.gettorrentlist()
		if "getfile"==self.data:
			self.getfile()
		if "getdetails"==self.data:
			self.torrentdetails()
		if "removeTorrent"==self.data:
			self.removeTorrent()
		if "hello" in self.data:
			self.send("hello back")
			print "fuck?"
			
	def recv(self):
		return self.rfile.readline().strip()
	
	def send(self,bla):
		self.wfile.write(bla)
	
	def login(self):
		user = self.recv()
		password = self.recv()
		print user+" "+password
		mymutex.acquire()
		(valid,name,pswd,quota) = GetClientInfo(user)
		mymutex.release()
		if valid and pswd==password:
			self.send("ACK")
		else:
			self.send("NAK")
	def registerQ(self):
		q = random.choice(self.questions.keys())
		self.send(q)
		
	def register(self):
		user = self.recv()
		password = self.recv()
		question = self.recv()
		answer = self.recv()
		answer = answer.lower().strip()
		mymutex.acquire()
		(valid,name,pswd,quota) = GetClientInfo(user)
		mymutex.release()
		if valid:
			self.send("NAK")
			return
		elif self.questions[question].lower()==answer:
			mymutex.acquire()
			changePass(user,password)
			mymutex.release()
			self.send("ACK")
			return
		else:
			self.send("NAK")
	
	def removeTorrent(self):
		user = self.recv()
		torrent = self.recv()
		self.send("ACK")
		mymutex.acquire()
		eliminateTorrentOnUserDemand(user,torrent)
		count = getClientCountForTorrent(torrent)
		mymutex.release()
		print count
		if int(count)==0:
			print "eliminate"
			mymutex.acquire()
			eliminateTorrentFromDatabase(torrent)
			mymutex.release()
		
	def addtorrent(self):
		user_name = self.recv()
		torrent_name = self.recv()
		fno = int(self.recv())
		f_lst = []
		total_dim = 0
		# file sizes also?
		for i in range(fno):
			fname = self.recv()
			fdim = self.recv()
			f_lst.append((fname,fdim))
			total_dim += long(fdim)
		tsize = long(self.recv())
		print tsize
		# transfer torrent
		# f = open("file.torrent","wb")
		f = NamedTemporaryFile("wb",delete=False)
		while (tsize>0):
			s = 1024
			if (tsize<1024):
				s = tsize
			f.write(self.rfile.read(s))
			tsize-=1024
		f.close()
		mymutex.acquire()
		(valid,clientname,pwd,quota) = GetClientInfo(user_name)
		q = getGlobalQuota()
		qt = getTotalQuota()
		mymutex.release()
		print total_dim
		
		if long(quota)+total_dim>q:
			self.send("NAK")
			return
		rc = add_torrent(f.name)
		print rc
		
		info = TorrentInfo(f.name)
		tupluri = []
		print "ici--"
		for i in info.files:
			plul = ( i["path"], str(i["size"]) )
			tupluri.append(plul)			
		mymutex.acquire()
		addTorrentToDatabase(info.name,tupluri)
		for (fisier,cev) in f_lst:
			addTorrentFileToUser(user_name, info.name, fisier)
		mymutex.release()
		
		self.send("ACK")
		self.recv()
		
		print "done"
	
	def info(self):
		torrent_name = self.recv()
		try:
			rc = MyParser(torrent_name)
			self.send(rc.get_state()+" "+rc.get_progress())
		except:
			self.send(" ")
		print "---"
		print rc.get_progress()
		if "100%" in rc.get_progress():
			if torrent_name in TorrentDict.keys() and TorrentDict[torrent_name]!="100%":
				print "full"
				mymutex.acquire()
				endServerDownloadFullTorrent(torrent_name)
				mymutex.release()
		TorrentDict[torrent_name]=rc.get_progress().split()[0]


	def torrentdetails(self):
		torrent_name = self.recv()
		try:
			rc = MyParser(torrent_name)
			self.send("ACK")
			self.recv()
		except:
			self.send("NAK")
			self.recv()
			return
		(seeds,peers,avail) = rc.get_info()
		self.send(seeds)
		self.recv()
		self.send(peers)
		self.recv()
		self.send(avail)
		self.recv()
		ID = rc.get_ID()
		self.send(ID)
		print "OK1"
		self.recv()
		print "OK2"
		eta = rc.get_eta()
		self.send(eta+" ")
		print eta
		print "OK3"
		self.recv() #
		print "OK4"
		self.send(rc.get_downspeed())
		print "OK5"
		self.recv()
		self.send(rc.get_upspeed())
		self.recv()
		mymutex.acquire()
		count = getClientCountForTorrent(torrent_name)
		mymutex.release()
		self.send(str(count))
		self.recv()
		print "done"
			
	def gettorrent(self):
		torrent_name = self.recv()
		basepath = "/home/icecold/"
		path = basepath+torrent_name
		try: dirList = os.listdir(path)
		except: 
			self.send("NAK")
			return
		self.send(str(len(dirList))) # Send NrFisiere
		self.recv() 				# OK
		for filename in dirList:
			self.send(filename) #Send NUME
			self.recv()			# OK
			size = long(os.stat(path+"/"+filename).st_size)
			self.send(str(size)) 	#send size
			self.recv()				#OK
			f = open(path+"/"+filename,"rb") # sau path+filename???
			while size>0:			# trimite fisierul. Chunk de 1024
				part = f.read(1024)
				self.send(part)
				self.recv()
				size-=1024
			f.close()
			
	def getfile(self):
		torrent_name = self.recv()
		file_name = self.recv()
		basepath = "/home/icecold/"
		path = basepath+file_name
		try: #dirList = os.listdir(path)
			print path
			size = long(os.stat(path).st_size)
			f = open(path,"rb")		
		except: 
			self.send("NAK")
			return
		print "here"
		self.send(str(size)) # OK
		self.recv()
		print "here2"
		while size>0:
			part = f.read(1024)
			self.send(part)
			self.recv()
			size-=1024
		f.close()
	
	def gettorrentlist(self):
		username = self.recv()
		mymutex.acquire()
		mydic = getClientTorrentList(username)
		mymutex.release()
		# print username
		# print mydic
		self.send(str(len(mydic.keys()))) # Send NrFisiere
		self.recv() 				# OK
		for key in mydic.keys():
			self.send(key) #Send NUME
			self.recv()			# OK
			size = len(mydic[key])
			self.send(str(size)) 	#send list size
			self.recv()				#OK
			lista = mydic[key]
			for i in lista:
				nume,ceva,altceva = i
				self.send(nume) # file name
				self.recv()
				self.send(ceva) # file size
				self.recv()
    	
class ThreadingTCPServer(ThreadingMixIn, TCPServer):
	def server_bind(self):
		self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, False)
		SocketServer.TCPServer.server_bind(self)

if __name__ == "__main__":
	try:
		server = MyTCPServer('',9999)
	except:
		server = MyTCPServer('',9998)
	server.start()
	
	
