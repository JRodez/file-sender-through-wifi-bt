service bluetooth start
bluetoothctl discoverable on
hcitool dev | grep -o "[[:xdigit:]:]\{11,17\}"