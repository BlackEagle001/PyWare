# PyWare
## Introduction
PyWare est un petit malware écrit en python. Il rentre dans le cadre du cursus de *sécurité des systèmes* de la haute-école *[Henallux](https://www.henallux.be/)*. En particulier le cours *[R209 : Developpement](https://services.henallux.be/paysage/public/cursus/infoaa/idAa/97103/idUe/97118/idCursus/68)* donné en deuxième bachelier.

PyWare ne se charge pas de l'infection et part du postulat que la victime est déjà infectée pour le démarrage de PyWare.

## Prérequis
L'ensemble des programmes ont été écrit et testé avec [Python](https://www.python.org) [3.7.2](https://www.python.org/downloads/release/python-372/) . Celui-ci est nécessaire sur les deux machines et de préférence ajouté à la variable d'environnement PATH. De plus, le module [PyCryptodome](https://pycryptodome.readthedocs.io) est nécessaire sur le serveur de l'attaquant. Si le module n'est pas présent sur la victime, une fonctionnalité de PyWare permet de l'installer.

## Architecture
L'attaquant fait office de serveur et attend la connexion depuis la victime. La victime, de son côté, essaye une connexion vers l'un des serveur de l'attaquant à un intervalle de temps déterminer. Cette solution permet de s'affranchir des informations de connexion de la victime. De plus, elle permet de contourner les problèmes liés au NAT et Firewall. Une fois la connexion établie, un shell interactif est ouvert côté attaquant et les diverses commandes acceptables sont ensuite transféré à la victime. Le retour de la commande est renvoyé à l'attaquant et est affichée.

## Fonctionnement
- Attaquant
  - PyWareGen : Générateur du fichier de configuration listant les différents serveurs que l'attaquant peut utiliser, ainsi que leurs informations de connexion.
  - PyWareServ : Serveur de connexion. Il attend une connexion de la victime puis ouvre un shell intérectif.
- Victime
  - Malware : Client de connexion vers le serveur. Il essaye d'ouvrir une connexion vers celui-ci à partir du fichier de configuration. Le nom du fichier est laissé libre à l'utilisateur. Il nécéssite aussi le fichier *crypto.py*.
  - Configuration : Fichier de configuration regroupant 

## Fonctionnalités
### Gestion de la communication
| Commandes | Description |
| -- | -- |
| exit | Termine la connexion entre les deux machines et ferme le programme côté attaquant. Cependant, PyWare continue de tourner sur la cible et retente une connexion vers le serveur sélectionné à un intervalle de temps déterminer dans le fichier de configuration. Pour arrêter le programme sur les deux machines, utilisez la commande *kill*. |
| kill | Termine la connexion et ferme les programmes des deux côtés. |
| newkeys | Regénère une clef de session afin de sécuriser la communication. |
| quit | Alias de la commande *exit*. |

### Fonctions locales
Ces fonctionnalités ne sont exécutées que du côté de la machine locale et ne transmet rien à la victime. 

| Commandes | Description |
| -- | -- |
| help \[Commands,\] | Affiche les différentes commandes demandé par l'utilisateur, ainsi qu'une brève explications de chacun d'elles. Si aucune commande n'est fournie, il affiche alors toutes les commandes disponibles. |
| list | List les différentes commandes disponibles. |
| /cd Dir | Change le répertoire courant à 'Dir'. |
| /dir \[Dir\] | Alias pour la commande */ls*. |
| /ls \[Dir\] | List les fichiers et répertoire du dossier 'Dir'. Si 'Dir' n'est pas spécifier, le dossier courant est utilisé. |
| /pwd | Affiche le dossier courant. |

### Informations
| Commandes | Description |
| -- | -- |
| cd Dir | Change le répertoire courant à 'Dir'. |
| dir \[Dir\] | Alias pour la commande */ls*. |
| download File | Télécharge le fichier 'File' depuis la victime vers la machine locale. Le fichier est enregistré dans le dossier courant en conservant le même nom. |
| getinfo \[Options,\] | Récupère des informations sur la victime. Si aucune option n'est renseignée, il les retourne toutes. Les options disponibles sont `user, hostname, fqdn, ip, os, version, architecture, language, time`. |
| getservices | Affiche l'ensemble des services en cours d'exécution sur la victime. |
| getusers | Liste l'ensemble des utilisateurs de la victime. |
| ls \[Dir\] | List les fichiers et répertoire du dossier 'Dir'. Si 'Dir' n'est pas spécifier, le dossier courant est utilisé. |
| ps | Alias pour la commande *getservices*. |
| pwd | Affiche le dossier courant. |
| upload File | Envoie le fichier 'File' depuis la machine courant vers la victime. Le fichier est enregistré dans le dossier courant en conservant le même nom. |

### Exécutions distantes
| Commandes | Description |
| -- | -- |
| autostart \[Name\] | Installe PyWare sur la victime sous le nom 'Name'. De plus, PyWare démarre de manière automatique à la connexion de l'utilisateur. |
| exec Command | Exécute la commande 'Command' sur la victime. Attention, cette fonction n'est pas interactive. |
| installmodules | Installe les modules Python nécessaire à PyWare pour prendre en charge l'ensemble des fonctionnalités. |

## Algorithmique
Pour comprendre comment fonctionne les différentes fichiers, veuillez-vous référer au fichier [algorithmique.md](algorithmique.md).

## Références
 - https://www.python.org/
 - https://docs.python.org/3/
 - https://docs.python.org/fr/3/
 - https://pypi.org/
 - https://www.jetbrains.com/pycharm/
 - https://github.com/
 - https://git-scm.com/
 - https://nmap.org/book/
 - https://www.wireshark.org/
 - https://pycryptodome.readthedocs.io/
 - https://fr.wikipedia.org/
 - https://en.wikipedia.org/
 - https://www.deepl.com/translator
 - https://stackoverflow.com/
 - http://apprendre-python.com/
 - https://www.debian.org/
 - https://wiki.debian.org/
 - https://askubuntu.com/
 - https://openclassrooms.com/fr/
 - https://www.commentcamarche.net/
 - http://www.patorjk.com/software/taag/
 - A. Voisin, *Python, Dans le contexte de la sécurité informatique*, 2018-2019
