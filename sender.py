import socket
import os
import sys
import argparse
# from pathlib import Path

TQDM = False
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096 

parser = argparse.ArgumentParser(description='Send and execute a file over WIFI or Bluetooth.')
parser.add_argument('-b','--bluetooth', help='Use bluetooth instead of internet.',action="store_true")
parser.add_argument('-x','--execute', help='Execute file remotely after upload.',action="store_true")
parser.add_argument("address", help="destination address")
parser.add_argument("port", help="destination port",type=int)
parser.add_argument("file", help="file to send")

args = parser.parse_args()

try:
    import tqdm
    TQDM = True
except:
    print(' ** Tqdm is not installed,  you can install it with "pip install tqdm **"',
          " ** You can still use this program without a good looking loading bar **", sep="\n")


host = args.address #sys.argv[1]
port = args.port #int(sys.argv[2])

# the name of file we want to send, make sure it exists
filename = args.file
# get the file size
filesize = os.path.getsize(filename)

# create the client socket
s = socket.socket()

print(f"[+] Connecting to {host}:{port}")
s.connect((host, port))
print("[+] Connected.")

# send the filename and filesize
s.send(f"{os.path.basename(filename)}{SEPARATOR}{filesize}{SEPARATOR}{('EXECUTE' if args.execute else 'NOP')}".encode())

# start sending the file
if TQDM :
    progress = tqdm.tqdm(range(
        filesize), f"Sending {filename}", unit="o", unit_scale=True, unit_divisor=1024)

with open(filename, "rb") as f:
    while True:
        bytes_read = f.read(BUFFER_SIZE)
        if not bytes_read:
            break
 
        s.sendall(bytes_read)

        if TQDM :
            progress.update(len(bytes_read))

s.close()
