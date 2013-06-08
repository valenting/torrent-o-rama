import subprocess


process = "deluge-console"

def add_torrent(name):
	args = " add "+name
	print "addtorrent DLDer.py 1"
	rc = subprocess.check_output([process,args])
	print "2"
	return rc

def info():
	args = "info"
	rc = subprocess.check_output([process,args])
	return rc

''' Name poate fi id-ul, sau primele litere din nume '''
def info_name(name):
	args = "info "+name
	rc = subprocess.check_output([process,args])
	return rc
	
