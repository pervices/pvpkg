import os
from common import pdf_report
from common import generator as gen
from common import test_args
import sys


targs = test_args.TestArgs(testDesc="Basic Tx Trigger Test")
report = pdf_report.ClassicShipTestReport("tx_trigger", targs.serial, targs.report_dir, targs.docker_sha)
test_fail = 0

def test(it):
    global test_fail
    gen.dump(it)

    name = "tx_trigger_log.txt"

    # os.system("/home/notroot/libuhd/examples/test_tx_trigger.cpp > %s" % name)
    # TODO: Check if the following file exists; if it doesn't, throw and error and
    # indicate that the test_tx_trigger example binary was not found
    # Using invokation from tx_trig pkg
    os.system("/usr/lib/uhd/examples/test_tx_trigger --path ./test_tx_trig_files/data.txt --start_time={} --period={} --tx_rate={} --tx_center_freq={} --tx_gain={} --setpoint={} --samples={} --num_trigger={} --gating=dsp > {}".format(it["start_time"], it["period"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["setpoint"], it["sample_count"], it["num_trigger"], name))

    test_info = [["Center Freq", "Sampling Rate", "Tx Gain", "Period", "Setpoint", "Samples", "Start Time", "Num Trigger"],
                 [it["center_freq"], it["sample_rate"], it["tx_gain"], it["period"], it["setpoint"], it["sample_count"], it["start_time"], it["num_trigger"]]]


    report.buffer_put("text_large", "Test Summary")
    report.buffer_put("text", " ")
    report.buffer_put("table", test_info, "Parameters")
    report.buffer_put("text", " ")

    results = [["Description", "Value", "Acceptance Criteria", "Result"]]
    buffer_info = [["Channel", "Max Buffer Level", "Average Buffer Level"]]
    # [Ch, MaxLevel, AvLevel]
    ch_buf_info = [[0, 0, 0],
                   [1, 0, 0],
                   [2, 0, 0],
                   [3, 0, 0],]
    max_div = 0

    with open(name, "r") as b:
        lines = b.readlines()
        b.seek(0)
        print(b.read())

        # For removing noise SMA setup / teardown.
        pad = 50

        # Max - Min for four columns stored in column 4 (indexed at 0) of log.
        col = 4

        # Max divergence for four channels.
        thresh = 10

        # A sliding window is used because sometimes the buffer level is retrieved by UDP while being updated by the FPGA.
        a = 0
        b = 0
        c = 0
        i = 0
        for line in lines[pad : len(lines) - pad]:

            row = line.split()
            if len(row) > col:      # Log has some unrelated info printed during setup/teardown, ignore these lines.
                # Slide the window.
                a = b
                b = c
                c = float(row[col])

                i += 1
                ch_buf_info[0][1] = int(row[0]) if (int(row[0]) > ch_buf_info[0][1]) else ch_buf_info[0][1]     # ChA buffer level max
                ch_buf_info[0][2] = round(((ch_buf_info[0][2]*(i-1)) + float(row[0]))/i, 3)                     # ChA buffer level average
                ch_buf_info[1][1] = int(row[1]) if (int(row[1]) > ch_buf_info[1][1]) else ch_buf_info[1][1]     # ChB buffer level max
                ch_buf_info[1][2] = round(((ch_buf_info[1][2]*(i-1)) + float(row[1]))/i, 3)                     # ChB buffer level average
                ch_buf_info[2][1] = int(row[2]) if (int(row[2]) > ch_buf_info[2][1]) else ch_buf_info[2][1]     # ChC buffer level max
                ch_buf_info[2][2] = round(((ch_buf_info[2][2]*(i-1)) + float(row[2]))/i, 3)                     # ChC buffer level average
                ch_buf_info[3][1] = int(row[3]) if (int(row[3]) > ch_buf_info[3][1]) else ch_buf_info[3][1]     # ChD buffer level max
                ch_buf_info[3][2] = round(((ch_buf_info[3][2]*(i-1)) + float(row[3]))/i, 3)                     # ChD buffer level average

                # Only fail if the past three trigger events were above threshold. The UHD program is not currently set up to grab the channel buffer levels
                # in parrallel. If a trigger event happens in the middle of reading the channel levels, it will appear as though there is a huge difference.
                try:
                    assert a < thresh or b < thresh or c < thresh
                except:
                    test_fail = 1
                    max_div = max(a, b, c)

    # if any of the channels have an average or max buffer level of 0, something went wrong in the test
    for i in range(2,4):
        for j in range (2,3):
            if ch_buf_info[i][j] == 0:
                test_fail = 1
                print("ERROR: Empty buffer found during tx trigger test.")
                break
        else:
            continue
        break

    res = "Fail" if test_fail else "Pass"
    results.append(["Max Divergence", max_div, "< {}".format(thresh), res])
    report.buffer_put("table", results, "Results")
    report.buffer_put("text", " ")
    for row in ch_buf_info:
        buffer_info.append(row)
    report.buffer_put("table", buffer_info, "Buffer Information")


def build_report():
    report.insert_title_page("Tx Trigger Test")
    report.draw_from_buffer()
    report.save()
    print("PDF report saved at " + report.get_filename())

def main(iterations):
    for it in iterations:
        test(it)

## SCRIPT LOGIC ##
if(targs.product == "Vaunt"):
    main(gen.tx_trigger())
else:
    main(gen.cyan.lo_band.tx_trigger(4))

build_report()
sys.exit(test_fail)

