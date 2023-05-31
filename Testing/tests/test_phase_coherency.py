from common import sigproc
from common import engine
from common import generator as gen
from retrying import retry
import numpy as np
import matplotlib.pyplot as plt
import sys

def main(iterations):
    for it in iterations:
        gen.dump(it)
        # Collect.
        tx_stack = [ (10.5, it["sample_count" ]) ] # One seconds worth.
        rx_stack = [ (10.5, it["sample_count"]) ]
        vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
        error_detected = 0
        # Process.

        for ch, channel in enumerate(vsnk):

            real = [datum.real for datum in channel.data()]
            imag = [datum.imag for datum in channel.data()]

            lag = sigproc.lag(real, imag, it["sample_rate"], it["wave_freq"])
            print("channel %2d: lag %f" % (ch, lag))
            #print('the value of the real array is', real)
            #print('the value of the imag array is', imag)
            #for b in it["channels"]:fig, axs = plt.subplots(2, 2)
            #print('it is',it["name"])
            time=np.arange(0,len(real)/it["sample_rate"], 1/it["sample_rate"])
            plt.figure()
            plt.title("Time plot of {} for wave_freq = {} Hz".format(ch,it["wave_freq"]))
            plt.xlabel("time")
            plt.ylabel("Amplitude")
            plt.plot(time[0:500], real[0:500], color='red', label='real')
            plt.plot(time[0:500], imag[0:500], color='green', label='imag')
            plt.legend()
            plt.savefig(fname='timeplot-{}-channel{}-wavefreq-{}'.format(ch,it["wave_freq"],it["name"],format='png'))
            fig = plt.figure()


        for i, channel in enumerate(vsnk):
            ax = fig.add_subplot(2, 2, i+1)
            ax.set_title("Time plot of {} for wave_freq = {} Hz".format(i,it["wave_freq"]),fontsize = 10)
            plt.xlabel("time")
            plt.ylabel("Amplitude")
            ax.plot(time[0:500], real[0:500], color='red', label='real')
            ax.plot(time[0:500], imag[0:500], color='green', label='imag')
            plt.tight_layout()
            plt.savefig(fname='timeplot-all-channel{}-wavefreq-{}'.format(it["wave_freq"],it["name"],format='png'))
            #sys.exit(1)


main(gen.lo_band_tx_ph_coherency(4))
main(gen.lo_band_rx_ph_coherency(4))
