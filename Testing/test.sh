#!/bin/bash

#####################
##### RUN TESTS #####
#####################

source variables.sh

# Execute tests
PASSED_TESTS=0
FAILED_TESTS=0
RETURN=0

serial_number=$1
jenkins_bn=$2
DOCKER_SHA=$3
if [ -z $DOCKER_SHA ]; then
	echo "ERROR: Docker SHA must be specified. Usage: test-only.sh [serial] [jenkins_bn] [docker_sha]" && exit 22
fi
shift; shift; shift; shift
TEST_LIST=("$@")

if [ -z $serial_number ]; then
	echo "ERROR: Serial must be specified. Usage: test-only.sh [serial] [jenkins_bn] [docker_sha]" && exit 22
fi

if [[ $serial_number != "TNG"* && $serial_number != "CYN"* && $serial_number != "int" ]]; then
	echo "ERROR: Invalid serial number provided. Valid serial numbers are TNG*, CYN*, or int" && exit 22
fi

if [ -z $jenkins_bn ]; then
	echo "ERROR: Jenkins build number must be specified. Usage: test-only.sh [serial] [jenkins_bn] [docker_sha]" && exit 22
fi

PRODUCT=$(uhd_find_devices | grep 'type:')
case $PRODUCT in
*"crimson"*)
	PRODUCT=v
	TEST_NAMES=("${V_TEST_NAMES[@]}")
	TEST_FILES=("${V_TEST_FILES[@]}")
	;;
*"cyan"*)
	if uhd_manual_get --path /mboards/0/tx/0/fw_version | grep BBTx; then
		# If the unit uses BBTx boards, we need to run the tests at frequencies less than 5GHz to allow the loopback to work
		PRODUCT=b
		echo "Detected Baseband TX boards on Cyan"
	else
		PRODUCT=t
	fi
	TEST_NAMES=("${T_TEST_NAMES[@]}")
	TEST_FILES=("${T_TEST_FILES[@]}")
	;;
*"chestnut"*)
	PRODUCT=l
	TEST_NAMES=("${L_TEST_NAMES[@]}")
	TEST_FILES=("${L_TEST_FILES[@]}")
	;;
*)
	echo "Could not determine if unit is Crimson, Cyan, or Chestnut" && exit 1
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

		python3 -u ${TEST_FILES[$i]}.py -p $PRODUCT -s $serial_number -o $REPORT_DIR -d $DOCKER_SHA

		rv=$?
		if [ $rv -eq 0 ]; then
			PASSED_TESTS=$((PASSED_TESTS+1))
			echo "${TEST_NAMES[$i]} test PASSED" >> log.txt
		else
			FAILED_TESTS=$((FAILED_TESTS+1))
			RETURN=$((RETURN+1))
			echo "${TEST_NAMES[$i]} test FAILED" >> log.txt
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

		python3 -u ${TEST_FILES[$idx]}.py -p $PRODUCT -s $serial_number -o $REPORT_DIR -d $DOCKER_SHA

		rv=$?
		if [ $rv -eq 0 ]; then
			PASSED_TESTS=$((PASSED_TESTS+1))
			echo "${TEST_NAMES[$idx]} test PASSED" >> log.txt
		else
			FAILED_TESTS=$((FAILED_TESTS+1))
			RETURN=$((RETURN+1))
			echo "${TEST_NAMES[$idx]} test FAILED" >> log.txt
		fi
		echo "" >> log.txt
	done
fi


echo "=================Functional Test Results================="
echo "Summary: There are total $NUM_TESTS test(s), $PASSED_TESTS passed, $FAILED_TESTS failed"
echo "=================begin of log.txt================="
echo ""
cat log.txt
echo "=================end of log.txt================="

exit $RETURN
