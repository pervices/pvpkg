#!/bin/bash

echo $1
/usr/bin/ip link set dev $1 mtu 9000 && /usr/sbin/ethtool -G $1 rx 8192 && /usr/sbin/ethtool -G $1 tx 8192
exit $?
