### Readme - Server ###
1. Instalare deluge
		#dezarhivare
	1.1 tar -xvf deluge-1.3.1.tar.gz 
	1.2 cd deluge-1.3.1
		#instalare dependinte
	1.3 sudo apt-get install python python-twisted python-twisted-web2 python-openssl python-simplejson python-setuptools gettext python-xdg python-chardet python-geoip python-libtorrent python-notify python-pygame python-gtk2 python-gtk2-dev librsvg2-dev xdg-utils python-mako 
		#instalare deluge	
	1.4 sudo python setup.py install

2. Metode de utilizare deluge:
	* interfata grafica -> deluge-gtk
	* consola -> deluge-console
	Exemplu adaugare torrent:
	2.1 #pornire daemon
		deluged
	2.2 deluge-console "add file.torrent"
	2.3 deluge-console info
	2.4 deluge-console "info NUMETORRENT"
	
	ATENTIE
	
	Este necesara rularea cu python 2.7.1
	Un ghid pentru instalare in paralel cu versiunea actuala, folositi pythonbrew: http://stackoverflow.com/questions/5233536/python-2-7-on-ubuntu
	scriptul server.sh face switch-ul la 2.7.1 si ruleaza serverul
	Inainte de pornirea serverului:
		stergeti fisierele /server/user si /server/torrents
		porniti deluged
	La client recomandam folosirea python 2.6.5
