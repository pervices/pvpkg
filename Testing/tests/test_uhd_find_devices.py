#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 19:23:43 2026

@author: skan
uhd_find_devices check for crimson for ci training
"""
from common import generator as gen
from common import pdf_report
from common import test_args
from common import log
import sys
import time
import subprocess
import re

targs = test_args.TestArgs(testDesc="UHD Device Type Verification Test")
report = pdf_report.ClassicShipTestReport(
    "uhd_device_type_check",
    targs.serial,
    targs.report_dir,
    targs.docker_sha,
    targs.addr
    )

test_fail = 0

def test() -> int:
    global test_fail

    command = "uhd_find_devices"

    report.buffer_put("text_large", "Test Summary")
    report.buffer_put("text", " ")

    log.pvpkg_log_info("UHD_DEVICE_TYPE_CHECK", "Running command: " + command)

    try:
        result = subprocess.check_output(command, shell=True, text=True,) #stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        log.pvpkg_log_error("UHD_DEVICE_TYPE_CHECK", "Error running command")
        result = str(e.output)
        test_fail = 1
        report.buffer_put("text", "Error running command: " + command)
        report.buffer_put("text", "Test failed")
        return

    log.pvpkg_log_info("UHD_DEVICE_TYPE_CHECK", "Results:" + result)


    match = re.search(r'type:\s*(\S+)', result) #find non-white space text after type: 
    
    if match:
        actual_type = match.group(1).strip()
    else:
        actual_type = "NOT FOUND"
        test_fail = 1

    expected_type = "crimson_tng"


    if actual_type == expected_type:
        log.pvpkg_log_info("UHD_DEVICE_TYPE_CHECK", "Pass. Found expected type: " + actual_type)
    else:
        log.pvpkg_log_error("UHD_DEVICE_TYPE_CHECK", f"Fail. Expected type '{expected_type}' but got '{actual_type}'")
        test_fail = 1


    test_info = [
        [
            "Parameter",
            "Value"
        ],
        [
            "Command Run",
            command
        ],
        [
            "Expected Device Type",
            expected_type
        ],
        [
            "Actual Device Type Detected",
            actual_type
        ],
        [
            "Test Verdict",
            "PASS" if not test_fail else "FAIL"
        ]
    ]

    report.buffer_put("table", test_info, "Parameters")
    report.buffer_put("text", " ")

    if test_fail:
        report.buffer_put("text", "Test failed")
    else:
        report.buffer_put("text", "Test passed")


def build_report():
    report.insert_title_page("UHD Device Type Verification Test")
    report.draw_from_buffer()
    report.save()
    log.pvpkg_log_info("UHD_DEVICE_TYPE_CHECK", "PDF report saved at " + report.get_filename())

def main():

    test()

main()

build_report()
sys.exit(test_fail)


