import socket
import sys
import os

from threading import *

class TCPClient():
	''' Initializeaza clientul cu ADRESA si PORT '''
	def __init__(self,host,port):
		self.HOST = host
		self.PORT = port
	
	''' Trimite o comanda oarecare si returneaza raspunsul '''
	def send_command(self,command):
		self.init()
		self.send(command)
		rec = self.recv()
		self.close()
		return rec
	
	''' Initiaza conexiunea '''
	def init(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.HOST, self.PORT))
	
	''' Inchide conexiunea '''
	def close(self):
		self.sock.close()
	
	''' Trimite un sir de caractere '''
	def send(self,string):
		self.sock.send(string+"\n")
	
	''' Primeste un mesaj de maxim 1024 caractere '''
	def recv(self):
		return self.sock.recv(1024)
	
	''' Realizeaza inregistrarea clientului '''
	def login(self,user,password):
		self.init() 		# initializare
		self.send("login")	# nume comanda
		self.send(user)		# trimite USERNAME
		self.send(password)	# trimite PAROLA
		rec = self.recv()	# asteapta raspunsul
		self.close()		# inchide conexiunea
		return rec			# returneaza raspunsul
	
	''' Primeste o intrebare de la server '''
	def registerQ(self):
		self.init()
		self.send("registerQ")
		q = self.recv()
		self.close()
		return q
	
	''' Realizeaza inregistrarea utilizatorului '''
	def register(self,user,password,question,answer):
		self.init()
		self.send("register")
		self.send(user)
		self.send(password)
		self.send(question)
		self.send(answer)
		r = self.recv()
		self.close()
		return r
	
	''' Trimite un torrent catre server '''
	def addtorrent(self,torrent_name,file_list,file_name,username="default"):
		try: # se verifica existenta fisierului
			f = open(file_name,"rb") 
		except:
			return "NAK"
		print "add torrent; user: "+username
		self.init()
		self.send("addtorrent")
		self.send(username)
		self.send(torrent_name)
		self.send(str(len(file_list))) # trimite lungimea listei de fisiere
		for i in range(len(file_list)):
			num_fis,dim = file_list[i]
			self.send(num_fis)
			self.send(str(dim))
		size = long(os.stat(file_name).st_size) 
		self.send(str(size))	# trimite dimensiunea fisierului
		while size>0:			# trimite fisierul. Chunk de 1024
			part = f.read(1024)
			self.sock.send(part)
			size-=1024
		rc = self.recv()		# primeste mesaj de confirmare
		self.send("OK")
		# trimitere
		self.close()
		print "done"
		return rc

	''' Primeste un fisier de la server '''
	def getfile(self,torrent_name,file_name,folder="."):
		self.init()
		self.send("getfile")
		self.send(torrent_name)
		self.send(file_name)
		print "client got here too"
		ret = self.recv()
		if ret=="NAK":
			return "ERR"
		print "bok"
		print "aok"
		size = long(ret)
		self.send("OK")
		try:
			f = open(folder+"/"+file_name.split("/")[-1],"wb")
		except:
			print "download to "+ file_name.split("/")[-1]
		while size>0:
			s = 1024
			if size<1024:
				s = size	
			buff = self.recv()
			f.write(buff)
			self.send("OK")
			size-=len(buff)
		f.close()
		return "OK"
	
	def gettorrent(self,torrent_name,folder="."):
		self.init()
		self.send("gettorrent")
		self.send(torrent_name)
		nrfis = self.recv()
		if nrfis=="NAK":
			return # torrentul nu e disponibil
		self.send("OK")
		nr = int(nrfis)
		try:
			os.makedirs(folder)
		except:
			pass
		for i in range(nr):
			nume = self.recv()
			self.send("OK")
			sdim = self.recv()
			# print sdim
			dim = long(sdim)
			self.send("OK")
			f = open(folder+"/"+nume,"wb")
			while dim>0:
				s = 1024
				if dim<1024:
					s = dim
				buff = self.recv()
				f.write(buff)
				self.send("OK")
				dim-=len(buff)
			f.close()
		print self.recv() # ??? error?
		self.close()
		
	def getdetails(self,torrent_name):
		self.init()
		self.send("getdetails")
		self.send(torrent_name)
		iok = self.recv()
		self.send("OK")
		if iok=="NAK":
			print "ERROR"
			return None
		seeds = self.recv()
		self.send("OK")
		peers = self.recv()
		self.send("OK")
		avail = self.recv()
		self.send("OK")
		ID = self.recv()
		print "A1"
		self.send("OK")
		print "A2"
		eta = self.recv() #
		print "A3"
		self.send("OK")
		print "A4"
		dspeed = self.recv()
		self.send("OK")
		uspeed = self.recv()
		self.send("OK")
		clients = self.recv()
		self.send("OK")
		self.close()
		print "done"
		return (seeds,peers,avail,ID,eta,dspeed,uspeed,clients)
	
	def removedTorrent(self,user,torrent):
		self.init()
		self.send("removeTorrent")
		self.send(user)
		self.send(torrent)
		self.recv()
		self.close()
	
	''' Primeste informatii despre un torrent '''
	def info(self,torrent_name):
		self.init()
		self.send("info")
		self.send(torrent_name)
		rec = self.recv()
		self.close()
		return rec
	
	def gettorrentlist(self,user):
		self.init()
		self.send("gettorrentlist")
		self.send(user)
		nrfis = self.recv()
		self.send("OK")
		nr = int(nrfis)
		mydic = {}
		for i in range(nr):
			torrentname = self.recv()
			self.send("OK")
			number = int(self.recv())
			self.send("OK")
			lst = []
			for j in range(number):
				filename = self.recv()
				self.send("OK")
				filesize = self.recv()
				self.send("OK")
				lst.append((filename,filesize))

			mydic[torrentname]=lst
		return mydic

if __name__ == "__main__":
	try:
		tcp = TCPClient('localhost',9999)
		tcp.send_command("test")
	except:
		tcp = TCPClient('localhost',9998)
		tcp.send_command("test")
	#print tcp.send_command("hello")
	print tcp.info("PC")
	print tcp.login("abc","def")
	print "---gay"
	print tcp.registerQ()
	print tcp.register("abc","def","Ce faci?","Bine")
	'''
	print tcp.addtorrent("THE torrent",[],"comp.torrent")
	tcp.gettorrent("Computer Desktop Wallpapers Collection (99)","test/")
	'''
