# PyWare
## Introduction
PyWare est un petit malware écrit en python. Il rentre dans le cadre du cursus de *sécurité des systèmes* de la haute-école [*Henallux*](https://www.henallux.be/). En particulier le cours [*R209 : Developpement*](https://services.henallux.be/paysage/public/cursus/infoaa/idAa/97103/idUe/97118/idCursus/68) donné en deuxième bachelier.

PyWare ne se charge pas de l'infection et part du postulat que la victime est déjà infectée pour le démarrage de PyWare.

## Prérequis
L'ensemble des programmes ont été écrits et testés avec [Python](https://www.python.org) [3.7.2](https://www.python.org/downloads/release/python-372/) . Celui-ci est nécessaire sur les deux machines et de préférence ajouté à la variable d'environnement PATH. De plus, le module [PyCryptodome](https://pycryptodome.readthedocs.io) est nécessaire sur le serveur de l'attaquant. Si le module n'est pas présent sur la victime, une fonctionnalité de PyWare permet de l'installer.

## Architecture
 - Coté attaquant
   - [**PyWareGen**](pywaregen.py) : Générateur du fichier de configuration utilisé par la victime.
   - [**PyWareServ**](pywareserv.py) : Serveur de connexion. Lorsqu'une liaison est établie, il ouvre un shell interactif afin d'envoyer les commandes à la victime. Le port de connexion peut être précisé à l'aide de l'argument `-p Port`. Par défaut, le 4444 est utilisé.
   - [crypto](crypto.py) : Fichier python regroupant les fonctions de chiffrements symétrique et asymétrique. Il est utilisé par *PyWareServ* et par le malware, et par conséquence présent aussi sur la victime.
   - [hello](hello.py) : Fichier python regroupant les différents démarrages de PyWare. Il est utilisé par *PyWareGen* et *PyWareServ*.
   
 - Coté victime : 
   - [**malware**.py](malware.py) : Client à exécuter sur la victime. Il gère la connexion et les différentes commandes envoyées par l'utilisateur distant. Le nom du fichier est laissé libre à l'utilisateur.
   - [**malware**.cfg](malware.cfg) : Fichier de configuration regroupant les différents serveurs de l'attaquant. Le nom du fichier doit être le même que celui du malware. Il peut être édité à la main ou à l'aide de PyWareGen. Les différentes valeurs demandées sont :
     - \[server name\] ; un nom arbitraire pour le serveur.
     - Host ; Adresse ip ou nom de domaine à utiliser pour se connecter au serveur.
     - Port ; Port de connexion au serveur. Il doit être un nombre entier compris entre 1 et 65535 inclus.
     - RetryInterval ; Intervalle de temps en seconde entre deux tentatives de connexion. Il doit un nombre entier positif.
   - [crypto.py](crpyto.py) : Fichier python gérant le chiffrement. Il est une copie de celui utilisé côté attaquant.

## Fonctionnement
En lançant PyWareServ, vous démarrez le serveur. Celui-ci écoute sur le port 4444 ou sur le port passé en argument, s'il y en a un.

De son côté, la victime démarre le malware. Celui-ci ira lire le fichier de configuration en commençant par la section par défaut *DEFAULT*. Il écrasera ensuite ces valeurs par celles inscrites dans la première section personnalisée. Si une erreur est présente dans cette section, celles de la section par défaut seront utilisées. Si le fichier de configuration est manquant ou que des erreurs sont présentes dans la section par défaut, des valeurs se secours ont été écrites dans le programme du malware. Pour les connaitre, veuillez-vous référer au début du [fichier python adéquat](malware.py). Après cela, le malware essaye d'initier la connexion en tant que client vers le serveur. Cette solution a été choisie car elle permet de s'affranchir des limitations liées au NAT et au pare-feu. Si la connexion échoue car il est impossible de résoudre le nom de domaine du serveur, le serveur suivant listé dans le fichier de configuration est utilisé. S'il échoue pour une autre raison, le malware se met en pause pendant l'intervalle de temps inscrit dans le fichier de configuration. 

Lorsque la connexion est établie, le serveur génère une paire de clef RSA de 2048 bits et envoie au client la clef publique chiffrée en base64. La victime récupère cette clef publique. Si le fichier *crypto.py* est disponible et que PyCryptodome est installé, une clef de session AES 256 bits et un vecteur d'initialisation de 128 bits sont alors générés, chiffrés avec la clef publique et envoyé au serveur. Si le chiffrement n'est pas disponible, le client envoie un message chiffré en base64 afin de prévenir le serveur. L'attaquant vérifie que la cryptographie est bien gérée par la victime. Si c'est bien le cas, la clef de session et le vecteur d'initialisation sont alors utilisés pour sécuriser le reste de la connexion. Sinon, un chiffrement par base64 est utilisé pour le reste de la communication. Dans les deux cas, l'utilisateur est prévenu. Il est possible de redémarrer cette phase de génération et d'échange de clefs à l'aide de la commande `newkeys`.

Une fois cette phase terminée, un shell intéractif est ouvert côté attaquant. Les diverses commandes fournies par l'utilisateurs seront d’abord vérifiées avant d'être transmit à la victime si besoin et si la commande est correcte. La session est terminée des deux côtés lorsque l'utilisateur rentre la commande `exit`, `quit` ou `kill`. Seul cette troisième commande arrête le malware. Les deux autres remettent le malware dans la phase de connexion, sans relecture du fichier de configuration.

## Fonctionnalités
### Gestion de la communication
| Commandes | Description |
| -- | -- |
| exit | Termine la connexion entre les deux machines et ferme le programme côté attaquant. Cependant, PyWare continue de tourner sur la cible et retente une connexion vers le serveur sélectionné à un intervalle de temps déterminé dans le fichier de configuration. Pour arrêter le programme sur les deux machines, utilisez la commande `kill`. |
| kill | Termine la connexion et ferme les programmes des deux côtés. |
| newkeys | Regénère une clef de session afin de sécuriser la communication. |
| quit | Alias de la commande `exit`. |

### Fonctions locales
Ces fonctionnalités ne sont exécutées que du côté de la machine locale et ne transmet rien à la victime. 

| Commandes | Description |
| -- | -- |
| help \[Commands,\] | Affiche les différentes commandes demandées par l'utilisateur, ainsi qu'une brève explications de chacune d'elles. Si aucune commande n'est fournie, il affiche alors toutes les commandes disponibles. |
| list | Liste les différentes commandes disponibles. |
| /cd Dir | Change le répertoire courant à 'Dir'. |
| /dir \[Dir\] | Alias pour la commande `/ls`. |
| /ls \[Dir\] | Liste les fichiers et répertoire du dossier 'Dir'. Si 'Dir' n'est pas spécifié, le dossier courant est utilisé. |
| /pwd | Affiche le dossier courant. |

### Informations
| Commandes | Description |
| -- | -- |
| cd Dir | Change le répertoire courant à 'Dir'. |
| dir \[Dir\] | Alias pour la commande `ls`. |
| download File | Télécharge le fichier 'File' depuis la victime vers la machine locale. Le fichier est enregistré dans le dossier courant en conservant le même nom. |
| getinfo \[Options,\] | Récupère des informations sur la victime. Si aucune option n'est renseignée, il les retourne toutes. Les options disponibles sont `user, hostname, fqdn, ip, os, version, architecture, language, time`. |
| getservices | Affiche l'ensemble des services en cours d'exécution sur la victime. |
| getusers | Liste l'ensemble des utilisateurs de la victime. |
| ls \[Dir\] | List les fichiers et répertoire du dossier 'Dir'. Si 'Dir' n'est pas spécifié, le dossier courant est utilisé. |
| ps | Alias pour la commande `getservices`. |
| pwd | Affiche le dossier courant. |
| upload File | Envoie le fichier 'File' depuis la machine courant vers la victime. Le fichier est enregistré dans le dossier courant en conservant le même nom. |

### Exécutions distantes
| Commandes | Description |
| -- | -- |
| autostart \[Name\] | Installe PyWare sur la victime sous le nom 'Name'. De plus, PyWare démarre de manière automatique à la connexion de l'utilisateur. Si 'name' n'est pas renseigné, 'services' est utilisé. Pour Linux, les fichiers sont copiés dans le répertoire ~/.*name* et ajouté dans la table cron de l'utilisateur. Pour Windows, les fichiers sont copiés dans le répertoire %APPDATA%\\Microsoft\\Windows\\*Name* et un script est écrit sous le nom %APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\*name*.vbs . *Remarque :* Vous pouvez mettre à jours manuellement PyWare en écrasant ces fichier à l'aide de la commande `upload`|
| exec Command | Exécute la commande 'Command' sur la victime. Attention, cette fonction n'est pas interactive. |
| installmodules | Installe les modules Python nécessaire à PyWare pour prendre en charge l'ensemble des fonctionnalités. |

## Algorithmique
Pour comprendre comment fonctionne les différents fichiers, veuillez-vous aux fichiers eux-mêmes.

## Fonctions supplémentaires
Ces fonctions supplémentaires ont été imaginées mais n'ont malheureusement pas encore été écrites.
 - [ ] keylogger {start|stop|download}
 - [ ] login de la session
 - [ ] reload PyWare
 - [ ] scan réseau
 - [ ] shell intéractif / ouverture d'une connexion remote ssh
 - [ ] mise à jour de PyWare

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
 - https://www.developpez.net/forums/
 - http://apprendre-python.com/
 - https://www.debian.org/
 - https://wiki.debian.org/
 - https://askubuntu.com/
 - https://openclassrooms.com/fr/
 - https://www.commentcamarche.net/
 - http://www.patorjk.com/software/taag/
 - A. Voisin, *Python, Dans le contexte de la sécurité informatique*, 2018-2019
