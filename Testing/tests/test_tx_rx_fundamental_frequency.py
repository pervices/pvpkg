import os
from common import sigproc
from common import engine
from common import generator as gen
from common import pdf_report
from common import test_args
from common import log
from retrying import retry
import numpy as np
import matplotlib.pyplot as plt
import sys
import time, datetime


targs = test_args.TestArgs(testDesc="Tx Rx Fundamental Frequency Test")
report = pdf_report.ClassicShipTestReport("tx_rx_fundamental_frequency", targs.serial, targs.report_dir, targs.docker_sha)
test_fail = 0
summary_tables = []
max_attempts = 1
attempt_num = 0

@retry(stop_max_attempt_number = 1)
def test(it, data):
    global test_fail
    global attempt_num
    attempt_num += 1
    test_dnf = False
    gen.dump(it)


    tx_stack = [ (5.0, it["sample_count"]) ] # One seconds worth.
    rx_stack = [ (5.0, int(it["sample_count"]) ) ]
    try:
        vsnk = engine.run(targs.channels, it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
    except Exception as err:
        test_fail = 1
        if attempt_num < max_attempts:
            raise
        else:
            test_dnf = True

    center_freq = "{:.1e}".format(it["center_freq"])
    wave_freq = "{:.1e}".format(it["wave_freq"])
    title = "Center freq: {}, Wave freq: {}".format(center_freq, wave_freq)
    test_info = [["Center Frequency (Hz)", "Wave Frequency (Hz)", "Sample Rate (SPS)", "Sample Count", "TX Gain (dB)", "RX Gain (dB)", "Attempts"],
                        [center_freq, wave_freq, it["sample_rate"], it["sample_count"], it["tx_gain"], it["rx_gain"], attempt_num]]

    report.buffer_put("text_large", title)
    report.buffer_put("table_large", test_info, "")
    report.buffer_put("text", " ")
    images = []

    # Since engine.run failed, exit test early with DNF for missing data
    if attempt_num >= max_attempts and test_dnf:
        data.append([str(center_freq), str(wave_freq), "DNF", "fail"])
        report.buffer_put("pagebreak")
        return data

    for ch, channel in enumerate(vsnk):
        real = [datum.real for datum in channel.data()]
        imag = [datum.imag for datum in channel.data()]

        fund_real = sigproc.fundamental(real, it["sample_rate"])
        fund_imag = sigproc.fundamental(imag, it["sample_rate"])

        like_real = (float(it["wave_freq"]) / fund_real)
        like_imag = (float(it["wave_freq"]) / fund_imag)

        log.pvpkg_log_info("TX_RX_FUNDAMENTAL_FREQUENCY", "channel %2d: real %10.0f Hz (%8.5f) :: imag %10.0f Hz (%8.5f)" % (targs.channels[ch], fund_real, like_real, fund_imag, like_imag))

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

        data.append([str(center_freq), str(wave_freq), str(ch), attempt_num, res])

    report.buffer_put("image_list_dynamic", images, "")
    report.buffer_put("pagebreak")

    return data

def main(iterations, desc):
    global attempt_num
    data  = [["Centre Freq", "Wave Freq", "Channel", "Attempts", "Result"]]
    for it in iterations:
        attempt_num = 0
        test(it, data)
    summary_tables.append([desc, data])

def add_summary_table(title, data):
    report.insert_text_large("{} Testing Summary".format(title))
    report.insert_text("")
    report.insert_table(data)
    report.new_page()

def build_report():
    report.insert_title_page("Fundamental Frequency Test")
    for summary in summary_tables:
        add_summary_table(summary[0], summary[1])
    report.draw_from_buffer()
    report.save()
    log.pvpkg_log_info("TX_RX_FUNDAMENTAL_FREQUENCY", "PDF report saved at " + report.get_filename())


## SCRIPT LOGIC ##
if(targs.product == "Vaunt"):
    main(gen.lo_band_wave_sweep(), "Low Band")
    main(gen.hi_band_wave_sweep(), "High Band")
elif(targs.product == "Tate"):
    main(gen.cyan.lo_band.wave_sweep(), "Low Band")
    main(gen.cyan.mid_band.wave_sweep(), "Mid Band")
    main(gen.cyan.hi_band.wave_sweep(), "High Band")
elif(targs.product == "BasebandTate"):
    main(gen.cyan.lo_band.wave_sweep(), "Low Band")
    main(gen.cyan.mid_band.wave_sweep(), "Mid Band")
elif(targs.product == "Lily"):
    main(gen.chestnut.lo_band.wave_sweep(), "Low Band")
    main(gen.chestnut.mid_band.wave_sweep(), "Mid Band")
    main(gen.chestnut.hi_band.wave_sweep(), "High Band")
else:
    log.pvpkg_log_error("TX_RX_FUNDAMENTAL_FREQUENCY", "Unrecognized product argument")
    test_fail = 1

build_report()
sys.exit(test_fail)
