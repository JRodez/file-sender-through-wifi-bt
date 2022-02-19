sudo rfkill unblock wifi; sudo rfkill unblock all
ifconfig wlan0 down
iwconfig wlan0 mode Ad-Hoc
ifconfig wlan0 essid KAJE
ifconfig wlan0 192.168.2.1
ifconfig wlan0 up
