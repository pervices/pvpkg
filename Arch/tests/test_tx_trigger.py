import os

def main():

    name = "tx_trigger_log.txt"

    os.system("/home/notroot/gnuradio/examples/test_tx_trigger > %s" % name)

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

