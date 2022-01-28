from common import sigproc
from common import engine
from common import generator as gen
from retrying import retry
import numpy as np
import matplotlib.pyplot as plt
import sys


@retry(stop_max_attempt_number = 3)
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
        #print('the value of reals[0] is', reals[0])
        #print('the value of imags[0] is', imags[0])

        real_coherency = sigproc.lag(real, reals[0], it["sample_rate"], it["wave_freq"])
        imag_coherency = sigproc.lag(imag, imags[0], it["sample_rate"], it["wave_freq"])

        print("channel %2d: real coherency %f" % (ch, real_coherency))
        print("channel %2d: imag coherency %f" % (ch, imag_coherency))

        sigproc.dump_file(vsnk, it["wave_freq"])
        thresh = 0.15
        try:
            assert real_coherency > -thresh and real_coherency < thresh and \
                    imag_coherency > -thresh and imag_coherency < thresh
        except:
            print('threshold not satisfied for channel {} at wave_freq = {}'.format(it["channels"], it["wave_freq"]))
            #plot and save real component
            plt.figure()
            plt.title("Real sample data plot of {} for wave_freq = {} Hz".format(it["channels"],it["wave_freq"]))
            plt.xlabel("Sample")
            plt.ylabel("Amplitude")
            plt.plot(real[0:500], color='black',label='real')
            plt.plot(reals[0][0:500],color='purple',label='reals[0]')
            plt.legend()
            plt.savefig(fname='Real lag plot for channel {} at wave_freq {}'.format(ch, it["wave_freq"],format='png'))

            #plot and save imag component
            plt.figure()
            plt.title("Imag Sample Data plot of {} for wave_freq = {} Hz".format(it["channels"],it["wave_freq"]))
            plt.xlabel("Sample")
            plt.ylabel("Amplitude")
            plt.plot(imag[0:500], color='green', label='imag')
            plt.plot(imags[0][0:500], color='orange', label='imags[0]')
            plt.legend()
            plt.savefig(fname='Imag lag plot for channel {} at wave_freq {}'.format(it["channels"], it["wave_freq"],format='png'))

            time=np.arange(0,len(real)/it["sample_rate"], 1/it["sample_rate"])
            #print(len(len(real)/it["sample_rate"]))
            #plot and save real/imag component vs. time
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

main(gen.lo_band_wave_sweep())
main(gen.hi_band_wave_sweep())

