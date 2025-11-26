import os
from common import pdf_report
from common import generator as gen
from common import test_args
from common import log
import sys
import time


targs = test_args.TestArgs(testDesc="Tx Rate Test")
report = pdf_report.ClassicShipTestReport("tx_rate", targs.serial, targs.report_dir, targs.docker_sha)
test_fail = 0
summary_table = [ ["Description", "Tx Rate (Msps)", "Tx Channels", "Result"] ]

# Converts list of number l to a string that can be passed as an argument to another program
def list_to_arg_string(l):
    s = ""
    i = 0
    for element in l:
        s = s + str(element)
        i = i + 1
        if(len(l) != i):
            s = s + ","

    return "\"" + s + "\""

def test(it):
    global test_fail
    global summary_table
    gen.dump(it)

    # Error code for this iteration
    iteration_result = 0

    # Call cpp program to run the benchmark since it is much faster and reliable
    # tx only
    if(len(it["tx_channel"]) != 0):
        time.sleep(60) # give network card on host some time to cool down between runs
        iteration_result = os.system("/usr/lib/uhd/examples/benchmark_rate --priority high --tx_rate={} --tx_channels {}  --overrun-threshold 0 --underrun-threshold 0 --drop-threshold 0 --seq-threshold 0".format(it["tx_rate"], list_to_arg_string(it["tx_channel"])))
    # rx only
    else:
        log.pvpkg_log_warning("TX_RATE", "No tx channels on this device. Skipping tx rate test")
        return

    # Set test_fail to the return code of the first failed iteration
    if(iteration_result and not test_fail):
        test_fail = iteration_result

    result_string = "Fail" if iteration_result != 0 else "Pass"

    # Adds this iteration's results to the summary table
    summary_table.append([it["description"], "{:.2f}".format(it["tx_rate"]/1e6), str(it["tx_channel"]), result_string])

def build_report():
    report.insert_title_page("Tx Rate Test")
    report.draw_from_buffer()
    report.save()
    log.pvpkg_log_info("TX_RATE", "PDF report saved at " + report.get_filename())

def main(iterations):
    for it in iterations:
        test(it)

    report.buffer_put("text_large", "Test Summary")
    report.buffer_put("text", " ")
    report.buffer_put("table", summary_table)
    report.buffer_put("text", " ")

## SCRIPT LOGIC ##
if(targs.product == "Vaunt"):
    main(gen.tx_rate())
elif(targs.product == "Lily"):
    main(gen.chestnut.lo_band.tx_rate(4))
elif(targs.product == "Tate" or targs.product == "BasebandTate"):
    main(gen.cyan.lo_band.tx_rate(4))
else:
    test_fail = 1
    log.pvpkg_log_error("TX_RATE", "Invalid product specified")

build_report()
# sys.exit only takes values in range 0-255 benchmark_rate returns EXIT_FAILURE which may be > 255. If that happens replace the value with 1
if(test_fail > 255):
    test_fail = 1
sys.exit(test_fail)

