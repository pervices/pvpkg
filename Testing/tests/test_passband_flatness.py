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
test_info = [["Channel Peak Information (dB):", "Wave Frequency (Hz)"]]
iteration_num = 0
channel_map = np.array(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])
# All iterations should have same number of channels so declare here so test() and main() can both access it
channels = []

def test(it):
    global test_fail
    global iteration_num
    global channels
    gen.dump(it)
    largest_peak = []
    yfp = []

    # Since this test formats the report table to include each channel as a column header instead of a row and
    # overlays each iteration for a channel on the same graph, every iteration should have the same number of channels.
    # Since the number of channels may be specified in the generator, we must check it here instead of in main(), so
    # assume the channels for the first iteration is the same as the rest.
    if iteration_num == 0:
        # If the channels argument was set, it will override the channels specified in the generator.
        # If neither the channels arg or the generator specified the channels, fallback to four channels.
        if targs.channels != None:
            channels = targs.channels
        elif "channels" in it:
            channels = it["channels"]
        else:
            channels = [0,1,2,3]

        # Insert channel column headers for the report
        channel_names = channel_map[targs.channels].tolist()
        for ch in reversed(channel_names):
            test_info[0].insert(1, ch)

    tx_stack = [ (10.0, it["sample_count"]) ] # One seconds worth.
    rx_stack = [ (10.0, it["sample_count"]) ]
    try:
        vsnk = engine.run(channels, it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
    except Exception as err:
        # Test will be marked as failed with DNF for missing data but still continue to next iterations.
        log.pvpkg_log_error("PASSBAND_FLATNESS", 
            "Exception occured while streaming.\nIteration {}\nException: {}\nTest will continue but be marked as failed with DNF for missing data."
            .format(str(it), str(err)))
        test_fail = 1
        test_info.append(["Iteration {}:".format(iteration_num)] + ["DNF" for _ in channels] + [it["wave_freq"]])
        return

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
    test_info.append(["Iteration {}:".format(iteration_num)] + [round(peak, 3) for peak in largest_peak] + [it["wave_freq"]])

def main(iterations, desc):
    global iteration_num
    global test_fail
    passband_flat = []
    test_info_channel_diff = []

    for it in iterations:
        test(it)
        iteration_num += 1

    # Check the data for passband flatness. This only checks iterations that finished, so does not consider any marked as DNF.
    for ch, channel in enumerate(channels):
        channel_test = []

        plt.figure()
        plt.title("Channel {} Rx FFT".format(channel), fontsize=14)
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
            log.pvpkg_log_error("PASSBAND_FLATNESS", "Channel {} failed passband test with a difference of {}".format(ch, channel_diff))
            test_fail = 10 + int(ch) #Set fail value to 10 + the channel that fails for easy debugging of error code
            passband_flat.append("Fail")

    test_info.append(["Channel High Low Difference"] + [diff for diff in test_info_channel_diff] + ["N/A"])
    test_info.append(["Passband Flatness Pass"] + [flat for flat in passband_flat] + ["N/A"])

    title = "Passband Flatness Test : {}".format(desc)
    report.buffer_put("text_large", title)
    report.buffer_put("text", " ")
    report.buffer_put("image_list_dynamic", images, "")
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
elif(targs.product == "Avery"):
    main(gen.calamine.lo_band.passband_flatness_test(), "Low Band")
elif(targs.product == "Tate"):
    main(gen.cyan.lo_band.passband_flatness_test(), "Low Band")
elif(targs.product == "Lily"):
    main(gen.chestnut.lo_band.passband_flatness_test(), "Low Band")
else:
    log.pvpkg_log_error("PASSBAND_FLATNESS", "Unrecognized product argument")
    test_fail = 1

build_report()
sys.exit(test_fail)
