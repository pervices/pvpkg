import os
from common import sigproc
from common import engine
from common import generator as gen
from retrying import retry
import numpy as np
import matplotlib.pyplot as plt
import sys

@retry(stop_max_attempt_number = 1)
def test(it):
    gen.dump(it)


    tx_stack = [ (10.0, it["sample_count"]) ] # One seconds worth.
    rx_stack = [ (10.0, int(it["sample_count"]) ) ]
    vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)

    for ch, channel in enumerate(vsnk):
        real = [datum.real for datum in channel.data()]
        imag = [datum.imag for datum in channel.data()]
        #print(len(real))
        #print(len(imag))

        fund_real = sigproc.fundamental(real, it["sample_rate"])
        fund_imag = sigproc.fundamental(imag, it["sample_rate"])

        like_real = (float(it["wave_freq"]) / fund_real)
        like_imag = (float(it["wave_freq"]) / fund_imag)

        print("channel %2d: real %10.0f Hz (%8.5f) :: imag %10.0f Hz (%8.5f)" % (ch, fund_real, like_real, fund_imag, like_imag))

        sigproc.dump_file(vsnk, it["wave_freq"])


        try:
            assert (like_real > 0.95 and like_real < 1.05 and like_imag > 0.95 and like_imag < 1.05), "like_real and like_imag do not meet requirements, fail"
        except:
            sigproc.dump(vsnk)
            raise
            #plot and save real/imag component vs. sample
            plt.figure()
            plt.title("Fundamental frequency sample plot of {} for wave_freq = {} Hz".format(ch,it["wave_freq"]))
            plt.xlabel("Sample")
            plt.ylabel("Amplitude")
            plt.plot(real[0:300], label='real')
            plt.plot(imag[0:300],label='imag')
            plt.legend()
            plt.savefig(fname='Fundamental frequency sample plot for channel {} at wave_freq {}'.format(ch, it["wave_freq"],format='png'))

            time=np.arange(0,len(real)/it["sample_rate"], 1/it["sample_rate"])
            #plot and save real/imag component vs. time
            plt.figure()
            plt.title("Fundamental frequency time plot of {} for wave_freq = {} Hz".format(ch,it["wave_freq"]))
            plt.xlabel("time")
            plt.ylabel("Amplitude")
            plt.plot(time, real, label='real')
            plt.plot(time, imag, label='imag')
            plt.legend()
            plt.savefig(fname='Fundamental frequency time plot for channel {} at wave_freq {}'.format(ch, it["wave_freq"],format='png'))
            sys.exit(1)

def main(iterations):

    for it in iterations:
        test(it)

main(gen.lo_band_wave_sweep())
main(gen.hi_band_wave_sweep())
