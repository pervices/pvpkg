from gnuradio import uhd
from common import sigproc
from common import engine
from common import generator as gen
from common import pdf_report
from common import test_args
from common import log
import numpy as np
import math
import matplotlib.pyplot as plt
import sys

#Setup argument parsing
targs = test_args.TestArgs(testDesc="Passband Flatness Test")

report = pdf_report.ClassicShipTestReport("passband_flatness_test", targs.serial, targs.report_dir, targs.docker_sha)
test_fail = 0
channel_peak = []
plot_points_xf = []
plot_points_yf = []
images = []
test_summary = []

def test(it, data):
    global test_fail
    gen.dump(it)
    reals = []
    imags = []
    largest_peak = []
    yfp = []

    tx_stack = [ (10.0, it["sample_count"]) ] # One seconds worth.
    rx_stack = [ (10.0, it["sample_count"]) ]
    vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
    error_detected = 0

    if it["wave_freq"] not in test_summary:
        test_summary.append(it["wave_freq"])

    # Process.
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
        # Check any of the peaks are the expected wave wave
        # Unlike tx, the rx lo will end up at 0Hz after mixing and therefore not be visible

        # Convert the yf values from magnitude to dB
        largest_peak.append(20*np.log10(np.max(yf[peaks])))
        converted_yf = [20*np.log10(yf_points) for yf_points in yf]
        yfp.append(converted_yf)

    plot_points_xf.append(xf)
    plot_points_yf.append(yfp)
    channel_peak.append(largest_peak)
    return data

def main(iterations, desc):
    data  = [["Center Freq", "Wave Freq", "Channel", "Result"]]

    for it in iterations:
        test(it, data)

    global test_fail
    passband_flat = []
    test_info_channel_diff = []

    for ch in list(range(4)):
        channel_test = []

        plt.figure()
        plt.title("Channel {} Rx FFT".format(ch), fontsize=14)
        plt.xlabel("Frequency (Hz)", fontsize=12)
        plt.ylabel("Magnitude", fontsize=12)

        # Loop through array to plot all iterations per channel on one graph
        for it in list(range(len(plot_points_xf))):
            channel_test.append(channel_peak[it][ch])
            plt.plot(plot_points_xf[it], plot_points_yf[it][ch])

        s = report.get_image_io_stream()
        plt.savefig(s, format='png')
        plt.close()
        img = report.get_image_from_io_stream(s)
        images.append(img)

        # Get difference of max peak and min peak to check if passband is flat
        channel_max = np.max(channel_test)
        channel_min = np.min(channel_test)
        channel_diff = np.abs(channel_max-channel_min)
        test_info_channel_diff.append(round(channel_diff,3))

        if np.abs(channel_diff) <= 4 :
            passband_flat.append("Pass")
        else:
            log.pvpkg_log_info("PASSBAND_FLATNESS", "Channel {} failed passband test with a difference of {}".format(ch, channel_diff))
            test_fail = 10 + int(ch) #Set fail value to 10 + the channel that fails for easy debugging of error code
            passband_flat.append("Fail")

    test_info = [["Channel Peak Information (dB):","A","B","C","D", "Wave Frequency (Hz)"]]

    # Iterate through the channel peak array to create a summary chart
    for it in list(range(len(plot_points_xf))):
        test_info.append(["Iteration {}:".format(it),
                round(channel_peak[it][0],3),round(channel_peak[it][1],3),round(channel_peak[it][2],3),round(channel_peak[it][3],3), test_summary[it]])

    test_info.append(["Channel High Low Difference",test_info_channel_diff[0],test_info_channel_diff[1],test_info_channel_diff[2],test_info_channel_diff[3], "N/A"])
    test_info.append(["Passband Flatness Pass",passband_flat[0],passband_flat[1],passband_flat[2],passband_flat[3], "N/A"])

    title = "Passband Flatness Test : {}".format(desc)
    report.buffer_put("text_large", title)
    report.buffer_put("text", " ")
    report.buffer_put("image_quad", images, "")
    report.buffer_put("pagebreak")
    report.buffer_put("table_wide", test_info, "")
    report.buffer_put("pagebreak")


def build_report():
    report.insert_title_page("UHD Passband Flatness Test")
    report.draw_from_buffer()
    report.save()
    log.pvpkg_log_info("PASSBAND_FLATNESS", "PDF report saved at " + report.get_filename())


## SCRIPT LOGIC ##
if(targs.product == "Vaunt"):
    main(gen.lo_band_passband_flatness_test(), "Low Band")
elif(targs.product == "Tate"):
    main(gen.cyan.lo_band.passband_flatness_test(), "Low Band")
elif(targs.product == "Lily"):
    main(gen.chestnut.lo_band.passband_flatness_test(), "Low Band")
else:
    log.pvpkg_log_info("PASSBAND_FLATNESS", "Unrecognized product argument")
    test_fail = 1

build_report()
sys.exit(test_fail)
