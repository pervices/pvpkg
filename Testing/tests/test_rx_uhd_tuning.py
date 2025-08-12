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
targs = test_args.TestArgs(testDesc="Rx UHD Tuning Test")

report = pdf_report.ClassicShipTestReport("rx_uhd_tuning", targs.serial, targs.report_dir, targs.docker_sha)
test_fail = 0
summary_tables = []

def test(it, data):
    global test_fail
    gen.dump(it)

    # Create manual tune request for rx, use default tuning for tx (just pass center freq)
    rx_tune_request = uhd.tune_request(it["center_freq"], it["rx_lo"])

    tx_stack = [ (5.0, int(2 * it["sample_rate"])) ]
    rx_stack = [ (5.5, int(it["sample_count"])) ]

    try:
        vsnk = engine.manual_tune_run(it["channels"], it["wave_freq"],
                                    it["sample_rate"], it["sample_rate"],
                                    it["center_freq"], rx_tune_request,
                                    it["tx_gain"], it["rx_gain"],
                                    tx_stack, rx_stack)
    except Exception as err:
        build_report()
        sys.exit(1)

    center_freq = "{:.3e}".format(it["center_freq"])
    rx_lo = "{:.2e}".format(it["rx_lo"])
    wave_freq = "{:.1e}".format(it["wave_freq"])

    rx_dsp = it["rx_lo"] - it["center_freq"]
    rx_dsp_sci = "{:.1e}".format(rx_dsp)

    title = "NCO: {}Hz, Center Freq: {}Hz".format(rx_dsp_sci, center_freq)
    test_info = [["Rx NCO (Hz)", "Rx LO (Hz)", "Center Freq (Hz)", "Wave Freq (Hz)", "Rate (SPS)", "Sample Count", "TX Gain (dB)", "RX Gain (dB)"],
                [rx_dsp_sci, rx_lo, center_freq, wave_freq, it["sample_rate"], it["sample_count"], it["tx_gain"], it["rx_gain"]]]

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
        # Check any of the peaks are the expected wave wave
        # Unlike tx, the rx lo will end up at 0Hz after mixing and therefore not be visible
        for peak in xf[peaks]:
            if math.isclose(peak, it["wave_freq"], rel_tol=tolerance):
                tone_present = True

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
        if not tone_present:
            test_fail = 1
            res = "fail"
        else:
            res = "pass"

        data.append([str(rx_dsp_sci) , str(rx_lo), str(center_freq), str(wave_freq), str(ch), str(tone_present),  res])

    report.buffer_put("text_large", title)
    report.buffer_put("table_wide", test_info, "")
    report.buffer_put("text", " ")
    report.buffer_put("image_quad", images, "")
    report.buffer_put("pagebreak")

    return data

def main(iterations, desc):
    data  = [["Rx NCO", "Rx LO", "Center Freq", "Wave Freq", "Channel", "Tone Freq Present", "Result"]]
    for it in iterations:
        test(it, data)
    summary_tables.append([desc, data])

def add_summary_table(title, data):
    report.insert_text_large("{} Testing Summary".format(title))
    report.insert_text("")
    report.insert_table(data)
    report.new_page()

def build_report():
    report.insert_title_page("UHD Rx Tune Request Test")
    for summary in summary_tables:
        add_summary_table(summary[0], summary[1])
    report.draw_from_buffer()
    report.save()
    print("PDF report saved at " + report.get_filename())


## SCRIPT LOGIC ##
if(targs.product == "Vaunt"):
    main(gen.rx_uhd_tune(), "")
elif(targs.product == "Tate" or targs.product == "BasebandTate"):
    main(gen.cyan.mid_band.rx_uhd_tune(), "")
elif(targs.product == "Lily"):
    main(gen.chestnut.mid_band.rx_uhd_tune(), "")
else:
    print("ERROR: unrecognized product argument", file=sys.stderr)
    test_fail = 1
build_report()
sys.exit(test_fail)
