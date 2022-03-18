# coding: utf-8
# /bin/python3

from logging import exception
import socket
import os
import sys
import argparse
import threading
import subprocess
from pathlib import Path
import stat
import re
import uuid
import bluetooth

TQDM = False
BUFFER_SIZE = 4096
# separateur entre le nom de fichier et la taille et le contenu
SEPARATOR = "<SEPARATOR>"

# définition des arguments
parser = argparse.ArgumentParser(
    description='Send and execute a file over WIFI or Bluetooth.')
parser.add_argument("port", help="destination port", type=int)
parser.add_argument('--bluetooth', '-b',
                    help='Use bluetooth instead of internet.', action="store_true")
parser.add_argument(
    "--out", "-o", help='destination folder of the file, default = "./out/"', default="./out/")
parser.add_argument(
    "--loop", "-l",  help="relisten when a download is finished.", action="store_true")

args = parser.parse_args()

# si la bibliothèque tqdm n'est pas installée c'est pas grave mais c'est dommage
try:
    import tqdm
    TQDM = True
except:
    print(' ** Tqdm is not installed,  you can install it with "pip install tqdm **"',
          " ** You can still use this program without a good looking loading bar **", sep="\n")

SERVER_HOST = "0.0.0.0"
SERVER_PORT = args.port

# utilisation de la bibliothèque Path pour plus de compatibilité
OUTDIR = Path(args.out)
if not os.path.exists(args.out):  # si le dossier n'existe pas on le crée.
    os.makedirs(args.out)


class ClientThread(threading.Thread):  # processus représentant une réception

    def __init__(self, ip, port, clientsocket):

        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket = clientsocket

    def run(self):

        print("Incoming file from %s @ %s" % (self.ip, self.port, ))

        # réception de nom_fichier<SEPARATOR>taille_fichier<SEPARATOR>EXECUTE et
        # traitement de ces informations
        received = self.clientsocket.recv(BUFFER_SIZE).decode()
        receiveTuple = received.split(SEPARATOR)
        filename = receiveTuple[0]
        filesize = int(receiveTuple[1])
        execute = True if receiveTuple[2] == "EXECUTE" else False

        filepath = OUTDIR / filename  # emplacement de téléchargement

        if TQDM:  # on affiche la barre Tqdm si installée
            progress = tqdm.tqdm(range(
                filesize), f"Downloading {filename}", unit="o", unit_scale=True, unit_divisor=1024)

        currentsize = 0  # nombre d'octets téléchargés

        with open(filepath, 'wb') as f:  # ouverture du fichier et fermeture implicite en sortie
            while True:
                try:  # essaie de lire le buffer
                    bytes_read = self.clientsocket.recv(BUFFER_SIZE)
                except:  # si la connexion est rompue on sort de la boucle mais on ne panique pas
                    print("- Connection ended")
                    bytes_read = None

                # si le buffer est vide ou que le fichier est complet
                if not bytes_read or (currentsize == filesize):
                    if TQDM:  # on stoppe tqdm
                        progress.close()
                    break  # on sort de la boucle

                # on ajoute le nombre d'octets lu
                currentsize += len(bytes_read)
                f.write(bytes_read)
                if TQDM:  # on met à jour la progression
                    progress.update(len(bytes_read))

        self.clientsocket.close()  # une fois sortie de la boucle on ferme le socket

        if currentsize < filesize:  # si le téléchargement est incomplet
            print(
                f"ERROR : Connection closed before the end of the download ({int(100*currentsize/filesize)}% done)")
        print(f"- Disconnecting from {self.ip}", flush=True)

        if execute:
            print(f"Starting to execute {filename} :")
            executeFile(filepath)

        print(f"- Done with {filename}.")


def executeFile(filepath):
    if sys.platform == "win32":
        os.startfile(filepath)
    else:
        try:  # d'abord on essaie avec xdg-open pour pouvoir ouvrir le fichier avec le logiciel par défaut
            opencmd = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opencmd, filepath])

        except OSError:  #  si une erreur survient on essaie de l'éxécuter
            print(f"Cannot open \"{filepath}\" with \"{opencmd}\" command.",
                  "Trying to execute it instead.", sep="\n")
            try:
                os.chmod(filepath, os.stat(
                    filepath).st_mode | stat.S_IEXEC)  # on fait un chmod +x
                subprocess.call(filepath)  # on exécute

            except Exception as e:
                print(
                    f"The file \"{filepath}\" is not executable :\n  ", e)


if __name__ == "__main__":

    # le socket bluetooth et le socket tcp ont les mêmes proptypes de fonctions qu'on va utiliser,
    # on peut donc utiliser la praticité du python et ne pas différencier les types plus tard dans le code
    if args.bluetooth:
        s: bluetooth.BluetoothSocket = bluetooth.BluetoothSocket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", args.port))

    else:
        s: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", args.port))

    s.settimeout(2)
    dotcount = 0
    s.listen(10)

    if args.loop:
        print(f"Listening on {args.port} ...", end="", flush=True)

    while True:
        if not args.loop:
            print(f"\rListening on {args.port} ." + "." *
                  dotcount + " "*(5-dotcount), end="", flush=True)
            dotcount = (dotcount + 1) % 6

        try:  # attente d'une connexion
            (clientsocket, (ip, port)) = s.accept()
            print()
            client = ClientThread(ip, port, clientsocket)
            client.start()

            if not args.loop:
                client.join()
                exit()

        except KeyboardInterrupt:
            print("\n** User ask to stop **\n")
            exit()

        except SystemExit:
            print("** Exiting. **\n")
            exit()
        except:
            pass
