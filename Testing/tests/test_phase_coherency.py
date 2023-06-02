from common import sigproc
from common import engine
from common import generator as gen
from retrying import retry
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import sys
def fit_func(xdata, A, lag_abs):
    fit_y = A*np.exp((2*np.pi)+lag_abs)
    return fit_y
def main(iterations):
    for it in iterations:
        gen.dump(it)
        # Collect.
        tx_stack = [ (10, it["sample_count" ]) ] # One seconds worth.
        rx_stack = [ (10.5, it["sample_count"]) ]
        vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
        error_detected = 0

        for ch, channel in enumerate(vsnk):

            real = [datum.real for datum in channel.data()]
            imag = [datum.imag for datum in channel.data()]


            lag = sigproc.lag(real, imag, it["sample_rate"], it["wave_freq"])
            lag_abs = abs(lag)

            print("channel %2d: lag %f" % (ch, lag))
            #print('the value of the real array is', real)
            #print('the value of the imag array is', imag)
            #for b in it["channels"]:fig, axs = plt.subplots(2, 2)
            #print('it is',it["name"])
            time=np.arange(0,len(real)/it["sample_rate"], 1/it["sample_rate"])
            xdata = np.asarray(time)
            rdata = np.asarray(real)
            idata = np.asarray(imag)
            f_data = idata*1j + real
            #size = len(f_data)
            #size_t = len(xdata)
            #print("fdata xdata",size,size_t)
            fit_data = fit_func(xdata, f_data, lag_abs)
            p_opt,p_cov = curve_fit(fit_func, xdata, fit_data)
            y_data = fit_func(xdata, *p_opt)
            plt.plot(xdata, f_data, 'o')
            plt.plot(xdata, y_data, '-', label='fit',color='red')
            plt.savefig(fname='fitplot for time amp')

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
