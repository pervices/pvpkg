from common import sigproc
from common import engine
from common import generator as gen
from retrying import retry
import numpy as np
import matplotlib.pyplot as plt
import sys

def test(it):

    gen.dump(it)

    # Collect.
    tx_stack = [ (10.0, it["sample_count" ]) ] # One seconds worth.
    rx_stack = [ (10.0, it["sample_count"]) ]
    vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
    error_detected = 0
    # Process.
    reals = []
    imags = []
    for ch, channel in enumerate(vsnk):

        real = [datum.real for datum in channel.data()]
        imag = [datum.imag for datum in channel.data()]
        #print('the value of the real array is', real)
        #print('the value of the imag array is', imag)

        reals.append(real)
        imags.append(imag)

        time=np.arange(0,len(real)/it["sample_rate"], 1/it["sample_rate"])
        plt.figure()
        plt.title("Time plot of {} for wave_freq = {} Hz".format(ch,it["wave_freq"]))
        plt.xlabel("time")
        plt.ylabel("Amplitude")
        plt.plot(time[0:500], real[0:500], color='red', label='real')
        plt.plot(time[0:500], reals[0][0:500], color='blue', label='reals')
        plt.plot(time[0:500], imag[0:500], color='green', label='imag')
        plt.plot(time[0:500], imags[0][0:500], color='orange', label='imags')
        plt.legend()
        plt.savefig(fname='Time plot for channel {} at wave_freq {}'.format(ch, it["wave_freq"],format='png'))
        sys.exit(1)

def main(iterations):

    for it in iterations:
        test(it)

main(gen.hi_band_tx_ph_coherency())
