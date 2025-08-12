from gnuradio import uhd
from common import sigproc
from common import engine
from common import generator as gen
from common import pdf_report
from common import test_args
import numpy as np
import math
import matplotlib.pyplot as plt
import sys

#Setup argument parsing
targs = test_args.TestArgs(testDesc="Tx UHD Tuning Test")

report = pdf_report.ClassicShipTestReport("tx_uhd_tuning", targs.serial, targs.report_dir, targs.docker_sha)
test_fail = 0
summary_tables = []

def test(it, data):
    global test_fail
    gen.dump(it)

    # Create manual tune request for tx, use default tuning for rx (just pass center freq)
    tx_tune_request = uhd.tune_request(it["center_freq"], it["tx_lo"])

    tx_stack = [ (5.0, int(it["sample_count"])) ] # One seconds worth.
    rx_stack = [ (5.0, int(it["sample_count"]) ) ]

    try:
        vsnk = engine.manual_tune_run(it["channels"], it["wave_freq"],
                                    it["sample_rate"], it["sample_rate"],
                                    tx_tune_request, it["center_freq"],
                                    it["tx_gain"], it["rx_gain"],
                                    tx_stack, rx_stack)
    except Exception as err:
        build_report()
        sys.exit(1)

    center_freq = "{:.3e}".format(it["center_freq"])
    tx_lo = "{:.2e}".format(it["tx_lo"])
    wave_freq = "{:.1e}".format(it["wave_freq"])

    tx_dsp = it["tx_lo"] - it["center_freq"]
    tx_dsp_sci = "{:.1e}".format(tx_dsp)

    title = "NCO: {}Hz, Center Freq: {}Hz".format(tx_dsp_sci, center_freq)
    test_info = [["Tx NCO (Hz)", "Tx LO (Hz)", "Center Freq (Hz)", "Wave Freq (Hz)", "Rate (SPS)", "Sample Count", "TX Gain (dB)", "RX Gain (dB)"],
                [tx_dsp_sci, tx_lo, center_freq, wave_freq, it["sample_rate"], it["sample_count"], it["tx_gain"], it["rx_gain"]]]

    images = []
    for ch, channel in enumerate(vsnk):
        real = [datum.real for datum in channel.data()]
        imag = [datum.imag for datum in channel.data()]

        comp = np.array([])
        if len(real) == len(imag):
            for idx, point in enumerate(real):
                comp = np.append(comp, complex(point, imag[idx]))
        else:
            raise Exception("Length of real data does not match length of imaginary data. Real len: {} Imag len: {}".format(len(real), len(imag)))

        # Find all peaks that that are significant enough that they might be the lo or wave
        peaks, xf, yf = sigproc.fft_peaks(comp, it["sample_rate"])
        tolerance = 0.05  # within 5% of expected frequency
        tone_present = False
        LO_feedthrough_present = False
        # Check if each of the peaks found was the lo or the wave
        for peak in xf[peaks]:
            if math.isclose(peak, it["wave_freq"], rel_tol=tolerance):
                tone_present = True
            elif math.isclose(peak, int(tx_dsp), rel_tol=tolerance):        # LO feedthrough artifact will be shifted from 0Hz by nco, so look for it at dsp nco value
                LO_feedthrough_present = True

        plt.figure()
        plt.title("Channel {} Rx FFT".format(ch), fontsize=14)
        plt.xlabel("Frequency (Hz)", fontsize=12)
        plt.ylabel("Magnitude", fontsize=12)
        plt.plot(xf, yf, label="FFT")
        plt.plot(xf[peaks], yf[peaks], "x", label="Detected peaks")
        plt.legend()

        s = report.get_image_io_stream()
        plt.savefig(s, format='png')
        plt.close()
        img = report.get_image_from_io_stream(s)
        images.append(img)

        res = ""
        if not tone_present or not LO_feedthrough_present:
            test_fail = 1
            res = "fail"
        else:
            res = "pass"

        data.append([str(tx_dsp_sci) , str(tx_lo), str(center_freq), str(wave_freq), str(ch), str(tone_present), str(LO_feedthrough_present),  res])

    report.buffer_put("text_large", title)
    report.buffer_put("table_wide", test_info, "")
    report.buffer_put("text", " ")
    report.buffer_put("image_quad", images, "")
    report.buffer_put("pagebreak")

    return data

def main(iterations, desc):
    data  = [["Tx NCO", "Tx LO", "Center Freq", "Wave Freq", "Channel", "Tone Freq Present", "LO Feedthrough Present", "Result"]]
    for it in iterations:
        test(it, data)
    summary_tables.append([desc, data])

def add_summary_table(title, data):
    report.insert_text_large("{} Testing Summary".format(title))
    report.insert_text("")
    report.insert_table(data)
    report.new_page()

def build_report():
    report.insert_title_page("UHD Tx Tune Request Test")
    for summary in summary_tables:
        add_summary_table(summary[0], summary[1])
    report.draw_from_buffer()
    report.save()
    print("PDF report saved at " + report.get_filename())


## SCRIPT LOGIC ##
if(targs.product == "Vaunt"):
    main(gen.tx_uhd_tune(), "")
elif(targs.product == "Tate"):
    main(gen.cyan.mid_band.tx_uhd_tune(), "")
elif(targs.product == "Lily"):
    main(gen.chestnut.mid_band.tx_uhd_tune(), "")
else:
    print("ERROR: unrecognized product argument", file=sys.stderr)
    test_fail = 1
build_report()
sys.exit(test_fail)
