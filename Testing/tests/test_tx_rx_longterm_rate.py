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

targs = test_args.TestArgs(testDesc="Tx Rx Long-term Streaming Rate Test")
report = pdf_report.ClassicShipTestReport(
    "tx_rx_longterm_rate",
    targs.serial, 
    targs.report_dir, 
    targs.docker_sha
    )

test_fail = 0

def main(iterations, title="TX RX Long-term Streaming Rate Test") -> int:
    global test_fail
    generator.dump(iterations)

    command = "/usr/lib/uhd/examples/benchmark_rate --tx_rate={} --rx_rate={} --tx_channels={} --rx_channels={} --duration={}".format(
        iterations["sample_rate"], 
        iterations["sample_rate"],
        str(iterations["channels"])[1:-1].replace(" ", ""),
        str(iterations["channels"])[1:-1].replace(" ", ""),
        iterations["duration"],
    )
        
    test_info = [
        [
            "Sampling Rate",
            "Duration",
         ],
        [
            iterations["sample_rate"],
            iterations["duration"],
            ]
        ]

    report.buffer_put("text_large", "Test Summary")
    report.buffer_put("text", " ")
    report.buffer_put("table", test_info, "Parameters")
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
        # report.insert_title_page("Tx Rx Long-term Streaming Rate Test")
        # report.draw_from_buffer()
        # report.save()
        # print("PDF report saved at " + report.get_filename())
        # sys.exit(1)
    
    # result = result.split("Done!\n", 1)[1]
    print("Results:" + result)

    over_underflow_count = [["Channel", "Overflow", "Underflow"]]
    individual_lines = result.split("\n")
    for line in individual_lines: 
        if ("CH" not in line):
            continue
        ch_name = line.split("CH ",1)[1][0]
        over_underflow_count.append([ch_name, re.findall('\\d+', line)[0], re.findall('\\d+', line)[1]])
           
    report.buffer_put("table", over_underflow_count, "Results")
    report.buffer_put("text", " ")
    
    for row in over_underflow_count[1:]:
        if (int(row[1]) > 0 or int(row[2]) > 0):
            test_fail = 1
            
    if (test_fail): 
        report.buffer_put("text", "Test failed")
    else:
        report.buffer_put("text", "Test passed") 
    
    report.insert_title_page("Tx Rx Long-term Streaming Rate Test")
    report.draw_from_buffer()
    report.save()
    print("PDF report saved at " + report.get_filename())
    
    if (test_fail != 0):
        sys.exit(1)
    
    sys.exit(0)


for it in generator.tx_rx_longterm_rate():
    main(it)
