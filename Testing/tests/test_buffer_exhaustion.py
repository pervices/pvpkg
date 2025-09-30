import os
from common import sigproc
from common import engine
from common import generator as gen
from common import pdf_report
from common import test_args
from retrying import retry
import numpy as np
import matplotlib.pyplot as plt
import sys
import time, datetime


targs = test_args.TestArgs(testDesc="Buffer Exhaustion")
report = pdf_report.ClassicShipTestReport("buffer_exhaustion", targs.serial, targs.report_dir, targs.docker_sha)
test_fail = 0
summary_tables = []
buffer_shift = 0

@retry(stop_max_attempt_number = 1)
def test(it, data):
    global test_fail
    test_dnf = False
    gen.dump(it)


    tx_stack = [ (5.0, it["sample_count"]) ] # One seconds worth.
    rx_stack = [ (5.0, int(it["sample_count"]) ) ]
    try:
        vsnk = engine.run(targs.channels, it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
    except Exception as err:
        test_fail = 1

    center_freq = "{:.1e}".format(it["center_freq"])
    wave_freq = "{:.1e}".format(it["wave_freq"])
    title = "Center freq: {}, Wave freq: {}".format(center_freq, wave_freq)
    test_info = [["Center Frequency (Hz)", "Wave Frequency (Hz)", "Sample Rate (SPS)", "Tune Sample Count", "Used Sample Count", "TX Gain (dB)", "RX Gain (dB)"],
                        [center_freq, wave_freq, it["sample_rate"], it["sample_count"],it["sample_count"] - buffer_shift  ,it["tx_gain"], it["rx_gain"]]]

    report.buffer_put("text_large", title)
    report.buffer_put("table_large", test_info, "")
    report.buffer_put("text", " ")
    images = []

    for ch, channel in enumerate(vsnk):
        real = [datum.real for datum in channel.data()]
        imag = [datum.imag for datum in channel.data()]

        fund_real = sigproc.fundamental(real, it["sample_rate"])
        fund_imag = sigproc.fundamental(imag, it["sample_rate"])

        like_real = (float(it["wave_freq"]) / fund_real)
        like_imag = (float(it["wave_freq"]) / fund_imag)

        print("channel %2d: real %10.0f Hz (%8.5f) :: imag %10.0f Hz (%8.5f)" % (targs.channels[ch], fund_real, like_real, fund_imag, like_imag))

        plt.figure()
        plt.title("Channel {}".format(targs.channels[ch]), fontsize=14)
        plt.xlabel("Sample", fontsize=12)
        plt.ylabel("Amplitude", fontsize=12)
        plt.plot(real[0:300], label='real')
        plt.plot(imag[0:300],label='imag')

        s = report.get_image_io_stream()
        plt.savefig(s, format='png')
        plt.close()
        img = report.get_image_from_io_stream(s)
        images.append(img)

        res = ""
        if(like_real > 0.95 and like_real < 1.05 and like_imag > 0.95 and like_imag < 1.05 and not test_dnf):
            res = "pass"
        else:
            res = "fail"
            test_fail = 1

        data.append([str(center_freq), str(wave_freq), str(ch), res])

    report.buffer_put("image_list_dynamic", images, "")
    report.buffer_put("pagebreak")

    return data

def main(iterations, desc):
    data  = [["Centre Freq", "Wave Freq", "Channel", "Result"]]
    for it in iterations:
        test(it, data)
    summary_tables.append([desc, data])

def add_summary_table(title, data):
    report.insert_text_large("{} Testing Summary".format(title))
    report.insert_text("")
    report.insert_table(data)
    report.new_page()

def build_report():
    report.insert_title_page("Buffer Exhaustion Test")
    for summary in summary_tables:
        add_summary_table(summary[0], summary[1])
    report.draw_from_buffer()
    report.save()
    print("PDF report saved at " + report.get_filename())


## SCRIPT LOGIC ##
if(targs.product == "Vaunt"):
    buffer_shift = 74000
    main(gen.lo_band_buffer_exhaust_test(), "Low Band")
elif(targs.product == "Tate" or targs.product == "BasebandTate"):
    buffer_shift = 74000
    main(gen.cyan.lo_band.buffer_exhaust_test(), "Low Band")
elif(targs.product == "Lily"):
    buffer_shift = 74000
    main(gen.chestnut.lo_band.buffer_exhaust_test(), "Low Band")
else:
    print("ERROR: unrecognized product argument", file=sys.stderr)
    test_fail = 1

build_report()
sys.exit(test_fail)
