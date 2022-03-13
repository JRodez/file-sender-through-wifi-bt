#!/bin/bash

if [ $# -ne 2 ]
then
	echo "USAGE : $0 <network name> <node number>"
	exit
fi

rfkill unblock wifi; rfkill unblock all
wpa_cli terminate
sleep 1
scan="$(sudo iwlist wlan0 scan | grep Frequency | sort | uniq -c | sort -n )"
echo "$scan"
CHANNEL=$(echo $scan | cut -d '(' -f 2 | cut -d ' ' -f 2 | cut -d ')' -f 1 | head -n 1)
echo The channel the less used is the Channel $CHANNEL.
ifconfig wlan0 down
iwconfig wlan0 mode Ad-Hoc
iwconfig wlan0 channel $CHANNEL
iwconfig wlan0 essid $1
echo "My ip address is 192.168.2.$2 over $1 network using the $CHANNEL channel."
ifconfig wlan0 192.168.2.$2
ifconfig wlan0 up
exit