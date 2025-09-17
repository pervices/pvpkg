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
targs = test_args.TestArgs(testDesc="Passband Flatness Test")

report = pdf_report.ClassicShipTestReport("passband_flatness_test", targs.serial, targs.report_dir, targs.docker_sha)
test_fail = 0
summary_tables = []
channel_peak = []
plot_points_xf = []
plot_points_yf = []
plot_points_peaks = []
images = []
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
    xfp = []
    yfp = []
    peaksp = []
    largest_peaks = []
    for ch, channel in enumerate(vsnk):
        real = [datum.real for datum in channel.data()]
        imag = [datum.imag for datum in channel.data()]
        comp = np.array([0,0,0,0])
        if len(real) == len(imag):
            for idx, point in enumerate(real):
                comp = np.append(comp, complex(point, imag[idx]))
        else:
            raise Exception("Length of real data does not match length of imaginary data. Real len: {} Imag len: {}".format(len(real), len(imag)))

        # Find all peaks that that are significant enough that they might be the lo or wave
        peaks, xf, yf = sigproc.fft_peaks(comp, it["sample_rate"])
        passband_flat = False
        # Check any of the peaks are the expected wave wave
        # Unlike tx, the rx lo will end up at 0Hz after mixing and therefore not be visible
        largest_peak = np.max(yf[peaks])
        largest_peaks.append(largest_peak)
        xfp.append(xf)
        yfp.append(yf)
        peaksp.append(peaks)
    plot_points_xf.append(xfp)
    plot_points_yf.append(yfp)
    plot_points_peaks.append(peaksp)
    channel_peak.append(largest_peaks)
    return data

def main(iterations, desc):
    data  = [["Center Freq", "Wave Freq", "Channel", "Result"]]
    for it in iterations:
        test(it, data)

    summary_tables.append([desc, data])
    passband_flat = []

    for ch in list(range(4)):
        channel_test = []
        channel_test.append(channel_peak[0][ch])
        channel_test.append(channel_peak[1][ch])
        channel_test.append(channel_peak[2][ch])
        channel_max = np.max(channel_test)
        channel_min = np.min(channel_test)
        if np.abs(channel_max - channel_min) <= 4 :
            passband_flat.append("Pass")
        else:
            passband_flat.append("Fail")
        plt.figure()
        plt.title("Channel {} Rx FFT".format(ch), fontsize=14)
        plt.xlabel("Frequency (Hz)", fontsize=12)
        plt.ylabel("Magnitude", fontsize=12)
        plt.plot(plot_points_xf[0][ch], plot_points_yf[0][ch], label="FFT")
        plt.plot(plot_points_xf[1][ch], plot_points_yf[1][ch], label="FFT")
        plt.plot(plot_points_xf[2][ch], plot_points_yf[2][ch], label="FFT")
        plt.plot(plot_points_xf[0][ch][plot_points_peaks[0][ch]], plot_points_yf[0][ch][plot_points_peaks[0][ch]],color='red' ,"x", label="Detected peaks")
        plt.plot(plot_points_xf[1][ch][plot_points_peaks[1][ch]], plot_points_yf[1][ch][plot_points_peaks[1][ch]],color='red',"x", label="Detected peaks")
        plt.plot(plot_points_xf[2][ch][plot_points_peaks[2][ch]], plot_points_yf[2][ch][plot_points_peaks[2][ch]],color='red',"x", label="Detected peaks")
        plt.legend()

        s = report.get_image_io_stream()
        plt.savefig(s, format='png')
        plt.close()
        img = report.get_image_from_io_stream(s)
        images.append(img)
    test_info = [["Channel Peak Information (dB):","A","B","C","D"],
                ["Iteration 1:",
                round(channel_peak[0][0],3),round(channel_peak[0][1],3), round(channel_peak[0][2],3),round(channel_peak[0][3],3)],
                ["Iteration 2:",
                round(channel_peak[1][0],3),round(channel_peak[1][1],3), round(channel_peak[1][2],3),round(channel_peak[1][3],3)],
                ["Iteration 3:",
                round(channel_peak[2][0],3),round(channel_peak[2][1],3), round(channel_peak[2][2],3),round(channel_peak[2][3],3)],
                ["Passband Flatness Pass",
                passband_flat[0],passband_flat[1],passband_flat[2],passband_flat[3]]]

    title = "Passband Flatness Test"
    report.buffer_put("text_large", title)
    report.buffer_put("table_wide", test_info, "")
    report.buffer_put("text", " ")
    report.buffer_put("image_quad", images, "")
    report.buffer_put("pagebreak")

def build_report():
    report.insert_title_page("UHD Passband Flatness Test")
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
