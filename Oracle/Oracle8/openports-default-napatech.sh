#!/bin/bash

#This is a script to configure and update the firewall on redhat.

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

qSFP_nic_prefix=ntxs
mgmt_nic=enp58s0

echo -e "Configuring qSFP+ NICs\n"

for n in {0..3}
do
    openports-configSFP.sh $qSFP_nic_prefix$n $n
done

echo -e "Configuring mgmt NIC\n"
openports-MGMT.sh $mgmt_nic

echo -e "Opening firewalld ports.\n"

echo -e "Adding nics to trusted zones.\n"

exit 0
