# coding: utf-8
# /bin/python3

import socket
import os
import sys
import argparse
import bluetooth
from pathlib import Path


TQDM = False
BUFFER_SIZE = 4096
# separateur entre le nom de fichier et la taille et le contenu
SEPARATOR = "<SEPARATOR>"

# définition des arguments
parser = argparse.ArgumentParser(
    description='Send and execute a file over WIFI or Bluetooth.')
parser.add_argument('--bluetooth', '-b',
                    help='Use bluetooth instead of internet.', action="store_true")
parser.add_argument(
    '--execute', '-x', help='Execute file remotely after upload.', action="store_true")
parser.add_argument("address", help="destination address")
parser.add_argument("port", help="port", type=int)
parser.add_argument("file", help="file to send")

args = parser.parse_args()

# si la bibliothèque tqdm n'est pas installée c'est pas grave mais c'est dommage
try:
    import tqdm
    TQDM = True
except:
    print(' ** Tqdm is not installed,  you can install it with "pip install tqdm **"',
          " ** You can still use this program without a good looking loading bar **", sep="\n")

# utilisation de la bibliothèque Path pour plus de compatibilité
filename = Path(args.file)
filesize = os.path.getsize(filename)

# le socket bluetooth et le socket tcp ont les mêmes proptypes de fonctions qu'on va utiliser,
# on peut donc utiliser la praticité du python et ne pas différencier les types plus tard dans le code
if args.bluetooth:
    s: bluetooth.BluetoothSocket = bluetooth.BluetoothSocket()
else:
    s: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Tentative de connexion
print(f"Connecting to {args.address} @ {args.port}")
try:
    s.connect((args.address, args.port))
    s.settimeout(10)
except Exception as e:
    print(args.address, "@", args.port, "\n  ", e,
          f" - {args.address} {args.port}\n- Aborting.")
    s.close()
    exit()
print("Connected.")

# envoie de filename<SEPARATOR>filesize<SEPARATOR>EXECUTE
s.send(f"{os.path.basename(filename)}{SEPARATOR}{filesize}{SEPARATOR}{('EXECUTE' if args.execute else 'NOP')}".encode())

# on affiche la barre Tqdm si installée
if TQDM:
    progress = tqdm.tqdm(range(
        filesize), f"Sending {filename}", unit="o", unit_scale=True, unit_divisor=1024)

with open(filename, "rb") as f:  # ouverture du fichier et fermeture implicite en sortie
    while True:
        bytes_read = f.read(BUFFER_SIZE)
        if not bytes_read:  # s'il n'y a rien à lire on quite
            break

        s.sendall(bytes_read)

        if TQDM:  # on stoppe tqdm
            progress.update(len(bytes_read))

        if args.bluetooth:
            try:  # on vide le buffer
                s.settimeout(0.01)
                s.recv(1024)
            except:
                pass
            s.settimeout(10)

if TQDM:
    progress.close()  # on ferme la barre
s.close()
print("Done.")
