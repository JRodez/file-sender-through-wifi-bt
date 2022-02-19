sudo rfkill unblock wifi; sudo rfkill unblock all
wpa_cli terminate
ifconfig wlan0 down
iwconfig wlan0 mode Ad-Hoc
ifconfig wlan0 essid KAJE
ifconfig wlan0 192.168.2.2
ifconfig wlan0 up
