# coding: utf-8
# /bin/python3

import socket
import os
import sys
import argparse
import bluetooth
from pathlib import Path


TQDM = False
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096

parser = argparse.ArgumentParser(
    description='Send and execute a file over WIFI or Bluetooth.')
parser.add_argument('-b', '--bluetooth',
                    help='Use bluetooth instead of internet.', action="store_true")
parser.add_argument(
    '-x', '--execute', help='Execute file remotely after upload.', action="store_true")
parser.add_argument("address", help="destination address")
parser.add_argument("port", help="destination port", type=int)
parser.add_argument("file", help="file to send")

args = parser.parse_args()

try:
    import tqdm
    TQDM = True
except:
    print(' ** Tqdm is not installed,  you can install it with "pip install tqdm **"',
          " ** You can still use this program without a good looking loading bar **", sep="\n")


filename = Path(args.file)
filesize = os.path.getsize(filename)


if args.bluetooth:
    s: bluetooth.BluetoothSocket = bluetooth.BluetoothSocket()
else:
    s: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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

s.send(f"{os.path.basename(filename)}{SEPARATOR}{filesize}{SEPARATOR}{('EXECUTE' if args.execute else 'NOP')}".encode())

if TQDM:
    progress = tqdm.tqdm(range(
        filesize), f"Sending {filename}", unit="o", unit_scale=True, unit_divisor=1024)

with open(filename, "rb") as f:
    while True:
        bytes_read = f.read(BUFFER_SIZE)
        if not bytes_read:
            break

        s.sendall(bytes_read)

        if TQDM:
            progress.update(len(bytes_read))

        if args.bluetooth:
            try :
                s.settimeout(0.5)
                s.recv(BUFFER_SIZE)
                s.settimeout(10)
            except :
                continue

progress.close()
s.close()
print("Done.")