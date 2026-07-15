import os
from common import sigproc
from common import generator
from common import pdf_report
from common import test_args
from common import log
import sys
import time, datetime
import subprocess
import re
"""
Created on Tue Jul 14 19:06:08 2026

@author: hhep
"""

targs = test_args.TestArgs(testDesc="CrimsonTNG Unit Discoverability Test")
report = pdf_report.ClassicShipTestReport(
    "crimson_discoverable",
    targs.serial, 
    targs.report_dir, 
    targs.docker_sha
    )

test_fail = 0

def main(iterations, title="CrimsonTNG Unit Discoverability Test") -> int:
    global test_fail
    generator.dump(iterations)
    
    command = "uhd_find_devices"
    
    report.buffer_put("text_large", "Test Summary")
    report.buffer_put("text", " ")
    
    # store action in log
    log.pvpkg_log_info("CRIMSON_DISCOVERABLE", "Running command: " + command)
    
    try: 
        result = subprocess.check_output(command, shell=True, text=True)
    except subprocess.CalledProcessError as e: # Return is not 0
        log.pvpkg_log_error("CRIMSON_DISCOVERABLE", "Error running command")
        result = str(e.output)
        test_fail = 1
        report.buffer_put("text", "Error running command: " + command)
        report.buffer_put("text", "Test failed")
    
    # result = result.split("Done!\n", 1)[1]
    log.pvpkg_log_info("CRIMSON_DISCOVERABLE", "Results:" + result)
    device_type = ""
    
    if ("type:" in result):    
        device_type = result.split("type: ")[1].strip()
    
    test_info = [
    [
        "Target Device Type",
        "Actual Device Type",
        "Duration",
        ],
    [
        str("crimson_tng"),
        device_type,
        str(iterations["duration"]) + " second(s)",
        ]
    ]

    report.buffer_put("table", test_info, "Parameters")
    report.buffer_put("text", " ")
    
    if (device_type != "crimson_tng"): 
        test_fail = 1
            
    if (test_fail): 
        report.buffer_put("text", "Test failed")
    else:
        report.buffer_put("text", "Test passed") 
    
    report.insert_title_page("CrimsonTNG Unit Discoverability Test")
    report.draw_from_buffer()
    report.save()
    log.pvpkg_log_info("CRIMSON_DISCOVERABLE", "PDF report saved at " + report.get_filename())
    
    if (test_fail != 0):
        sys.exit(1)
    
    sys.exit(0)
    
for it in generator.tx_rx_longterm_rate():
    time.sleep(60) # give network card on host some time to cool down between runs
    main(it)
