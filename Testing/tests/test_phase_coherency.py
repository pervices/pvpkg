from common import sigproc
from common import engine
from common import generator as gen
from retrying import retry
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import sys

def fit_func(xdata, A, f_wave, abs_phase):
    #fit_y = A*np.exp((2*np.pi*f_wave*xdata)+abs_phase)
    fit_y = A*np.cos(2*np.pi*f_wave*xdata+abs_phase)
    return fit_y

def main(iterations):
    for it in iterations:
        gen.dump(it)
        # Collect.
        tx_stack = [ (10,     it["sample_rate" ]) ]     # One seconds worth.
        rx_stack = [ (10.5,   it["sample_count"]) ]     # Half a seconds worth.
        vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
        error_detected = 0
        # Process.
        # xdata = []
        # rdata = []
        # idata = []
        #fit_data = []
        #w_freq = np.asarray(it["wave frequency"])
        for ch, channel in enumerate(vsnk):

            real = [datum.real for datum in channel.data()]
            imag = [datum.imag for datum in channel.data()]

            time=np.arange(0,it["sample_count"]/it["sample_rate"], 1/it["sample_rate"])
            xdata = np.asarray(time)
            rdata = np.asarray(real)
            idata = np.asarray(imag)

            #real_data = idata*1j + real #Numpy curve fit doesn't handle complex numbers
            f_data = np.asarray(rdata)


            rdata_max = max(rdata)
            plt.plot(xdata, f_data, 'o')
            plt.savefig(fname='dataplot-for-time-amp')


            w_freq = it["wave_freq"]
            print(rdata_max)
            print(w_freq)
            guess_opt=[rdata_max, w_freq, 0.75]

            p_opt,p_cov = curve_fit(fit_func, xdata, f_data, p0=guess_opt)
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
