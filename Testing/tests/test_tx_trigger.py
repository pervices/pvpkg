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
    channels = ','.join(str(x) for x in targs.channels)
    test_fail = test_fail | os.system("/usr/lib/uhd/examples/test_tx_trigger --channels={} --path ./test_tx_trig_files/data.txt --start_time={} --period={} --tx_rate={} --tx_center_freq={} --tx_gain={} --setpoint={} --samples={} --num_trigger={} --gating=dsp > {}".format(channels, it["start_time"], it["period"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["setpoint"], it["sample_count"], it["num_trigger"], name))

    # Flag to indicate that triggers failed to activate
    # Technically this could be caused by anything that returns an error code in UHD, but the trigger failing in time is most likely
    trigger_error = False
    if test_fail != 0:
        trigger_error = True

    #if exist_code != 0

    test_info = [["Center Freq", "Sampling Rate", "Tx Gain", "Period", "Setpoint", "Samples", "Start Time", "Num Trigger"],
                 [it["center_freq"], it["sample_rate"], it["tx_gain"], it["period"], it["setpoint"], it["sample_count"], it["start_time"], it["num_trigger"]]]


    report.buffer_put("text_large", "Test Summary")
    report.buffer_put("text", " ")
    report.buffer_put("table", test_info, "Parameters")
    report.buffer_put("text", " ")

    results = [["Description", "Value", "Acceptance Criteria", "Result"]]
    buffer_info = [["Channel", "Max Buffer Level", "Max difference from A"]]
    # [Ch, MaxLevel, Max difference from A]
    ch_buf_info = []
    for ch in targs.channels:
        ch_buf_info.append([ch, 0, 0])

    # Maximum divergence between channels
    max_div = 0

    # Flag for if there was stale data in the buffer after initialization
    stale_data = False
    # Flag for if data was not accepted by the system while priming
    priming_error = False
    #Flag for if an incorrect number of samples consumed per trigger
    sample_count_error = False


    with open(name, "r") as b:
        lines = b.readlines()
        b.seek(0)

        buffer_filled = False
        first_line = True
        previous_buffer_level = 0

        for line in lines:
            # Print lines so they end up in the logs
            print(line, end='')

            # Array containing the line seperated by " "
            row = line.split()

            all_numeric = True
            for val in row:
                if not val.isnumeric():
                    all_numeric = False
                    break
            if not all_numeric:
                # Not all values in the line are numberic, this is not a data line skip it
                continue

            # Convert values from string to int
            for n in range(len(row)):
                row[n] = int(row[n])

            # The last column indicates the difference in buffer level between channels
            # This value should always be 0 because all channels get the same data and should send the same amount at the same time
            # Having different channels be read at different times is not a concern. The reading is taken as soon as data is sent, and data is sent immediatly after a trigger so the program has almost a full second to read all channels and have them be the same
            if row[-1] != 0:
                if buffer_filled:
                    print("ERROR: discrepency in buffer level between channels")
                else:
                    print("ERROR: discrepency in buffer level between channels while priming")
                test_fail = test_fail | 1

            for ch in range(len(ch_buf_info)):
                # Update maximum buffer level
                ch_buf_info[ch][1] = max(ch_buf_info[ch][1], row[ch])
                # Update maximum difference from channel 0 (should be 0, error check is performaed above)
                ch_buf_info[ch][2] = max(ch_buf_info[ch][2], abs(row[ch] - row[0]))
                max_div = max(max_div, ch_buf_info[ch][2])

            if first_line:
                # Only the first column is checked since the rest should be identical unless the previous check failed
                first_line = False
                previous_buffer_level = row[0]
                # If the buffer had data then data from previous runs wasn't cleared when initializing
                if row[0] != 0:
                    print("ERROR: data in buffer at start")
                    stale_data = True
                    test_fail = test_fail | 1

            elif not buffer_filled:
                # Check if the buffer level is being filled up
                if(row[0] <= previous_buffer_level):
                    print("ERROR: samples not accepted while priming buffer")
                    priming_error = True
                    test_fail = test_fail | 1

                # Record that the buffer has been filled to the desired level
                if(row[0] >= it["setpoint"]):
                    buffer_filled = True

                previous_buffer_level = row[0]

            # During normal streaming between reads data should be consumed and the same amount of data should be sent to replace it
            else:
                if row[0] != previous_buffer_level:
                    print("ERROR: incorrect number of samples consumed by trigger")
                    sample_count_error = True
                    test_fail = test_fail | 1

                previous_buffer_level = row[0]

    divergence_res = "Fail" if max_div != 0 else "Pass"
    stale_data_res = "Fail" if stale_data else "Pass"
    priming_res = "Fail" if priming_error else "Pass"
    sample_count_res = "Fail" if sample_count_error else "Pass"
    trigger_res = "Fail" if trigger_error else "Pass"

    results.append(["Max Divergence", max_div, "== 0", divergence_res])
    results.append(["Stale data", "--", "Starting buffer level > 0", stale_data_res])
    results.append(["Dropped data while priming", "--", "During priming buffer level > buffer level before the previous send", priming_res])
    results.append(["Correct samples per trigger", "--", "During streaming buffer level after each trigger + send is the same", sample_count_res])
    results.append(["Other errors in program", "--", "No other errors (most likely from trigger not activating)", trigger_res])


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
elif(targs.product == "Lily"):
    main(gen.chestnut.lo_band.tx_trigger())
elif(targs.product == "Tate" or targs.product == "BasebandTate"):
    main(gen.cyan.lo_band.tx_trigger())
else:
    print("ERROR: unrecognized product argument", file=sys.stderr)
    test_fail = 1

build_report()
sys.exit(test_fail)

