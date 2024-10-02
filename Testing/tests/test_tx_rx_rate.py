import os
from common import pdf_report
from common import generator as gen
from common import test_args
import sys


targs = test_args.TestArgs(testDesc="Tx and Rx Rate Test")
report = pdf_report.ClassicShipTestReport("tx_rx_rate", targs.serial, targs.report_dir, targs.docker_sha)
test_fail = 0

# Converts list of number l to a string that can be passed as an argument to another program
def list_to_arg_string(l):
    s = ""
    for element in l:
        s = s + str(element)

    return "\"" + s + "\""

def test(it):
    global test_fail
    gen.dump(it)

    name = "tx_rx_rate_log.txt"
    print("T1")

    # Call cpp program to run the benchmark since it is much faster and reliable
    if((len(it["rx_channel"])) != 0 and (len(it["rx_channel"]) != 0)):
        print("T2")
        command = "/usr/lib/uhd/examples/benchmark_rate --rx_rate {} --rx_channels {} --tx_rate={} --tx_channels {}  --overrun-threshold 0 --underrun-threshold 0 --drop-threshold 0 --seq-threshold 0 > {}".format(it["rx_rate"], list_to_arg_string(it["rx_channel"]), it["tx_rate"], list_to_arg_string(it["tx_channel"]), name)
        print("T2.5")
        test_fail = test_fail | os.system(command)
        print("T3")
    # rx only
    elif(len(it["rx_channel"]) != 0):
        test_fail = test_fail | os.system("/usr/lib/uhd/examples/benchmark_rate --rx_rate={} --rx_channels {}  --overrun-threshold 0 --underrun-threshold 0 --drop-threshold 0 --seq-threshold 0 > {}".format(it["rx_rate"], list_to_arg_string(it["rx_channel"]), name))
    # tx only
    else:
        test_fail = test_fail | os.system("/usr/lib/uhd/examples/benchmark_rate --tx_rate={} --tx_channels {}  --overrun-threshold 0 --underrun-threshold 0 --drop-threshold 0 --seq-threshold 0 > {}".format(it["tx_rate"], list_to_arg_string(it["tx_channel"]), name))

    print("T5")

    rate_error = test_fail != 0

    test_info = [ ["Description", "Rx Rate", "Rx Channels", "Tx Rate", "Tx Channels"],
                 [it["description"], it["rx_rate"], str(it["rx_channel"]), it["tx_rate"], str(it["tx_channel"])] ]

    report.buffer_put("text_large", "Test Summary")
    report.buffer_put("text", " ")
    report.buffer_put("table", test_info)
    report.buffer_put("text", " ")

    print("T10")

def build_report():
    report.insert_title_page("Tx Rx Rate Test")
    report.draw_from_buffer()
    report.save()
    print("PDF report saved at " + report.get_filename())

def main(iterations):
    for it in iterations:
        test(it)

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

