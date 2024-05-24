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
OS=$(cat /etc/os-release | grep PRETTY_NAME | cut -d '=' -f2 | tr -d '\"' | tr -d '\n' | tr -d [:blank:] | tr . _)
#NUMER_OF_EN_DEVICES=$(ip addr | grep enp | wc -l)
PV_HOST=192.168.10.
PV_INT=192.168.128.
SFP0=10.10.11.10
SFP1=10.10.10.10
COUNT=0

DUT_MGT_IP_ADDR1=192.168.10.2
DUT_DATA_IP_ADDR1=10.10.10.2
DUT_DATA_IP_ADDR2=10.10.11.2

SN=$1
BN=$2
DOCKER_SHA=$3
if [ -z $DOCKER_SHA ]; then
	echo "ERROR: Docker SHA must be specified. Usage: test-only.sh [serial] [jenkins_bn] [ftp_upload] [docker_sha]" && exit 22
fi
shift; shift; shift; shift
TEST_LIST=("$@")

if [ -z $SN ]; then
	echo "ERROR: Serial must be specified. Usage: test-only.sh [serial] [jenkins_bn] [ftp_upload] [docker_sha]" && exit 22
fi

if [[ $SN != "TNG"* && $SN != "CYN"* && $SN != "int" ]]; then
	echo "ERROR: Invalid serial number provided. Valid serial numbers are TNG*, CYN*, or int" && exit 22
fi

if [ -z $BN ]; then
	echo "ERROR: Jenkins build number must be specified. Usage: test-only.sh [serial] [jenkins_bn] [ftp_upload] [docker_sha]" && exit 22
fi

PRODUCT=$(uhd_find_devices | grep 'type:')
case $PRODUCT in
*"crimson"*)
	PRODUCT=v
	TEST_NAMES=("${V_TEST_NAMES[@]}")
	TEST_FILES=("${V_TEST_FILES[@]}")
	TEST_EXCEPTIONS=("${V_TEST_EXCEPTIONS[@]}")
	;;
*"cyan"*)
	PRODUCT=t
	TEST_NAMES=("${T_TEST_NAMES[@]}")
	TEST_FILES=("${T_TEST_FILES[@]}")
	TEST_EXCEPTIONS=("${T_TEST_EXCEPTIONS[@]}")
	;;
*)
	echo "Could not determine if unit is Crimson or Cyan" && exit 1
	;;
esac



if [ ! -z $TEST_LIST ]; then
	for i in "${!TEST_LIST[@]}"; do
		for j in "${!TEST_FILES[@]}"; do
			if [[ "${TEST_LIST[$i]}" = "${TEST_FILES[$j]}" ]]; then
				TEST_INDICES+=($j)
			fi
		done
	done

	if [[ ${#TEST_INDICES[@]} != ${#TEST_LIST[@]} ]]; then
		echo Not all test provided were found in the list of available tests. Available tests:
		printf "%s\n" "${TEST_FILES[@]}"
		exit 1
	fi
fi

echo ":: Starting preparation work"

cd tests/
curr=$(pwd)
cd ../../..
if [ ! -d reports ]; then
  mkdir -p reports;
fi
cd reports
REPORT_DIR=$(pwd)
cd $curr

echo ":: Starting Functional Tests" > log.txt

if [ -z $TEST_LIST ]; then
	NUM_TESTS=${#TEST_FILES[@]}
	for (( i=0; i<$NUM_TESTS; i++))
	do
		echo ":: Executing ${TEST_NAMES[$i]} test" >> log.txt
		pwd

		python3 -u ${TEST_FILES[$i]}.py -p $PRODUCT -s $SN -o $REPORT_DIR -d $DOCKER_SHA

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
else
	NUM_TESTS=${#TEST_INDICES[@]}
	for (( i=0; i<$NUM_TESTS; i++))
	do
		idx="${TEST_INDICES[$i]}"

		echo ":: Executing ${TEST_NAMES[$idx]} test" >> log.txt
		pwd

		python3 -u ${TEST_FILES[$idx]}.py -p $PRODUCT -s $SN -o $REPORT_DIR -d $DOCKER_SHA

		rv=$?
		if [ $rv -eq 0 ]; then
			PASSED_TESTS=$((PASSED_TESTS+1))
			echo "${TEST_NAMES[$idx]} test PASSED" >> log.txt
		elif [[ "${TEST_EXCEPTIONS[$idx]}" == "true" ]]; then
			EXCEPTIONS=$((EXCEPTIONS+1))
			FAILED_TESTS=$((FAILED_TESTS+1))
			echo "${TEST_NAMES[$idx]} test FAILED but it is an exception" >> log.txt
		elif [[ "${TEST_EXCEPTIONS[$idx]}" == "false" ]]; then
			FAILED_TESTS=$((FAILED_TESTS+1))
			RETURN=$((RETURN+1))
			echo "${TEST_NAMES[$idx]} test FAILED" >> log.txt
		else
			FAILED_TESTS=$((FAILED_TESTS+1))
			RETURN=$((RETURN+1))
			echo "ERROR: Invalid or missing test exception for ${TEST_NAMES[$idx]}: index $idx may have a problem." >> log.txt
		fi
		echo "" >> log.txt
	done
fi


echo "=================Functional Test Results================="
echo "Summary: There are total $NUM_TESTS test(s), $PASSED_TESTS passed, $FAILED_TESTS failed with the following $EXCEPTIONS exception(s):"
for (( i=0; i<$NUM_TESTS; i++)) do
	if [ -z $TEST_LIST ]; then
		idx=$i
	else
		idx="${TEST_INDICES[$i]}"
	fi

	if [[ "${TEST_EXCEPTIONS[$idx]}" == "true" ]]; then
		echo "EXCEPTION:: ${TEST_NAMES[$idx]} , ${TEST_FILES[$idx]} "
	fi
done

echo "Exceptions are tests that are presently allowed to fail. Please see below for more details"
echo "=================begin of log.txt================="
echo ""
cat log.txt
echo "=================end of log.txt================="

exit $RETURN
