# PyWare
## Introduction
PyWare est un petit malware écrit en python. Il rentre dans le cadre du cursus de sécurité des système de la [Henallux](https://www.henallux.be/). En particulier le cours R209: Developpement donné en deuxième bachelier.
PyWare ne se charge pas de l'infection et part du postula que la victime est déjà infecté pour le démarrage de PyWare.

## Prérequis
L'ensemble des programmes ont été écrit et testé avec [Python](https://www.python.org) [3.7.2](https://www.python.org/downloads/release/python-372/) . Celui-ci est nécessaire sur les deux machines et de préférence ajouté à la variable d'environnement PATH. De plus, le module [PyCryptodome](https://pycryptodome.readthedocs.io) est nécessaire sur le serveur de l'attaquant. Si le module n'est pas présent sur la victime, une fonctionnalité de PyWare l'intalle.

## Architecture
L'attaquant fait office de serveur et attant la connection depuis la victime. La victime, de son côté, essaye une connection vers l'un des serveur de l'attaquant à un interval de temps déterminer. Une fois la connection établie, un shell intéractif est ouvert côté attanquant et les diverses commandes acceptable sont ensuite transféré à la victime. Le retour de la commande est renvoyé à l'attaquant et est affichée.

## Fonctionnement
- Attaquant
  - PyWareGen : Générateur du fichier de configuration listant les différents serveurs que l'attaquant peut utiliser, ainsi que leurs informations de connection.
  - PyWareServ : Serveur de connection. Il attend une connection de la victime puis ouvre un shell intérectif.
- Victime
  - Malware : Client de connection vers le serveur. Il essaye d'ouvrir une connection vers celui-ci à partir du fichier de configuration. Le nom du fichier est laissé libre à l'utilisateur. Il nécéssite aussi le fichier *crypto.py*.
  - Configuration : Fichier de configuration regroupant 

## Fonctionnalitées
