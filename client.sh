sudo rfkill unblock wifi; sudo rfkill unblock all
wpa_cli terminate
sleep 1
ifconfig wlan0 down
iwconfig wlan0 mode Ad-Hoc
iwconfig wlan0 essid KAJE
ifconfig wlan0 192.168.2.2
ifconfig wlan0 up
