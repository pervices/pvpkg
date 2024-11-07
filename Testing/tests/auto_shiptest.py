import os
from common import sigproc
from common import engine
from common import generator as gen
from common import pdf_report
from common import test_args
import numpy as np
import matplotlib.pyplot as plt
import sys
import time, datetime


targs = test_args.TestArgs(testDesc="Automated Shiptest")
report = pdf_report.ClassicShipTestReport("automated_shiptest", targs.serial, targs.report_dir, targs.docker_sha)
test_fail = 0
freq_summary_table = ["Test Frequency", "ChA", "ChB", "ChC", "ChD", "Result"]
snr_summary_table = ["Test Frequency", "ChA", "ChB", "ChC", "ChD", "Result"]
spur_summary_table = ["Test Frequency", "ChA", "ChB", "ChC", "ChD", "Result"]
gain_var_summary_table = ["Test Frequency", "ChA", "ChB", "ChC", "ChD", "Max Diff", "Result"]

def test(it, summary_table):
    global test_fail
    gen.dump(it)


    tx_stack = [ (5.0, int(it["sample_count"])) ] # One seconds worth.
    rx_stack = [ (5.0, int(it["sample_count"]) ) ]
    try:
        vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
    except Exception as err:
        build_report()
        sys.exit(1)

    center_freq = "{:.1e}".format(it["center_freq"])
    wave_freq = "{:.1e}".format(it["wave_freq"])
    title = "Center freq: {}, Wave freq: {}".format(center_freq, wave_freq)
    test_info = [["Center Frequency (Hz)", "Wave Frequency (Hz)", "Sample Rate (SPS)", "Sample Count", "TX Gain", "RX Gain"],
                        [center_freq, wave_freq, it["sample_rate"], it["sample_count"], it["tx_gain"], it["rx_gain"]]]

    time_domain_images = []
    freq_domain_images = []
    for ch, channel in enumerate(vsnk):
        real = [datum.real for datum in channel.data()]
        imag = [datum.imag for datum in channel.data()]

        ## Frequency check ##
        fund_real = sigproc.fundamental(real, it["sample_rate"])
        fund_imag = sigproc.fundamental(imag, it["sample_rate"])


        like_real = (float(it["wave_freq"]) / fund_real)
        like_imag = (float(it["wave_freq"]) / fund_imag)

        print("channel %2d: real %10.0f Hz (%8.5f) :: imag %10.0f Hz (%8.5f)" % (it["channels"][ch], fund_real, like_real, fund_imag, like_imag))

        plt.figure()
        plt.title("Channel {}".format(ch), fontsize=14)
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
        if(like_real > 0.95 and like_real < 1.05 and like_imag > 0.95 and like_imag < 1.05):
            res = "pass"
        else:
            res = "fail"
            test_fail = 1

        data.append([str(center_freq), str(wave_freq), str(ch), res])

    ## Add plots to report ##
    report.buffer_put("text_large", title)
    report.buffer_put("table_wide", test_info, "")
    report.buffer_put("text", " ")
    report.buffer_put("image_quad", images, "")
    report.buffer_put("pagebreak")

    ## Update summary tables ##
    freq_summary_table.append([it["center_freq"], chA_freq, chB_freq, chC_freq, chD_freq, freq_result])
    snr_summary_table.append([it["center_freq"], chA_snr, chB_snr, chC_snr, chD_snr, snr_result])
    spur_summary_table.append([it["center_freq"], chA_spur, chB_spur, chC_spur, chD_spur, spur_result])
    gain_var_summary_table.append([it["center_freq"], chA_peak, chB_peak, chC_peak, chD_peak, peak_max_diff , gain_var_result])

    return data

def main(iterations):
    for it in iterations:
        test(it, summary_table)
    

def build_report():
    report.insert_title_page("Automated Ship Test")
    
    report.insert_text_large("Testing Summary")
    report.insert_text("")
    report.insert_table(summary_table)
    report.new_page()

    report.draw_from_buffer()
    report.save()
    print("PDF report saved at " + report.get_filename())


## -------SCRIPT LOGIC----------- ##
if(targs.product == "Vaunt"):
    main(gen.ship_test_crimson())
elif(targs.product == "Tate"):
    main(gen.ship_test_cyan())
elif(targs.product == "Lily"):
    main(gen.ship_test_chestnut())

build_report()
sys.exit(test_fail)
