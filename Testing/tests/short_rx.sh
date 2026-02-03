#!/bin/bash
set -Eeuo pipefail

SCRIPT_USER=`whoami`
SCRIPT_HM="$(sysctl -n kernel.hostname)"
SCRIPT_DATE=`date +%Y%m%dT%H%M%S.%N`
SCRIPT_DIR=`pwd`
SCRIPT_PROG=$0
SCRIPT_ARGS=$@
SCRIPT_UNAME=`uname -n -s -r -m`
rc=0

function print_diagnostics() {
    echo "----------------------------------------"
    echo $0 $@
    echo "----------------------------------------"
    echo "Running as: $SCRIPT_USER@$SCRIPT_HM    "
    echo "Date: $SCRIPT_DATE"
    echo "Directory: $SCRIPT_DIR"
    echo "Uname: $SCRIPT_UNAME"
    echo "----------------------------------------"
    echo "Current Time: `date +%Y%m%dT%H%M%S.%N`  "
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


function print_help() {
    echo "Usage:"
    echo "  ./short_rx.sh -m <MODE>"
    echo "  ./short_rx.sh [-h|--help]  # Prints this help menu"
    echo ""
    echo "Arguments:"
    echo "  -m, --mode      Specify whether to stream a set (fixed) number of samples (this is default) or stream continuously (FIXED | CONT)"
    echo ""
    echo "Examples:"
    echo "  ./short_rx.sh -m CONT       # Continuous streaming"
}

# Default to using fixed number of samples
MODE="FIXED"

# Parse arguments/flags
while [ $# -gt 0 ]; do
    key="$1"
    case $key in
        -h|--help)
            print_help
            exit 0
            ;;
        -m|--mode)
            if [ -z "${2:-}" ]; then
                print_diagnostics_short
                echo "[ERROR] Could not find value for -m|--mode argument."
                echo "        Make sure you provide a value after the mode argument"
                exit 1
            fi
            MODE="${2^^}"
            shift
            shift
            ;;
        *)
            print_diagnostics $@
            echo Unrecognized option: $key
            echo
            print_help
            exit 1
            ;;
    esac
done

# IPs of channels 0,1,...
CHANNELS="0,1,2,3"
CHANNEL_IPS=(10.10.10.2 10.10.11.2 10.10.12.2 10.10.13.2)

# nsamps=0 will stream continuously, nsamps > 0 will recv only set number of samples
# Stream for 100000 samples or equivalent duration
CMD_FIXED="/lib/uhd/examples/rx_samples_to_file --nsamps 100000 --rate 125e6 --channels $CHANNELS --null"
CMD_CONTINUOUS="/lib/uhd/examples/rx_samples_to_file --nsamps 0 --rate 125e6 --channels $CHANNELS --duration 0.002 --null"

attempt=0
ping_status=0
while [ $ping_status -eq 0 ]; do
    # Track number of attempts
    attempt=$((attempt+1))
    # Stream rx for short time
    if [ $MODE == "FIXED" ]; then
        stream_result=$($CMD_FIXED) || rc=$?
        check_rc $rc "Streaming for fixed number of samples"
    elif [ $MODE == "CONT" ]; then
        stream_result=$($CMD_CONTINUOUS) || rc=$?
        check_rc $rc "Streaming continuously"
    else
        echo "[ERROR] Invalid stream mode: $MODE"
        print_diagnostics
        exit 1
    fi
    
    # Ping all channels
    for ch in ${!CHANNEL_IPS[@]}; do
        ch_ip=${CHANNEL_IPS[$ch]}
        ping_result=$(ping -c 1 -W 1 $ch_ip) || ping_status=$?

        if [ $ping_status == 0 ]; then
            echo "Attempt $attempt: Pinged ch$ch"
        else
            echo "Attempt $attempt: Failed to ping ch$ch"
        fi
    done

    
done