import os
from common import sigproc
from common import engine
from common import generator
from common import pdf_report
from common import test_args
from common import log
from retrying import retry
import numpy as np
import matplotlib.pyplot as plt
import sys
import time, datetime
import subprocess
import re

targs = test_args.TestArgs(testDesc="UHD Find Devices Test")
report = pdf_report.ClassicShipTestReport(
    "uhd_find_devices",
    targs.serial, 
    targs.report_dir, 
    targs.docker_sha
    )

test_fail = 0

def main(iterations, title="UHD Find Devices Test") -> int:
    global test_fail
    generator.dump(iterations)

    command = "uhd_find_devices"

    report.buffer_put("text_large", "Test Summary")
    report.buffer_put("text", " ")
        
    log.pvpkg_log_info("UHD_FIND_DEVICES", "Running command: " + command)
    
    try: 
        result = subprocess.check_output(command, shell=True, text=True)
    except subprocess.CalledProcessError as e: # Return is not 0
        log.pvpkg_log_error("UHD_FIND_DEVICES", "Error running command")
        result = str(e.output)
        test_fail = 1
        report.buffer_put("text", "Error running command: " + command)
        report.buffer_put("text", "Test failed")
    
    log.pvpkg_log_info("UHD_FIND_DEVICES", "Results:" + result)

    # Parse for type
    device_type = None
    for line in result.split('\n'):
        if 'type:' in line:
            device_type = line.split('type:')[1].strip()
            break

    test_info = [
        ["Command", "Device Type", "Expected Type"],
        [command, device_type if device_type else "Not found", "crimson_tng"]
    ]

    report.buffer_put("table", test_info, "Parameters")
    report.buffer_put("text", " ")

    if device_type == "crimson_tng":
        report.buffer_put("text", "Test passed: Device type is crimson_tng")
    else:
        report.buffer_put("text", "Test failed: Device type is not crimson_tng")
        test_fail = 1
    
    report.insert_title_page("UHD Find Devices Test")
    report.draw_from_buffer()
    report.save()
    log.pvpkg_log_info("UHD_FIND_DEVICES", "PDF report saved at " + report.get_filename())
    
    if (test_fail != 0):
        sys.exit(1)
    
    sys.exit(0)


for it in generator.uhd_find_devices():
    main(it)

