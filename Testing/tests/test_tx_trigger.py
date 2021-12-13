import os

def main():

    name = "tx_trigger_log.txt"

    # os.system("/home/notroot/libuhd/examples/test_tx_trigger.cpp > %s" % name)
    # TODO: Check if the following file exists; if it doesn't, throw and error and
    # indicate that the test_tx_trigger example binary was not found
    # Using invokation from tx_trig pkg
    os.system("/usr/lib/uhd/examples/test_tx_trigger --path ./test_tx_trig_files/data.txt --start_time=5 --period=20 --tx_rate=10156250 --tx_center_freq=0 --tx_gain=20 --setpoint=1000 --samples=480 --gating=dsp > %s" % name)

    with open(name, "r") as b:

        lines = b.readlines()

        # For removing noise SMA setup / teardown.
        pad = 500

        # Max - Min for four columns stored in column 8 of log.
        col = 8

        # Max divergance for four channels.
        thresh = 10

        # A sliding window is used because sometimes the buffer level is retrieved by UDP while being updated by the FPGA.
        a = 0
        b = 0
        c = 0

        for line in lines[pad : -pad]:

            row = line.split()

            # Slide the window.
            a = b
            b = c
            c = float(row[col])

            assert a < thresh or b < thresh or c < thresh

main()

