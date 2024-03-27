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

PRODUCT=$1
PRODUCT=$(echo $PRODUCT | tr '[:upper:]' '[:lower:]')
case $PRODUCT in
v | vaunt | crimson)
	TEST_NAMES=("${V_TEST_NAMES[@]}")
	TEST_FILES=("${V_TEST_FILES[@]}")
	TEST_EXCEPTIONS=("${V_TEST_EXCEPTIONS[@]}")
	;;
t | tate | cyan)
	TEST_NAMES=("${T_TEST_NAMES[@]}")
	TEST_FILES=("${T_TEST_FILES[@]}")
	TEST_EXCEPTIONS=("${T_TEST_EXCEPTIONS[@]}")
	;;
*)
	echo "Product must be specified, use 'v' for vaunt or 't' for tate. Usage: test-only.sh [v | t] [serial] [jenkins_bn] [ftp_upload]"
	exit 1
	;;
esac

SN=$2
if [ -z $SN ]; then
	echo "Serial must be specified. Usage: test-only.sh [v | t] [serial] [jenkins_bn] [ftp_upload]"
	exit 1
fi

BN=$3
if [ -z $BN ]; then
	echo "Jenkins build number must be specified. Usage: test-only.sh [v | t] [serial] [jenkins_bn] [ftp_upload]"
	exit 1
fi

UPLOAD=$4
case $UPLOAD in
t | true | TRUE | True | 1)
	UPLOAD=1
	;;
f | false | FALSE | False | 0)
	UPLOAD=0
	;;
*)
	echo "FTP upload must be specified as true or false. Usage: test-only.sh [v | t] [serial] [jenkins_bn] [ftp_upload]"
	exit 1
	;;
esac


SN=$SN'_'$BN
DATETIME=$(date '+%Y-%m-%d-%H-%M')
TAR_NAME=$PRODUCT'_'$SN'_'$DATETIME

echo ":: Starting preparation work"

cd tests/
if [ ! -d $REPORT_DIR ]; then
  mkdir -p $REPORT_DIR;
fi

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

NUM_TESTS=${#TEST_FILES[@]}
for (( i=0; i<$NUM_TESTS; i++))
do
	echo ":: Executing ${TEST_NAMES[$i]} test" >> log.txt
	#echo "$i"
	pwd

	python3 -u ${TEST_FILES[$i]}.py -p $PRODUCT -s $SN -o $REPORT_DIR

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

echo "Packaging reports into tarball.."
tar -czvf $TAR_NAME $REPORT_DIR
if [[ $? != 0 ]]; then
	echo "Failed to create tarball"
else
	echo "Successfully created tarball"
fi

if [ $UPLOAD == 1 ]; then
	echo "Uploading to FTP server.."
	lftp -u $FTP_USER,$FTP_PW $FTP_ADD -e "$SSL_CERT; put -O $FTP_UPLOAD_DIR/ $TAR_NAME; bye"
	if [[ $? != 0 ]]; then
		echo "Failed to upload file $TAR_NAME to $FTP_UPLOAD_DIR"
	else
		echo "Successfully uploaded file $UPDATE_FILE_NAME to $FTP_UPLOAD_DIR"
	fi
fi

echo "Creating archive.."
cd ../..
mkdir archive
cp tests/$TAR_NAME archive/
if [[ $? != 0 ]]; then
	echo "Failed to create archive"
else
	echo "Successfully created archive"
fi

exit $RETURN
