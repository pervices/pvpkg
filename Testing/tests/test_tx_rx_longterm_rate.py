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

    report.buffer_put("text_large", "Test Summary")
    report.buffer_put("text", " ")
        
    log.pvpkg_log_info("TX_RX_LONGTERM_RATE", "Running command: " + command)
    
    try: 
        result = subprocess.check_output(command, shell=True, text=True)
    except subprocess.CalledProcessError as e: # Return is not 0
        log.pvpkg_log_error("TX_RX_LONGTERM_RATE", "Error running command")
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
    log.pvpkg_log_info("TX_RX_LONGTERM_RATE", "Results:" + result)

    actual_receive_rate = result.split("Testing receive rate ")[1].split("on")[0]
    actual_transmit_rate = result.split("Testing transmit rate ")[1].split("on")[0]

    test_info = [
    [
        "Target Sampling Rate",
        "Actual Receive Rate",
        "Actual Transmit Rate",
        "Duration",
        ],
    [
        str(iterations["sample_rate"] / 1000000) + " Msps",
        actual_receive_rate,
        actual_transmit_rate,
        str(iterations["duration"]) + " second(s)",
        ]
    ]

    report.buffer_put("table", test_info, "Parameters")
    report.buffer_put("text", " ")

    over_underflow_count = [["Channel", "Overflow", "Underflow"]]
    individual_lines = result.split("\n")
    for line in individual_lines: 
        if ("CH" not in line):
            continue
        ch_name = line.split("CH ",1)[1][0]
        over_underflow_count.append([ch_name, re.findall('\\d+', line)[0], re.findall('\\d+', line)[1]])
           
    report.buffer_put("table", over_underflow_count, "Results")
    report.buffer_put("text", " ")

    benchmark_rate_summary = [["Item", "Count"]]
    # Get the potion of benchmark rate summary text
    benchmark_rate_text = result.split("Benchmark rate summary:")
    benchmark_rate_text = benchmark_rate_text[1].split("Done!")[0]
    for line in benchmark_rate_text.split("\n"):
        stripped_line = line.strip()
        if stripped_line != '':
            splitted_line = stripped_line.split(':')
            for i, cell in enumerate(splitted_line):
                splitted_line[i] = cell.strip()
            benchmark_rate_summary.append(splitted_line)

    report.buffer_put("table", benchmark_rate_summary, "Benchmark Rate Summary")
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
    log.pvpkg_log_info("TX_RX_LONGTERM_RATE", "PDF report saved at " + report.get_filename())
    
    if (test_fail != 0):
        sys.exit(1)
    
    sys.exit(0)


for it in generator.tx_rx_longterm_rate():
    time.sleep(60) # give network card on host some time to cool down between runs
    main(it)
