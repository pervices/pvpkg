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


targs = test_args.TestArgs(testDesc="Tx Rx Long-term Loopback Test")
report = pdf_report.ClassicShipTestReport(
    "tx_rx_longterm_loopback", 
    targs.serial, 
    targs.report_dir, 
    targs.docker_sha
    )

test_fail = 0

def main(iterations, title="TX RX Long-term Loopback Test") -> int:
    global test_fail
    generator.dump(iterations)

    tx_stack = [ (5.0, iterations["sample_count"]) ]
    rx_stack = [ (5.0, int(iterations["sample_count"]) ) ]
    
    test_fail = test_fail | os.system(
        "/usr/lib/uhd/examples/rx_to_tx_loopback --rate={} --tx_channels={} --rx_channels={} --tx_freq={} --rx_freq={} --tx_gain={} --rx_gain={} --nsamps={}".format(
            iterations["sample_rate"], 
            iterations["channels"],
            iterations["channels"],
            iterations["center_freq"], 
            iterations["center_freq"], 
            iterations["tx_gain"], 
            iterations["rx_gain"], 
            iterations["sample_count"], 
            )
        )

    test_info = [
        [
            "Center Freq", 
            "Sampling Rate",
            "Tx Gain", 
            "Rx Gain",
            "Samples", 
         ],
        [
            iterations["center_freq"], 
            iterations["sample_rate"],
            iterations["tx_gain"], 
            iterations["rx_gain"],
            iterations["sample_count"], 
            iterations["start_time"], 
            ]
        ]

    report.buffer_put("text_large", "Test Summary")
    report.buffer_put("text", " ")
    report.buffer_put("table", test_info, "Parameters")
    report.buffer_put("text", " ")

    report.draw_from_buffer()
    report.save()
    
    if (test_fail == 1):
        sys.exit(1)
    
    sys.exit(0)