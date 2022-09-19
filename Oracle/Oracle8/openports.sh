#!/bin/bash

#This is a script to configure and update the firewall on redhat.

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

qSFP_nic_prefix=ntxs
mgmt_nic=enp58s0

ports='42836 42837 42838 42839 42840 42841 42842 42843 42809 42810 42811 42812 42799'

echo -e "Configuring qSFP+ NIC\n"

for n in {0..3}
do
	ip addr add 10.10.1$n.10/24 broadcast 10.10.1$n.255 dev $qSFP_nic_prefix$n
	ip link set mtu 9000 dev $qSFP_nic_prefix$n
done

echo -e "Configuring mgmt NIC\n"

	ip addr add 192.168.10.10/24 broadcast 192.168.10.255 dev $mgmt_nic
	ip link set mtu 9000 dev $mgmt_nic

echo -e "Opening firewalld ports.\n"

for port in $ports
do
	firewall-cmd --zone=trusted --add-port=$port/udp
done

echo -e "Adding nics to trusted zones.\n"

firewall-cmd --zone=trusted --change-interface=enp58s0 --permanent
for n in {0..3}
do
	firewall-cmd --zone=trusted --change-interface=$qSFP_nic_prefix$n --permanent
done



