#!/bin/bash

if [ $# -ne 2 ]
then
	echo "USAGE : $0 <network name> <node number>"
	exit
fi

ifconfig wlan0 up
sleep 1
scan="$(sudo iwlist wlan0 scan | grep Frequency | sort | uniq -c | sort -n )"
echo "$scan"
CHANNEL=$(echo $scan | cut -d '(' -f 2 | cut -d ' ' -f 2 | cut -d ')' -f 1 | head -n 1)
echo "The least used channel is channel $CHANNEL."

rfkill unblock wifi &> /dev/null ; rfkill unblock all &> /dev/null
wpa_cli terminate &> /dev/null
sleep 1

ifconfig wlan0 down
iwconfig wlan0 mode Ad-Hoc
iwconfig wlan0 channel $CHANNEL
iwconfig wlan0 essid $1
echo "My ip address is 192.168.2.$2 over $1 network using the channel $CHANNEL."
ifconfig wlan0 192.168.2.$2
ifconfig wlan0 up
exit