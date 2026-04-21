#!/bin/bash
# Utility script to call a test repeatedly until it fails

set -Eeuo pipefail

declare -i runs=0

# "$@" executes the provided command (inluding arguments)
while "$@"; do

    runs+=1
    echo "Completed iterations: $runs"

done
