#!/bin/bash
echo USAGE : $0 <network name> <node number>
sudo rfkill unblock wifi; sudo rfkill unblock all
wpa_cli terminate
sleep 1
ifconfig wlan0 down
iwconfig wlan0 mode Ad-Hoc
iwconfig wlan0 essid $1
echo My address is 192.168.2.$2 over $1 network.
ifconfig wlan0 192.168.2.$2
ifconfig wlan0 up
