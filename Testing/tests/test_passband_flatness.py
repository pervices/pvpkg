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


    tx_stack = [ (10.0, it["sample_count" ]) ] # One seconds worth.
    rx_stack = [ (10.0, it["sample_count"]) ]
    vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
    error_detected = 0
    # Process.
    reals = []
    imags = []
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
        peaks, xfp, yfp = sigproc.fft_peaks(comp, it["sample_rate"])
        troughs, xft, yft = sigproc.fft_troughs(comp, it["sample_rate"])
        passband_flat = False
        # Check any of the peaks are the expected wave wave
        # Unlike tx, the rx lo will end up at 0Hz after mixing and therefore not be visible
        for peak in xfp[peaks]:
            for trough in xft[troughs]:
                if np.abs(peak-trough) <= 4:
                    passband_flat = True

        plt.figure()
        plt.title("Channel {} Rx FFT".format(ch), fontsize=14)
        plt.xlabel("Frequency (Hz)", fontsize=12)
        plt.ylabel("Magnitude", fontsize=12)
        plt.plot(xfp, yfp, label="FFT")
        plt.plot(xfp[peaks], yfp[peaks], "x", label="Detected peaks")
        plt.legend()

        s = report.get_image_io_stream()
        plt.savefig(s, format='png')
        plt.close()
        img = report.get_image_from_io_stream(s)
        images.append(img)

        res = ""
        if not passband_flat:
            test_fail = 1
            res = "fail"
        else:
            res = "pass"

    title = "passband flatness"
    report.buffer_put("text_large", title)
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
    main(gen.lo_band_wave_sweep(), "Low Band")
else:
    print("ERROR: unrecognized product argument", file=sys.stderr)
    test_fail = 1

build_report()
sys.exit(test_fail)
