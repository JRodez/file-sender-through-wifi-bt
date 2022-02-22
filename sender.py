import socket
import os
import sys
import argparse

TQDM = False
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096  # send 4096 bytes each time step

parser = argparse.ArgumentParser(description='Send and execute a file over WIFI or Bluetooth.')
parser.add_argument('-bt','--bluetooth', help='Use bluetooth instead of internet.',action="store_true")
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
filename = sys.argv[3]
# get the file size
filesize = os.path.getsize(filename)

# create the client socket
s = socket.socket()

print(f"[+] Connecting to {host}:{port}")
s.connect((host, port))
print("[+] Connected.")

# send the filename and filesize
s.send(f"{filename}{SEPARATOR}{filesize}".encode())

# start sending the file
if TQDM :
    progress = tqdm.tqdm(range(
        filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)

with open(filename, "rb") as f:
    while True:
        # read the bytes from the file
        bytes_read = f.read(BUFFER_SIZE)
        if not bytes_read:
            # file transmitting is done
            break
        # we use sendall to assure transimission in
        # busy networks
        s.sendall(bytes_read)

        if TQDM :
            progress.update(len(bytes_read))

s.close()
