import os
from common import pdf_report
from common import generator as gen
from common import test_args
import sys


targs = test_args.TestArgs(testDesc="Tx and Rx Rate Test")
report = pdf_report.ClassicShipTestReport("tx_rx_rate", targs.serial, targs.report_dir, targs.docker_sha)
test_fail = 0
summary_table = [ ["Description", "Rx Rate (Msps)", "Rx Channels", "Tx Rate (Msps)", "Tx Channels", "Result"] ]

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

    # Filename to store output of program
    name = "tx_rx_rate_log.txt"

    iteration_result = 0

    # Call cpp program to run the benchmark since it is much faster and reliable
    # The ifelse decides whether to pass rx only, tx only, or both args
    if((len(it["rx_channel"])) != 0 and (len(it["tx_channel"]) != 0)):
        iteration_result = os.system("/usr/lib/uhd/examples/benchmark_rate --rx_rate {} --rx_channels {} --tx_rate={} --tx_channels {}  --overrun-threshold 0 --underrun-threshold 0 --drop-threshold 0 --seq-threshold 0 > {}".format(it["rx_rate"], list_to_arg_string(it["rx_channel"]), it["tx_rate"], list_to_arg_string(it["tx_channel"]), name))
    # rx only
    elif(len(it["rx_channel"]) != 0):
        iteration_result = os.system("/usr/lib/uhd/examples/benchmark_rate --rx_rate={} --rx_channels {}  --overrun-threshold 0 --underrun-threshold 0 --drop-threshold 0 --seq-threshold 0 > {}".format(it["rx_rate"], list_to_arg_string(it["rx_channel"]), name))
    # tx only
    else:
        iteration_result = os.system("/usr/lib/uhd/examples/benchmark_rate --tx_rate={} --tx_channels {}  --overrun-threshold 0 --underrun-threshold 0 --drop-threshold 0 --seq-threshold 0 > {}".format(it["tx_rate"], list_to_arg_string(it["tx_channel"]), name))

    # Update flag if the test failed
    test_fail = test_fail | iteration_result

    result_string = "Fail" if iteration_result != 0 else "Pass"

    # Adds this iteration's results to the summary table
    summary_table.append([it["description"], "{:.2f}".format(it["rx_rate"]/1e6), str(it["rx_channel"]), "{:.2f}".format(it["tx_rate"]/1e6), str(it["tx_channel"]), result_string])

def build_report():
    report.insert_title_page("Tx Rx Rate Test")
    report.draw_from_buffer()
    report.save()
    print("PDF report saved at " + report.get_filename())

def main(iterations):
    for it in iterations:
        test(it)

    report.buffer_put("text_large", "Test Summary")
    report.buffer_put("text", " ")
    report.buffer_put("table", summary_table)
    report.buffer_put("text", " ")

## SCRIPT LOGIC ##
if(targs.product == "Vaunt"):
    main(gen.tx_rx_rate())
elif(targs.product == "Lily"):
    main(gen.chestnut.lo_band.tx_rx_rate(4))
    print("Not implemented")
    test_fail = 1
elif(targs.product == "Tate"):
    main(gen.cyan.lo_band.tx_rx_rate(4))
    print("Not implemented")
    test_fail = 1
else:
    test_fail = 1
    print("Error: invalid product specified")

build_report()
sys.exit(test_fail)

