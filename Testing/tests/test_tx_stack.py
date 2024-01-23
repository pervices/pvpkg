from gnuradio import analog
from gnuradio import blocks
from gnuradio import uhd
from gnuradio import gr
import numpy as np
import sys
from common import crimson
from common import pdf_report

import argparse

#Setup argument parsing
parser = argparse.ArgumentParser(description = "Tx stack test")
parser.add_argument('-s', '--serial', required=False, default="", help="Serial number of the unit")
parser.add_argument('-p', '--product', required=False, default="v", help="Serial number of the unit")
parser.add_argument('-o', '--output', required=False, default="", help="Report output directory")
args = parser.parse_args()
serial_num = args.serial
product = args.product
out_dir = args.output

report = pdf_report.ClassicShipTestReport("tx_stack", serial_num, out_dir)
test_fail = 0

def main():

    """
    This is a MANUAL test.
    Hook an oscilloscope up to anyone of the four channels and look
    for a few one second bursts separate by some (human seeable) time interval.
    """

    if(product == 't'):
        # Cyan NRNT Setup.
        channels = np.array([0,1,2,3])
        sample_rate = 100e6
        sample_count = int(sample_rate)

    elif(product =='v'):
        # Crimson TNG Setup.
        channels = np.array([0,1,2,3])
        sample_rate = 20312500
        sample_count = int(sample_rate)

    else:
        print("Value of product argument must either be 'v' for vaunt or 't' for tate")
        sys.exit(1)

    global test_fail

    # Waveform setup.
    wave_center = 15e6
    wave_freq = 1.0e6
    wave_ampl = 2.0e4

    # Generates complex samples.
    sigs = [analog.sig_source_c(
        sample_rate, analog.GR_SIN_WAVE, wave_freq, wave_ampl, 0.0)
        for ch in channels]

    # Stops flowgraph when sample size is reached.
    heds = [blocks.head(gr.sizeof_gr_complex, sample_count)
        for ch in channels]

    # Converts complex floats to interleaved shorts.
    c2ss = [blocks.complex_to_interleaved_short(True)
        for ch in channels]

    test_info = [["Center Freq", "Wave Freq", "Wave Ampl", "Sample Rate", "Sample Count", "Result"]]
    try:
        # Takes interleaved shorts and outputs to Crimson/Cyan.
        csnk = crimson.get_snk_s(channels, sample_rate, wave_center, 0.0)

        """                                       +-----------+
        +---------+   +---------+   +---------+   |           |
        | sigs[0] |-->| heds[0] |-->| c2ss[0] |-->|ch[0]      |
        +---------+   +---------+   +---------+   |           |
        +---------+   +---------+   +---------+   |           |
        | sigs[1] |-->| heds[1] |-->| c2ss[1] |-->|ch[1]      |
        +---------+   +---------+   +---------+   |           |
                                                |           |
        +---------+   +---------+   +---------+   |           |
        | sigs[N] |-->| heds[N] |-->| c2ss[N] |-->|ch[N]      |
        +---------+   +---------+   +---------+   |      csnk |
                                                +-----------+
        """

        # Connects flowgraph.
        flowgraph = gr.top_block()
        for ch in channels:
            flowgraph.connect(sigs[ch], heds[ch])
            flowgraph.connect(heds[ch], c2ss[ch])
            flowgraph.connect(c2ss[ch], (csnk, ch))

        # Runs each TX command at specified start times.
        csnk.set_time_now(uhd.time_spec(0.0))
        for second in range(5, 25, 5):
            csnk.set_start_time(uhd.time_spec(second))

            # Flowgraph stop running when head count is full.
            flowgraph.run()

            # Sets head count to zero for next TX command start time.
            for ch in channels:
                heds[ch].reset()

        test_info.append([wave_center, wave_freq, wave_ampl, sample_rate, sample_count, "Pass"])

    except Exception as err:
        err_table = [["Error Message"], [err]]
        test_info.append([wave_center, wave_freq, wave_ampl, sample_rate, sample_count, "Fail"])
        test_fail = 1

    report.buffer_put("text_large", "Test Summary")
    report.buffer_put("table", test_info, "")
    if(test_fail):
        report.buffer_put("text", "")
        report.buffer_put("text", "")
        report.buffer_put("table", err_table, "")


report.insert_title_page("Tx Stack Test")
main()
report.draw_from_buffer()
report.save()
print("PDF report saved at " + report.get_filename())
sys.exit(test_fail)

