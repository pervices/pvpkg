from gnuradio import analog
from gnuradio import blocks
from gnuradio import uhd
from gnuradio import gr
import numpy as np
import sys
from common import crimson
from common import pdf_report
from common import test_args

#Setup argument parsing
targs = test_args.TestArgs(testDesc="Tx Stack Test")

report = pdf_report.ClassicShipTestReport("tx_stack", targs.serial, targs.report_dir, targs.docker_sha)
test_fail = 0

def main():

    """
    This is a MANUAL test.
    Hook an oscilloscope up to anyone of the four channels and look
    for a few one second bursts separate by some (human seeable) time interval.
    """
    global test_fail

    if(targs.product == 'Tate'):
        # Cyan NRNT Setup.
        channels = np.array([0,1,2,3])
        sample_rate = 100e6
        sample_count = int(sample_rate)
    elif(targs.product == 'Vaunt'):
        # Crimson TNG Setup.
        channels = np.array([0,1,2,3])
        sample_rate = 20312500
        sample_count = int(sample_rate)
    elif(targs.product == 'Lily'):
        # Chestnut Setup.
        channels = np.array([0,1,2,3])
        sample_rate = 100e6
        sample_count = int(sample_rate)
    else:
        print("ERROR: unrecognized product argument", file=sys.stderr)
        test_fail = 1


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

