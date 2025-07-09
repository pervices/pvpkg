from common import sigproc
from common import engine
from common import generator as gen
from common import pdf_report
from common import test_args
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def main(iterations, title="TX RX Gain Test") -> int:
    fail_flag = 0

    iteration_areas = []

    for it in iterations:
        gen.dump(it)
        sample_count = it["sample_count"]
        tx_stack = [ (5.0, int(it["sample_count" ])) ]
        rx_stack = [ (5.0, int(it["sample_count"])) ]
        try:
            vsnk = engine.run(targs.channels, it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
        except Exception as err:
            print("\x1b[31m" + "ERROR while gathering data\nIteration: " + str(it) + "\nException: " + str(err) + "\x1b[0m")
            fail_flag = 1
            continue

        
        current_test_only_fail_flag = 0

        channel_areas = []
        images = []
        for ch, channel in enumerate(vsnk):
            real = [datum.real for datum in channel.data()]
            imag = [datum.imag for datum in channel.data()]

            # Discard the first 50 unstable samples
            real = real[50:]
            imag = imag[50:]

            ## Calculate absolute area.
            area = sigproc.absolute_area(real)
            channel_areas.append(area)

            #plot and save real component
            plt.figure()
            plt.title("Gain plot of ch{} for wave_freq = {} Hz".format(targs.channels[ch],it["wave_freq"]))
            plt.xlabel("Sample")
            plt.ylabel("Amplitude")
            plt.plot(imag[0:300], label='reals')
            plt.plot(real[0:300], label='imags')
            plt.legend()

            s = report.get_image_io_stream()
            plt.savefig(s, format='png', dpi=200)
            plt.close()     # remember to close or you'll use up all the memory
            img = report.get_image_from_io_stream(s)
            images.append(img)


        iteration_areas.append(channel_areas)
        print("the areas of {} for gain are: {}".format(targs.channels, iteration_areas))
        # Assert area is increasing per channel.
        desc = "Gain plot of channels {} for wave_freq = {} Hz at Tx gain {} and Rx gain {} : ".format(targs.channels, it["wave_freq"], it["tx_gain"], it["rx_gain"])
        data = [["Center Frequency (Hz)", "Wave Frequency (Hz)", "Sample Rate (SPS)", "Sample Count", "TX Gain (dB)", "RX Gain (dB)"],
                        [it["center_freq"], it["wave_freq"], it["sample_rate"], it["sample_count"], it["tx_gain"], it["rx_gain"]]]

        report.buffer_put("pagebreak")
        report.buffer_put("text_large", title)
        report.buffer_put("table_wide", data, "Test Configuration")
        report.buffer_put("text", " ")
        report.buffer_put("image_list_dynamic", images, desc)
        if (current_test_only_fail_flag == 1):
            report.buffer_put("text_large", "This test has failed")
            current_test_only_fail_flag = 0

    for a in range(len(iteration_areas[0])):
        for b in range(len(iteration_areas)-1):
            # test for area
            try:
                # make sure the difference in area is significant
                assert iteration_areas[b+1][a] - iteration_areas[b][a] > 1
            except:
                print(sys.argv[0] + " unacceptable variation in gain")
                fail_flag = 1
                current_test_only_fail_flag = 1

    if (fail_flag == 1):
        return 1    # fail
    else:
        return 0

def to_pass_fail(input) -> str:
    if (input == 0):
        return "Pass"
    else:
        return "Fail"

if __name__ == "__main__":
    targs = test_args.TestArgs(testDesc="Tx Rx Gain Test")

    global report

    report = pdf_report.ClassicShipTestReport("tx_rx_gain", targs.serial, targs.report_dir, targs.docker_sha)

    if(targs.product == 'Tate'):
        report.insert_title_page("Cyan TX RX Gain Test")

        test_status = [["Test", "Status"]]

        # Change the argument in the following function to select how many channels to test
        ret = main(gen.cyan.lo_band.gain_tx(), "Low Band TX Gain Test")
        test_status.append(["Low Band TX Gain Test", to_pass_fail(ret)])

        ret = main(gen.cyan.lo_band.gain_rx(), "Low Band RX Gain Test")
        test_status.append(["Low Band RX Gain Test", to_pass_fail(ret)])

        ret = main(gen.cyan.mid_band.gain_tx(), "Mid Band TX Gain Test")
        test_status.append(["Mid Band TX Gain Test", to_pass_fail(ret)])

        ret = main(gen.cyan.mid_band.gain_rx(), "Mid Band RX Gain Test")
        test_status.append(["Mid Band RX Gain Test", to_pass_fail(ret)])

        ret = main(gen.cyan.hi_band.gain_tx(), "High Band TX Gain Test")
        test_status.append(["High Band TX Gain Test", to_pass_fail(ret)])

        ret = main(gen.cyan.hi_band.gain_rx(), "High Band RX Gain Test")
        test_status.append(["High Band RX Gain Test", to_pass_fail(ret)])
    elif(targs.product == 'Lily'):
        report.insert_title_page("Chestnut TX RX Gain Test")

        test_status = [["Test", "Status"]]

        # Change the argument in the following function to select how many channels to test
        ret = main(gen.chestnut.lo_band.gain_tx(), "Low Band TX Gain Test")
        test_status.append(["Low Band TX Gain Test", to_pass_fail(ret)])

        ret = main(gen.chestnut.lo_band.gain_rx(), "Low Band RX Gain Test")
        test_status.append(["Low Band RX Gain Test", to_pass_fail(ret)])

        ret = main(gen.chestnut.mid_band.gain_tx(), "Mid Band TX Gain Test")
        test_status.append(["Mid Band TX Gain Test", to_pass_fail(ret)])

        ret = main(gen.chestnut.mid_band.gain_rx(), "Mid Band RX Gain Test")
        test_status.append(["Mid Band RX Gain Test", to_pass_fail(ret)])

        ret = main(gen.chestnut.hi_band.gain_tx(), "High Band TX Gain Test")
        test_status.append(["High Band TX Gain Test", to_pass_fail(ret)])

        ret = main(gen.chestnut.hi_band.gain_rx(), "High Band RX Gain Test")
        test_status.append(["High Band RX Gain Test", to_pass_fail(ret)])
    elif(targs.product == 'Vaunt'):
        report.insert_title_page("Crimson TX RX Gain Test")

        test_status = [["Test", "Status"]]

        # Change the argument in the following function to select how many channels to test
        ret = main(gen.lo_band_gain_tx(), "Low Band TX Gain Test")
        test_status.append(["Low Band TX Gain Test", to_pass_fail(ret)])

        ret = main(gen.lo_band_gain_rx(), "Low Band RX Gain Test")
        test_status.append(["Low Band RX Gain Test", to_pass_fail(ret)])

        ret = main(gen.hi_band_gain_tx(), "High Band TX Gain Test")
        test_status.append(["High Band TX Gain Test", to_pass_fail(ret)])

        ret = main(gen.hi_band_gain_rx(), "High Band RX Gain Test")
        test_status.append(["High Band RX Gain Test", to_pass_fail(ret)])


    report.insert_text_large("Test Results")
    report.insert_table(test_status, 20)
    report.draw_from_buffer()
    report.save()
    print("PDF report saved at " + report.get_filename())

    for test in test_status:
        if "Fail" in test:
            sys.exit(1)
