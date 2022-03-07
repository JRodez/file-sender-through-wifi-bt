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

try:
    import tqdm
    TQDM = True
except:
    print(' ** Tqdm is not installed,  you can install it with "pip install tqdm **"',
          " ** You can still use this program without a good looking loading bar **", sep="\n")

SERVER_HOST = "0.0.0.0"
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
SERVER_PORT = args.port
OUTDIR = Path(args.out)
if not os.path.exists(args.out):
    os.makedirs(args.out)

myBtAdd = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
if args.bluetooth:
    print("The server MAC address is", myBtAdd)



class ClientThread(threading.Thread):
    # class Client():
    def __init__(self, ip, port, clientsocket):

        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket: socket.socket = clientsocket

    def run(self):

        print("Incoming file from %s:%s" % (self.ip, self.port, ))

        received = self.clientsocket.recv(BUFFER_SIZE).decode()
        receiveTuple = received.split(SEPARATOR)
        filename = receiveTuple[0]
        filesize = int(receiveTuple[1])
        execute = True if receiveTuple[2] == "EXECUTE" else False
        filepath = OUTDIR / filename

        if TQDM:
            progress = tqdm.tqdm(range(
                filesize), f"Downloading {filename}", unit="o", unit_scale=True, unit_divisor=1024)
        currentsize = 0

        with open(filepath, 'wb') as f:
            while True:
                bytes_read = self.clientsocket.recv(BUFFER_SIZE)
                if not bytes_read:
                    if TQDM:
                        progress.close()
                    break

                currentsize += len(bytes_read)
                f.write(bytes_read)
                if TQDM:
                    progress.update(len(bytes_read))

        if currentsize < filesize:
            print(
                f"ERROR : Connection closed before the end of the download ({int(100*currentsize/filesize)}% done)")
        self.clientsocket.close()
        print(f"Disconnecting from {self.ip}", flush=True)

        if execute:
            print(f"Starting to execute {filename} :")
            executeFile(filepath)

        print(f"Done with {filename}.")


def executeFile(filepath) : 
    if sys.platform == "win32":
        os.startfile(filepath)
    else:
        try:
            opencmd = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opencmd, filepath])
        except OSError:
            print(f"Cannot open \"{filepath}\" with \"{opencmd}\" command.",
                    "Trying to execute it instead.", sep="\n")
            try:
                os.chmod(filepath, os.stat(
                    filepath).st_mode | stat.S_IEXEC)
                subprocess.call(filepath)
            except Exception as e:
                print(
                    f"The file \"{filepath}\" is not executable :\n  ", e)


if __name__ == "__main__":

    if args.bluetooth:
        s: socket.socket = socket.socket(
            socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", args.port))

    else:
        s: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", args.port))

    s.settimeout(0.5)
    dotcount = 0
    s.listen(10)

    if args.loop:
        print(f"Listening on {args.port} ...", end="", flush=True)

    while True:
        if not args.loop:
            print(f"\rListening on {args.port} ." + "." *
                dotcount + " "*(5-dotcount), end="", flush=True)
            dotcount = (dotcount + 1) % 6

        try:
            (clientsocket, (ip, port)) = s.accept()
            print()
            client = ClientThread(ip, port, clientsocket)
            client.start()

            if not args.loop:
                exit()
        except socket.timeout:
            continue
