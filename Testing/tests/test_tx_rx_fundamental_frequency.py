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
import math

targs = test_args.TestArgs(testDesc="Tx Rx Fundamental Frequency Test")
report = pdf_report.ClassicShipTestReport("tx_rx_fundamental_frequency", targs.serial, targs.report_dir, targs.docker_sha)
test_fail = 0
summary_tables = []

@retry(stop_max_attempt_number = 1)
def test(it, data):
    global test_fail
    gen.dump(it)


    tx_stack = [ (5.0, it["sample_count"]) ] # One seconds worth.
    rx_stack = [ (5.0, int(it["sample_count"]) ) ]
    try:
        vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
    except Exception as err:
        build_report()
        sys.exit(1)

    center_freq = "{:.1e}".format(it["center_freq"])
    wave_freq = "{:.1e}".format(it["wave_freq"])
    title = "Center freq: {}, Wave freq: {}".format(center_freq, wave_freq)
    test_info = [["Center Frequency (Hz)", "Wave Frequency (Hz)", "Sample Rate (SPS)", "Sample Count", "TX Gain (dB)", "RX Gain (dB)"],
                        [center_freq, wave_freq, it["sample_rate"], it["sample_count"], it["tx_gain"], it["rx_gain"]]]

    time_images = []
    freq_images = []
    for ch, channel in enumerate(vsnk):
        real = [datum.real for datum in channel.data()]
        imag = [datum.imag for datum in channel.data()]

        # TIME DOMAIN ANALYSIS
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
        time_images.append(img)

        fun_freq_res = ""
        if(like_real > 0.95 and like_real < 1.05 and like_imag > 0.95 and like_imag < 1.05):
            fun_freq_res = "Pass"
        else:
            fun_freq_res = "Fail"
            test_fail = 1

        # FREQUENCY DOMAIN ANALYSIS
        comp = np.array([])
        if len(real) == len(imag):
            for idx, point in enumerate(real):
                comp = np.append(comp, complex(point, imag[idx]))
        else:
            raise Exception("Length of real data does not match length of imaginary data. Real len: {} Imag len: {}".format(len(real), len(imag)))
        peaks, xf, yf = sigproc.fft_peaks(comp, it["sample_rate"])

        tolerance = 0.05  # within 5% of expected frequency
        expected_tone_mag = -1
        spur_present = False
        max_spur_mag = -1
        max_spur_freq = -1
        for peak in xf[peaks]:
            if math.isclose(peak, it["wave_freq"], rel_tol=tolerance):
                expected_tone_mag = yf[peak]
            else:

        print("Spur found: {}, Spur freq: {}, Spur mag: {}".format(spur_present, max_spur_freq, max_spur_mag))

        plt.figure()
        plt.title("Channel {} Rx FFT".format(ch), fontsize=14)
        plt.xlabel("Frequency [Hz]", fontsize=12)
        plt.ylabel("Magnitude [dB]", fontsize=12)
        plt.plot(xf, yf, label="FFT")
        plt.plot(xf[peaks], yf[peaks], "x", label="Detected peaks")
        plt.legend()

        s = report.get_image_io_stream()
        plt.savefig(s, format='png')
        plt.close()
        img = report.get_image_from_io_stream(s)
        freq_images.append(img)

        # data formatted as [center_freq, wave_freq, channel, frequency found, frequency result, spurs within 30dB found?, if yes strongest spur freq]
        data.append([str(center_freq), str(wave_freq), str(ch), fun_freq_res])

    report.buffer_put("text_large", title)
    report.buffer_put("table_wide", test_info, "")
    report.buffer_put("text", " ")
    report.buffer_put("image_quad", time_images, "")
    report.buffer_put("pagebreak")
    report.buffer_put("image_quad", freq_images, "")
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
    report.insert_title_page("Fundamental Frequency Test")
    for summary in summary_tables:
        add_summary_table(summary[0], summary[1])
    report.draw_from_buffer()
    report.save()
    print("PDF report saved at " + report.get_filename())


## SCRIPT LOGIC ##
if(targs.product == "Vaunt"):
    main(gen.lo_band_wave_sweep(), "Low Band")
    main(gen.hi_band_wave_sweep(), "High Band")
else:
    main(gen.cyan.lo_band.wave_sweep(4), "Low Band")
    main(gen.cyan.mid_band.wave_sweep(4), "Mid Band")
    main(gen.cyan.hi_band.wave_sweep(4), "High Band")

build_report()
sys.exit(test_fail)
