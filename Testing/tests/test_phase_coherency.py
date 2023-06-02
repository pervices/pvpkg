from common import sigproc
from common import engine
from common import generator as gen
from retrying import retry
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import sys

def fit_func(xdata, A, f_wave, abs_phase):
    fit_y = A*np.sin(2*np.pi*f_wave*xdata+abs_phase)
    return fit_y

def main(iterations):
    for it in iterations:
        gen.dump(it)
        # Collect.
        tx_stack = [ (10, it["sample_rate" ]) ] # One seconds worth.
        rx_stack = [ (10.5, it["sample_count"]) ]
        vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
        error_detected = 0
        for ch, channel in enumerate(vsnk):

            real = [datum.real for datum in channel.data()]
            imag = [datum.imag for datum in channel.data()]

            #w_freq = abs(it["wave_freq"])
            print("channel %2d: lag %f" % (ch, lag))
            time=np.arange(0,len(real)/it["sample_rate"], 1/it["sample_rate"])
            xdata = np.asarray(time)
            rdata = np.asarray(real)*np.sin(2*np.pi*wave_freq*xdata)
            idata = rdata * 0

            rdata_max = max(rdata) #Provides us with the max value.
            rdata_norm = rdata * (1/rdata_max) #Normalizes nominal amplitude to 1
            plt.plot(xdata, rdata_norm, 'o')
            plt.savefig(fname='dataplot-for-time-amp')

            guess_opt=[1, sample_rate, 1]
            p_opt,p_cov = curve_fit(fit_func, xdata, rdata_norm, p0=guess_opt)
            A=p_opt[0]
            f_wave=p_opt[1]
            abs_phase=p_opt[2]
            fit_data = fit_func(xdata, A, f_wave, abs_phase)

            plt.plot(xdata, fit_data, '-')
            plt.savefig(fname='fitplot-for-time-amp')

            plt.figure()
            plt.title("Time plot of {} for wave_freq = {} Hz".format(ch,it["wave_freq"]))
            plt.xlabel("time")
            plt.ylabel("Amplitude")
            plt.plot(time[0:500], real[0:500], color='red', label='real')
            plt.plot(time[0:500], imag[0:500], color='green', label='imag')
            plt.legend()
            plt.savefig(fname='timeplot-{}-channel{}-wavefreq-{}'.format(ch,it["wave_freq"],it["name"],format='png'))

            #xdata = np.asarray(time)

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

#def fit_func(idata,rdata, xdata, w_freq, lag):
    #fit_y = (idata * np.cos((2*np.pi*w_freq*xdata)+lag))+(1j * (idata * np.cos((2*np.pi*w_freq*xdata)+lag)))
    #return fit_y

main(gen.lo_band_tx_ph_coherency(4))
main(gen.lo_band_rx_ph_coherency(4))
