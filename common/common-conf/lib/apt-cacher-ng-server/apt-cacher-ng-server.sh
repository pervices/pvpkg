#!/bin/bash
set -Eeuo pipefail

# DIAGNOSTICS
SCRIPT_USER=`whoami`
SCRIPT_HM=`hostname`
SCRIPT_DATE=`date +%Y%M%dT%H%M%S.%N`
SCRIPT_DIR=`pwd`
SCRIPT_PROG=$0
SCRIPT_ARGS=$@
SCRIPT_DIAGNOSTICS_SHORT="$SCRIPT_USER@$SCRIPT_HM:$SCRIPT_DIR/$SCRIPT_PROG $SCRIPT_ARGS" 
SCRIPT_UNAME=`uname -n -s -r -m`
rc=0

function print_diagnostics_short(){
    echo "INFO: `date +%Y%M%dT%H%M%S.%N`: $SCRIPT_DIAGNOSTICS_SHORT"
}

function print_diagnostics() {
    echo "----------------------------------------"
    echo $0 $@
    echo "----------------------------------------"
    echo "Running as: $SCRIPT_USER@$SCRIPT_HM    "
    echo "Date: $SCRIPT_DATE"
    echo "Directory: $SCRIPT_DIR"
    echo "Uname: $SCRIPT_UNAME"
    echo "----------------------------------------"
    echo "Current Time: `date +%Y%M%dT%H%M%S.%N`  "
    echo "PWD: `pwd`                              "
    echo "----------------------------------------"
}

function check_rc() {
    local rc=$1
    local cmd_name=${2:-"Previous command"}
    if [[ $rc != 0 ]]; then
        echo "----------------------------------------" 
        echo "ERROR: ${cmd_name} returned non-zero exit code, exiting..." 
        echo "----------------------------------------" 
        print_diagnostics
        exit $rc
    fi
}

# Ensure the container name was provided as argument and assign to variable
if [ -z $1 ]; then
    echo "ERROR: Container name not provided as argument, exiting..."
    print_diagnostics
    exit 1
fi
CONTAINER_NAME=${1:-} # Container named after service
CONTAINER_IMAGE="pvtesting/ubuntu2404:apt-cacher-ng"

# Create container if it does not exist
docker container inspect $CONTAINER_NAME &> /dev/null || rc=$?
if [[ $rc -gt 0 ]]; then
    rc=0
    docker run --rm \
    --name $CONTAINER_NAME \
    --network host \
    --volume /var/cache/apt-cacher-ng:/var/cache/apt-cacher-ng \
   $CONTAINER_IMAGE /usr/sbin/apt-cacher-ng ForeGround=1 \
   || rc=$?
   check_rc $rc "docker run"
else
    docker container start $CONTAINER_NAME || rc=$?
    check_rc $rc "Starting or attaching to Docker container"
fi

exit 0