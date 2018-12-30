# PyWare
## Introduction
PyWare est un petit malware écrit en python. Il rentre dans le cadre du cursus de sécurité des système de la [Henallux](https://www.henallux.be/). En particulier le cours R209: Developpement donné en deuxième bachelier.

PyWare ne se charge pas de l'infection et part du postula que la victime est déjà infecté pour le démarrage de PyWare.

## Prérequis
L'ensemble des programmes ont été écrit et testé avec [Python](https://www.python.org) [3.7.2](https://www.python.org/downloads/release/python-372/) . Celui-ci est nécessaire sur les deux machines et de préférence ajouté à la variable d'environnement PATH. De plus, le module [PyCryptodome](https://pycryptodome.readthedocs.io) est nécessaire sur le serveur de l'attaquant. Si le module n'est pas présent sur la victime, une fonctionnalité de PyWare l'intalle.

## Architecture
L'attaquant fait office de serveur et attant la connection depuis la victime. La victime, de son côté, essaye une connection vers l'un des serveur de l'attaquant à un interval de temps déterminer. Cette solution permet de s'affranchir des informations de connection de la victime. De plus, elle permet de contourner les problèmes lié au NAT et Firewall. Une fois la connection établie, un shell intéractif est ouvert côté attanquant et les diverses commandes acceptable sont ensuite transféré à la victime. Le retour de la commande est renvoyé à l'attaquant et est affichée.

## Fonctionnement
- Attaquant
  - PyWareGen : Générateur du fichier de configuration listant les différents serveurs que l'attaquant peut utiliser, ainsi que leurs informations de connection.
  - PyWareServ : Serveur de connection. Il attend une connection de la victime puis ouvre un shell intérectif.
- Victime
  - Malware : Client de connection vers le serveur. Il essaye d'ouvrir une connection vers celui-ci à partir du fichier de configuration. Le nom du fichier est laissé libre à l'utilisateur. Il nécéssite aussi le fichier *crypto.py*.
  - Configuration : Fichier de configuration regroupant 

## Fonctionnalités
### Getion de la communication
 - exit : Termine la connection entre les deux machines et ferme le programme côté attaquant. Par contre, PyWare continue de tourner sur la cible et retente une connection vers le serveur sélectionnné à un interval de temps déterminer dans le fichier de configuration. Pour arrêter le programme sur les deux machines, utilisez la commande *kill*.
 - kill : Termine la connection et ferme les programmes des deux côtés.
 - newkeys : Regénère une clef de session afin de sécurisé la communication.
 - quit : Alias de la commande *exit*.

### Fonctions locales
Ces fonctionnalitée ne sont exécuté que du côté de la machine locale et ne transmet rien à la victime. 
 - help \[Commands,\] : Affiche les différentes commandes demandé par l'utilisteur, ainsi qu'une brêve explications de chacun d'elles. Si aucune commande n'est fournis, il affiche alors toutes les commandes disponibles.
 - list : List les différentes commandes disponibles.
 - /cd Dir : Change le répertoire courant à 'Dir'.
 - /dir \[Dir\] : Alias pour la commande */ls*.
 - /ls \[Dir\] : List les fichiers et répertoire du dossier 'Dir'. Si 'Dir' n'est pas spécifier, le dossier courant est utilisé.
 - /pwd : Affiche le dossier courant.

### Informations
 - cd Dir : Change le répertoire courant à 'Dir'.
 - dir \[Dir\] : Alias pour la commande */ls*.
 - download File : Télécharge le fichier 'File' depuis la victime vers la machine locale. Le fichier est enregistré dans le dossier courant en conservant le même nom.
 - getinfo \[Options,\] : récupaire des informations sur la victime. Si aucune option n'est renseigné, il les retourne toutes. Les options disponibles sont `user, hostname, fqdn, ip, os, version, architecture, language, time`.
 - getservices : Affiche l'ensemble des services en cours d'exécution sur la victime.
 - getusers : Liste l'ensemble des utilisateurs de la victime.
 - ls \[Dir\] : List les fichiers et répertoire du dossier 'Dir'. Si 'Dir' n'est pas spécifier, le dossier courant est utilisé.
 - ps : Alias pour la commande *getservices*.
 - pwd : Affiche le dossier courant.
 - upload File : Evoie le fichier 'File' depuis la machine courant vers la victime. Le fichier est enregistré dans le dossier courant en conservant le même nom.

### Exécutions distantes
 - autostart \[Name\] : Installe PyWare sur la victime sous le nom 'Name'. De plus, PyWare démarre de manière automatique à la connection de l'utilisateur.
 - exec Command : Exécute la commande 'Command' sur la victime. Attention, cette fonction n'est pas intéractive.
 - installmodules : Installe les modules Python nécessaire à PyWare pour prendre en charge l'ensemble des fonctionnalitées.

## Algorithmique
Pour comprendre comment fonctionne les différentes fichiers, veuillez vous référer au fichier [algorithmique.md](algorithmique.md).

## Références
https://www.python.org/
https://docs.python.org/3/
https://docs.python.org/fr/3/
https://pypi.org/
https://www.jetbrains.com/pycharm/
https://github.com/
https://git-scm.com/
https://nmap.org/book/
https://www.wireshark.org/
https://pycryptodome.readthedocs.io/
https://fr.wikipedia.org/
https://en.wikipedia.org/
https://www.deepl.com/translator
https://stackoverflow.com/
http://apprendre-python.com/
https://www.debian.org/
https://wiki.debian.org/
https://askubuntu.com/
https://openclassrooms.com/fr/
https://www.commentcamarche.net/
http://www.patorjk.com/software/taag/
A. Voisin, *Python, Dans le contexte de la sécurité informatique*, 2018-2019
