import os
from common import sigproc
from common import engine
from common import generator
from common import pdf_report
from common import test_args
from retrying import retry
import numpy as np
import matplotlib.pyplot as plt
import sys
import time, datetime
import subprocess
import re

targs = test_args.TestArgs(testDesc="UHD Device Type Test")
report = pdf_report.ClassicShipTestReport(
    "uhd_device_type",
    targs.serial, 
    targs.report_dir, 
    targs.docker_sha
    )

test_fail = 0

def main(iterations, title="UHD_Device_Type_Test") -> int:
    global test_fail
    generator.dump(iterations)

    command = "uhd_find_devices"

    report.buffer_put("text_large", "Test Summary")
    report.buffer_put("text", " ")
        
    print("Running command: " + command)
    
    try: 
        result = subprocess.check_output(command, shell=True, text=True)
    except subprocess.CalledProcessError as e: # Return is not 0
        print("Error running command")
        result = str(e.output)
        test_fail = 1
        report.buffer_put("text", "Error running command: " + command)
        report.buffer_put("text", "Test failed")
    

    print("Results:\n" + result)

    match = re.search(r'type:\s*([^,]+)', result)
    device_type = match.group(1).strip()

    test_info = [
    [
        "Device Type",
        ],
    [
        device_type,
        ]
    ]

    report.buffer_put("table", test_info, "Parameters")
    report.buffer_put("text", " ")
    
    if (device_type == "crimson_tng"):
        test_fail = 0
    else:
        test_fail = 1
            
    if (test_fail): 
        report.buffer_put("text", "Test failed")
    else:
        report.buffer_put("text", "Test passed") 
    
    report.insert_title_page("UHD Device Type Test")
    report.draw_from_buffer()
    report.save()
    print("PDF report saved at " + report.get_filename())
    
    if (test_fail != 0):
        sys.exit(1)
    
    sys.exit(0)


for it in generator.uhd_device_type():
    time.sleep(60) # give network card on host some time to cool down between runs
    main(it)
