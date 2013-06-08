
	Torrent-o-rama
		Echipa: Valentin Gosu
				Emma Mirica
				Andrei Tigora
				
				
	Client:
		- isi ia configurarile dintr-un fisier, adica ip si port pentru server
		- pentru ca update-ul sa se faca mai rapid, el pastreaza o lista cu fisierele pe care le are,
		astfel, la fiecare sincronizare cu serverul, acesta nu mai trebuie sa trimita mereu fisierele, ci doar in momentul
		modificarii va fi anuntat
		- daca un client a cerut un fisier torrent si il sterge, ceilalti clienti care au cerut acelasi fisier
		vor vedea modificarea, adica, vor vedea ca fisierul este cerut de mai putin useri - se va face in felul acesta
		update in DatabaseManager
		- daca nu vom reusi sa facem sa mearga in Windows gtk-ul, o solutie la care ne-am gandit este sa facem clientul
		si in linia de comanda. Este mai putin estetic, dar ar functiona si in Windows :)
		
	Server:
		- Un readme complet pentru baza de date este disponibil pe svn. De asemenea, la pornirea serverului, se va verifica
		daca exista ierarhia de directoare, si daca nu, va fi creata.
		- Intr-adevar, nu am fost atenti, dar folderele pentru torrente trebuiau sa se afle in /torrents. In acest caz, trebuie
		doar modificata calea in daemonul de deluge (clientul de torrent), lucru care ne-a scapat, din cauza ca am fost interesati
		sa testam cat mai mult. Restul fisierelor cu informatii despre torrente se afla in /torrents asa cum am precizat in specificatie.
		- Pentru a observa ierarhia de directoare, am adaugat pe svn folderele /torrents si /users (deoarece am uitat sa le prezentam).
		Aici se poate observa structura unui fisier pentru informatii despe clienti si despre torrente.
			OBS: exista useri creati cu numele vali, Guldur
		- Pentru a intelege cum functioneaza deluge poate fi parcurs fisierul README.txt de pe svn /src
		
	Sursele in mare sunt comentate, deci se poate urmari relativ usor partea de client, respectiv server.