#!/bin/bash

#####################
##### RUN TESTS #####
#####################

source variables.sh

# Execute tests
PASSED_TESTS=0
FAILED_TESTS=0
EXCEPTIONS=0
TEST_RESULTS=()
RETURN=0
HOST=$(hostname)
USER=$(whoami)
NUMER_OF_EN_DEVICES=$(ifconfig -a | grep enp | wc -l)
PV_HOST=192.168.10.
PV_INT=192.168.128.
SFP0=10.10.11.10
SFP1=10.10.10.10
COUNT=0

DUT_MGT_IP_ADDR1=192.168.10.2
DUT_DATA_IP_ADDR1=10.10.10.2
DUT_DATA_IP_ADDR2=10.10.11.2

echo ":: Starting preparation work"

#cd .. &&
#mkdir -p pkg-archive && touch 1.xz && mv *.xz pkg-archive/ && sync &&
#echo $USER"@"$HOST | sudo -S rm -fv /usr/bin/usrp2_card_burner /usr/lib/uhd/utils/usrp2_card_burner.py /usr/lib/uhd/utils/usrp2_recovery.py &&
#makepkg &&
#echo $USER"@"$HOST | sudo -S pacman -U --noconfirm *.pkg.tar.xz &&
#cp src/uhd/host/build/examples/test_tx_trigger tests/ && 
#mv *.pkg.tar.xz pkg-archive/ && sync && cd scripts &&

echo ":: Configuring environment - UHD should eventually do this automatically."

echo $USER"@"$HOST | sudo -S sysctl -w net.core.rmem_max=50000000 &&
echo $USER"@"$HOST | sudo -S sysctl -w net.core.wmem_max=2500000 &&

for i in $(seq 1 $NUMER_OF_EN_DEVICES)
do
	NAME=$(ifconfig -a | grep enp | awk '{print $1}' | cut -d ':' -f1 | sed -n ${i}p)
	IP_INTERNAL=$(ifconfig $NAME | grep $PV_INT | awk '{print $2}')
	IP_HOST=$(ifconfig $NAME | grep $PV_HOST | awk '{print $2}')
	IP_SFP0=$(ifconfig $NAME | grep $SFP0 | awk '{print $2}')
	IP_SFP1=$(ifconfig $NAME | grep $SFP1 | awk '{print $2}')

	if [ -n "$IP_INTERNAL" ]
	then
		COUNT=$(($COUNT+1))
		echo "Interface $NAME has PV internal ip address $IP_INTERNAL" &&
		echo "Setting Interface $NAME MTU size to 9000..." &&
		echo $USER"@"$HOST | sudo -S ip link set $NAME up mtu 9000 &&
		echo ""
	fi

	if [ -n "$IP_HOST" ]
	then
		COUNT=$(($COUNT+1))
		echo "Interface $NAME has target device host ip address $IP_HOST" &&
		echo "Setting Interface $NAME MTU size to 9000..." &&
		echo $USER"@"$HOST | sudo -S ip link set $NAME up mtu 9000 &&
		echo ""
	fi

	if [ -n "$IP_SFP0" ]
	then
		COUNT=$(($COUNT+1))
		echo "Interface $NAME has SFP0 ip address $IP_SFP0" &&
		echo "Setting Interface $NAME MTU size to 9000..." && 
		echo $USER"@"$HOST | sudo -S ip link set $NAME up mtu 9000 &&
		echo ""
	fi

	if [ -n "$IP_SFP1" ]
	then
		COUNT=$(($COUNT+1))
		echo "Interface $NAME has SFP1 ip address $IP_SFP1" &&
		echo "Setting Interface $NAME MTU size to 9000..." &&
		echo $USER"@"$HOST | sudo -S ip link set $NAME up mtu 9000 &&
		echo ""
	fi
done

if [ "$COUNT" != "4" ]
then
		echo "Failed to set network properties. None of the following addresses should be empty:"
		echo "PV Internal IP address is $IP_INTERNAL"
		echo "Host IP address is $IP_HOST"
		echo "SFP0 IP address is $IP_SFP0"
		echo "SFP1 IP address is $IP_SFP1"
		exit 1
fi

echo ":: Testing reachablity to DUT ::"

(ping -c1 -W1 $DUT_MGT_IP_ADDR1 && echo "Management port $DUT_MGT_IP_ADDR1 is reachable") || (echo "Management port $DUT_MGT_IP_ADDR1 is not reachable" && exit 1) &&
(ping -c1 -W1 $DUT_DATA_IP_ADDR1 && echo "Data link port $DUT_DATA_IP_ADDR1 is reachable") || (echo "Data link port $DUT_DATA_IP_ADDR1 is not reachable" && exit 1) &&
(ping -c1 -W1 $DUT_DATA_IP_ADDR2 && echo "Data link port $DUT_DATA_IP_ADDR2 is reachable") || (echo "Data link port $DUT_DATA_IP_ADDR2 is not reachable" && exit 1) &&

echo ":: Debugging BIND: Address Already in use error ::"

echo $USER"@"$HOST | sudo -S netstat -pnltu &&
echo $USER"@"$HOST | sudo -S ss -lntupe &&

echo ":: Starting Functional Tests" > log.txt

for (( i=0; i<$NUM_TESTS; i++))
do
	echo ":: Executing ${TEST_NAMES[$i]} test" >> log.txt
	#echo "$i"
	pwd
	python2 -u ../tests/${TEST_FILES[$i]}.py
	rv=$?
	if [ $rv -eq 0 ]; then
		PASSED_TESTS=$((PASSED_TESTS+1))
		echo "${TEST_NAMES[$i]} test PASSED" >> log.txt
	elif [ $i -eq 5 ]; then
		EXCEPTIONS=$((EXCEPTIONS+1))
		FAILED_TESTS=$((FAILED_TESTS+1))
		echo "${TEST_NAMES[$i]} test FAILED but it is an exception" >> log.txt
	else
		FAILED_TESTS=$((FAILED_TESTS+1))
		RETURN=$((RETURN+1))
		echo "${TEST_NAMES[$i]} test FAILED" >> log.txt
	fi
	echo "" >> log.txt
done
echo "=================Functional Test Results================="
echo "Summary: There are total $NUM_TESTS test(s), $PASSED_TESTS passed, $FAILED_TESTS failed with $EXCEPTIONS exception(s)" 
echo "Execption is a type of failure that is known to us, currently the in_phase test is allowed to fail. Please see below for more details"
echo "=================begin of log.txt================="
echo ""
cat log.txt
echo "=================end of log.txt================="
exit $RETURN
