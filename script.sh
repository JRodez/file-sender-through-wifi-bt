sudo iwconfig wlan0 mode ad-hoc channel 11 essid $1 
sudo ip addr add 192.168.1.$2 dev wlan0