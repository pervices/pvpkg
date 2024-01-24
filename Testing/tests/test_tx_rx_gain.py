from common import sigproc
from common import engine
from common import generator as gen
from common import pdf_report
import matplotlib.pyplot as plt
import numpy as np
import sys

def main(iterations):

    # Collect.
    vsnks = []

    sample_count = 0

    report = pdf_report.ClassicShipTestReport("tx_rx_gain")
    report.insert_title_page("Crimson TX RX Gain Test")

    for it in iterations:
        gen.dump(it)
        sample_count = it["sample_count"]
        tx_stack = [ (10.0, int(it["sample_count" ])) ]
        rx_stack = [ (10.0, int(it["sample_count"])) ]
        vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
        vsnks.append(vsnk)
        #print("a")
        #print(len(vsnks))

        iteration_areas = []
        for vsnk in vsnks:
            channel_areas = []
            for ch, channel in enumerate(vsnk):

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
            for a in range(len(iteration_areas[0])):
                #print(area)
                for b in range(len(iteration_areas)-1):
                    #plot and save real component
                    plt.figure()
                    plt.title("Gain plot of {} for wave_freq = {} Hz".format(ch,it["wave_freq"]))
                    plt.xlabel("Sample")
                    plt.ylabel("Amplitude")
                    plt.plot(imag[0:300], label='reals')
                    plt.plot(real[0:300], label='imags')
                    plt.legend()

                    data = [["Center Frequency (Hz)", "Wave Frequency (Hz)", "Sample Rate (SPS)", "Sample Count", "TX Gain (dB)", "RX Gain (dB)"],
                            [it["center_freq"], it["wave_freq"], it["sample_rate"], it["sample_count"], it["tx_gain"], it["rx_gain"]]]
                    report.insert_table(data)
                    s = report.get_image_io_stream()
                    plt.savefig(s, format='png')
                    # plt.savefig(fname='Gain plot for channel {} at wave_freq {} at Tx gain {}'.format(ch, it["wave_freq"],it["tx_gain"],format='png'))
                    report.insert_image_from_io_stream(s, "Gain plot of channel {} for wave_freq = {} Hz at Tx gain {} and Rx gain {} : ".format(a,it["wave_freq"], it["tx_gain"], it["rx_gain"]))
                    print("image inserted for Gain plot of {} for wave_freq = {} Hz at Tx gain {}".format(a,it["wave_freq"], it["tx_gain"]))

                    try:
                        assert iteration_areas[b+1][a] - iteration_areas[b][a] > 1 #makes sure the difference in area is significant
                    except:
                        print("insignificant difference in area")
                        report.insert_text("The above test failed, insignificant difference in area")
                        # report.save()
                        # sys.exit(1)
    report.save()


#Change the argument in the following function to select how many channels to test
main(gen.lo_band_gain_tx(4))
# main(gen.lo_band_gain_rx(4))
# main(gen.hi_band_gain_tx(4))
# main(gen.hi_band_gain_rx(4))
