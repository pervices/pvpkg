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
#NUMER_OF_EN_DEVICES=$(ip addr | grep enp | wc -l)
PV_HOST=192.168.10.
PV_INT=192.168.128.
SFP0=10.10.11.10
SFP1=10.10.10.10
COUNT=0

DUT_MGT_IP_ADDR1=192.168.10.2
DUT_DATA_IP_ADDR1=10.10.10.2
DUT_DATA_IP_ADDR2=10.10.11.2

echo ":: Starting preparation work"

cd .. &&
mkdir -p pkg-archive && touch 1.xz && mv *.xz pkg-archive/ && sync &&
echo $USER"@"$HOST | sudo -S rm -fv /usr/bin/usrp2_card_burner /usr/lib/uhd/utils/usrp2_card_burner.py /usr/lib/uhd/utils/usrp2_recovery.py &&
makepkg &&
echo $USER"@"$HOST | sudo -S pacman -U --noconfirm *.pkg.tar.xz &&
cp src/uhd/host/build/examples/test_tx_trigger tests/ && 
mv *.pkg.tar.xz pkg-archive/ && sync && cd scripts &&


echo ":: Testing reachablity to DUT ::"

(ping -c1 -W1 $DUT_MGT_IP_ADDR1 && echo "Management port $DUT_MGT_IP_ADDR1 is reachable") || (echo "Management port $DUT_MGT_IP_ADDR1 is not reachable" && exit 1) &&
(ping -c1 -W1 $DUT_DATA_IP_ADDR1 && echo "Data link port $DUT_DATA_IP_ADDR1 is reachable") || (echo "Data link port $DUT_DATA_IP_ADDR1 is not reachable" && exit 1) &&
(ping -c1 -W1 $DUT_DATA_IP_ADDR2 && echo "Data link port $DUT_DATA_IP_ADDR2 is reachable") || (echo "Data link port $DUT_DATA_IP_ADDR2 is not reachable" && exit 1) &&

echo ":: Testing reachablity to DUT passed ::"

echo $USER"@"$HOST | sudo -S netstat -pnltu &&
echo $USER"@"$HOST | sudo -S ss -lntupe &&

echo ":: DUT Firmware Info ::"
uhd_usrp_info --all --git

echo ":: Starting Functional Tests" > log.txt

for (( i=0; i<$NUM_TESTS; i++))
do
	echo ":: Executing ${TEST_NAMES[$i]} test" >> log.txt
	#echo "$i"
	pwd
	python3 -u /home/notroot/testing/tests/${TEST_FILES[$i]}.py
	rv=$?
	if [ $rv -eq 0 ]; then
		PASSED_TESTS=$((PASSED_TESTS+1))
		echo "${TEST_NAMES[$i]} test PASSED" >> log.txt
	elif [[ "${TEST_EXCEPTIONS[$i]}" == "true" ]]; then
		EXCEPTIONS=$((EXCEPTIONS+1))
		FAILED_TESTS=$((FAILED_TESTS+1))
		echo "${TEST_NAMES[$i]} test FAILED but it is an exception" >> log.txt
	elif [[ "${TEST_EXCEPTIONS[$i]}" == "false" ]]; then
		FAILED_TESTS=$((FAILED_TESTS+1))
		RETURN=$((RETURN+1))
		echo "${TEST_NAMES[$i]} test FAILED" >> log.txt
	else
		FAILED_TESTS=$((FAILED_TESTS+1))
		RETURN=$((RETURN+1))
		echo "ERROR: Invalid or missing test exception for ${TEST_NAMES[$i]}: index $i may have a problem." >> log.txt
	fi
	echo "" >> log.txt
done

echo "=================Functional Test Results================="
echo "Summary: There are total $NUM_TESTS test(s), $PASSED_TESTS passed, $FAILED_TESTS failed with the following $EXCEPTIONS exception(s):"
for (( i=0; i<$NUM_TESTS; i++)) do
    if [[ "${TEST_EXCEPTIONS[$i]}" == "true" ]]; then
        echo "EXCEPTION:: ${TEST_NAMES[$i]} , ${TEST_FILES[$i]} "
    fi
done
echo "Exceptions are tests that are presently allowed to fail. Please see below for more details"
echo "=================begin of log.txt================="
echo ""
cat log.txt
echo "=================end of log.txt================="
exit $RETURN
