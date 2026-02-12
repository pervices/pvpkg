import os
from common import sigproc
from common import engine
from common import generator as gen
from common import pdf_report
from common import test_args
from common import log
from retrying import retry
import numpy as np
import matplotlib.pyplot as plt
import sys
import time, datetime

targs = test_args.TestArgs(testDesc="device type verification Test")
report = pdf_report.ClassicShipTestReport("device_type_verification", targs.serial, targs.report_dir, targs.docker_sha)
test_fail = 0
summary_tables = []

def test_device_type():
    global test_fail

    log.pvpkg_log_info("device_type_test", "starting device type verification")

    data = [["Test", "Expected", "Actual", "Result"]]

    try:
        # get device information with test arguments
        product_used = targs.product

        log.pvpkg_log_info("device_type_test", f"Detected product type: {product_used}")

        # create test info table
        test_info = [
            ["Parameter", "Value"],
            ["Serial Number", targs.serial],
            ["Detected Product", product_used],
            ["Expected Product", "Vaunt (crimson_tng)"]
        ]

        report.buffer_put("text_large", "Device Type Verification Test")
        report.buffer_put("text", " ")
        report.buffer_put("table_large", test_info, "")
        report.buffer_put("text", " ")

        # check if product is crimson_tng
        if product_used == "Vaunt":
            data.append(["device type", "crimson_tng", product_used, "pass"])
            report.buffer_put("text", "test result: pass")
            log.pvpkg_log_info("device_type_test", "device type verification passed")
        else:
            data.append(["device type", "crimson_tng", product_used, "fail"])
            report.buffer_put("text", "test result: fail")
            log.pvpkg_log_error("device_type_test", "device type verification failed. Expected crimson_tng")
            test_fail = 1

    except Exception as err:
        log.pvpkg_log_error("DEVICE_TYPE_TEST", f"Error during test: {str(err)}")
        data.append(["Device Type", "Vaunt (crimson_tng)", "ERROR", "fail"])
        report.buffer_put("text", f"Test Error: {str(err)}")
        report.buffer_put("pagebreak")
        test_fail = 1

    return data

def main():
    data = test_device_type()
    summary_tables.append(["device type verification", data])

def add_summary_table(title, data):
    report.insert_text_large("{} testing summary".format(title))
    report.insert_text("")
    report.insert_table(data)
    report.new_page()

def build_report():
    report.insert_title_page("device type verification test")
    for summary in summary_tables:
        add_summary_table(summary[0], summary[1])
    report.draw_from_buffer()
    report.save()
    log.pvpkg_log_info("device_type_test", "pdf report saved at " + report.get_filename())

## SCRIPT LOGIC ##
main()
build_report()
sys.exit(test_fail)
