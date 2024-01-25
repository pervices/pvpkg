from common import sigproc
from common import engine
from common import generator as gen
from common import pdf_report
import matplotlib.pyplot as plt
import numpy as np
import sys

def main(iterations, title="Crimson TX RX Gain Test") -> :

    # Collect.
    vsnks = []

    sample_count = 0

    fail_flag = 0

    for it in iterations:
        gen.dump(it)
        sample_count = it["sample_count"]
        tx_stack = [ (10.0, int(it["sample_count" ])) ]
        rx_stack = [ (10.0, int(it["sample_count"])) ]
        vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
        vsnks.append(vsnk)
        # print("new iteration")
        # print(len(vsnks))

        iteration_areas = []
        current_vsnk_i = 0
        for vsnk in vsnks:
            channel_areas = []
            current_vsnk_i += 1
            # print("vsnk")
            for ch, channel in enumerate(vsnk):
                # print("channel")
                real = [datum.real for datum in channel.data()]
                imag = [datum.imag for datum in channel.data()]
                #print('the value of the real array is', real)
                #print('the value of the imag array is', imag)

                ## Calculate absolute area.
                area = sigproc.absolute_area(real)
                channel_areas.append(area)


            iteration_areas.append(channel_areas)
            #areas = np.array(areas).T.tolist() # Transpose.
            print("the areas of channel 0-3 for gain [5,10,20] are:", iteration_areas)
            # Assert area is increasing per channel.
            desc = "Gain plot of channel {} for wave_freq = {} Hz at Tx gain {} and Rx gain {} : ".format(it["channels"], it["wave_freq"], it["tx_gain"], it["rx_gain"])
            images = []
            data = [["Center Frequency (Hz)", "Wave Frequency (Hz)", "Sample Rate (SPS)", "Sample Count", "TX Gain (dB)", "RX Gain (dB)"],
                        [it["center_freq"], it["wave_freq"], it["sample_rate"], it["sample_count"], it["tx_gain"], it["rx_gain"]]]
            
            
            for a in range(len(iteration_areas[0])):
                #print(area)
                for b in range(len(iteration_areas)-1):
                    # test for area
                    try:
                        # make sure the difference in area is significant
                        assert iteration_areas[b+1][a] - iteration_areas[b][a] > 1 
                    except:
                        fail_flag = 1
            
        
                #plot and save real component
                plt.figure()
                plt.title("Gain plot of ch{} for wave_freq = {} Hz".format(a,it["wave_freq"]))
                plt.xlabel("Sample")
                plt.ylabel("Amplitude")
                plt.plot(imag[0:300], label='reals')
                plt.plot(real[0:300], label='imags')
                plt.legend()

                s = report.get_image_io_stream()
                plt.savefig(s, format='png')
                plt.close()     # remember to close or you'll use up all the memory 
                img = report.get_image_from_io_stream(s)
                images.append(img)
                # plt.savefig(fname='Gain plot for channel {} at wave_freq {} at Tx gain {}'.format(ch, it["wave_freq"],it["tx_gain"],format='png'))
                # report.insert_image_from_io_stream(s, "Gain plot of channel {} for wave_freq = {} Hz at Tx gain {} and Rx gain {} : ".format(a,it["wave_freq"], it["tx_gain"], it["rx_gain"]))
                print("image inserted for Gain plot of {} for wave_freq = {} Hz at Tx gain {}".format(a,it["wave_freq"], it["tx_gain"]))

            if (current_vsnk_i == (len(vsnks) - 1) or len(vsnks) == 1):
                # dont draw unnecessary stuff
                report.insert_text_large(title)
                report.insert_table(data)
                report.insert_text(" ")
                report.insert_image_quad_grid(images, desc)
                report.new_page()

    # report.save()
    if (fail_flag == 1):
        return 1    # fail
        # sys.exit(1)
    else: 
        return 0

def to_pass_fail(input) -> str:
    if (input == 0):
        return "Pass"
    else:
        return "Fail"

if __name__ == "__main__":

    global report
    report = pdf_report.ClassicShipTestReport("tx_rx_gain")
    report.insert_title_page("Crimson TX RX Gain Test")

    test_status = [["Test", "Status"]]

    # Change the argument in the following function to select how many channels to test
    ret = main(gen.lo_band_gain_tx(4), "Low Band TX Gain Test")
    test_status.append(["Low Band TX Gain Test", to_pass_fail(ret)])
    #ret = main(gen.lo_band_gain_rx(4), "Low Band RX Gain Test")
    test_status.append(["Low Band RX Gain Test", to_pass_fail(ret)])
    #ret = main(gen.hi_band_gain_tx(4), "High Band TX Gain Test")
    test_status.append(["High Band TX Gain Test", to_pass_fail(ret)])
    #ret = main(gen.hi_band_gain_rx(4), "High Band RX Gain Test")
    test_status.append(["High Band RX Gain Test", to_pass_fail(ret)])

    report.insert_table(test_status)
    report.save()
