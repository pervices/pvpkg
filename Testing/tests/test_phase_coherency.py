from common import sigproc
from common import engine
from common import generator as gen
from retrying import retry
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import sys
import statistics
freq_array = []
run_array =[]
amp_array = []
phase_array = []
AB_f_data = []
AC_f_data = []
AD_f_data = []
AB_a_data = []
AC_a_data = []
AD_a_data = []
AB_p_data = []
AC_p_data = []
AD_p_data = []
def fit_func(xdata, A, f_wave, abs_phase):
    #fit_y = A*np.exp((2*np.pi*f_wave*xdata)+abs_phase)
    fit_y = A*np.cos(2*np.pi*f_wave*xdata+abs_phase)
    return fit_y
def table_freq(run_array,freq_array):

    print("FREQUENCY")
    print("{:^10}|{:^10}|{:^10}|{:^10}|".format("Runs", "AB", "AC", "AD"))
    print("---------------------------------------------------------\n")
    for run_val in range(len(run_array)):
        print("{:^10}|".format(run_val),end=" ")
        index_val = run_val*4
        #stop_val = start_val +3
        AB = np.subtract(freq_array[index_val+1], freq_array[index_val])
        np.array(AB_f_data.append(AB))
        AC = np.subtract(freq_array[index_val+2], freq_array[index_val])
        np.array(AC_f_data.append(AC))
        AD = np.subtract(freq_array[index_val+3], freq_array[index_val])
        np.array(AD_f_data.append(AD))
        print("{:^10.8f}|{:^10.8f}|{:^10.8f}|".format(AB,AC,AD))
        if(run_val == 1):
          print("{:^10}|{:^11.8f}|{:^11.8f}|{:^11.8f}|".format("Min diff",min(AB_f_data),min(AC_f_data),min(AD_f_data)))
          print("{:^10}|{:^11.8f}|{:^11.8f}|{:^11.8f}|".format("Max diff",max(AB_f_data),max(AC_f_data),max(AD_f_data)))
          print("{:^10}|{:^11.8f}|{:^11.8f}|{:^11.8f}|".format("Mean Value",np.mean(AB_f_data),np.mean(AC_f_data), np.mean(AD_f_data)))
          print("{:^10}|{:^11.8f}|{:^11.8f}|{:^11.8f}|".format("Std Dev",np.std(AB_f_data), np.std(AC_f_data), np.std(AD_f_data)))
def table_amp(run_array,amp_array):
        print("AMPLITUDE")
        print("{:^10}|{:^10}|{:^10}|{:^10}|".format("Runs", "AB", "AC", "AD"))
        print("---------------------------------------------------------\n")
        for run_val in range(len(run_array)):
            print("{:^10}|".format(run_val),end=" ")
            index_val = run_val*4
        #stop_val = start_val +3
            AB = np.subtract(amp_array[index_val+1], amp_array[index_val])
            np.array(AB_a_data.append(AB))
            AC = np.subtract(amp_array[index_val+2], amp_array[index_val])
            np.array(AC_a_data.append(AC))
            AD = np.subtract(amp_array[index_val+3], amp_array[index_val])
            np.array(AD_a_data.append(AD))
            print("{:^10.8f}|{:^10.8f}|{:^10.8f}|".format(AB,AC,AD))
            if(run_val == 1):
               print("{:^10}|{:^11.8f}|{:^11.8f}|{:^11.8f}|".format("Min diff",min(AB_a_data),min(AC_a_data),min(AD_a_data)))
               print("{:^10}|{:^11.8f}|{:^11.8f}|{:^11.8f}|".format("Max diff",max(AB_a_data),max(AC_a_data),max(AD_a_data)))
               print("{:^10}|{:^11.8f}|{:^11.8f}|{:^11.8f}|".format("Mean Value",np.mean(AB_a_data),np.mean(AC_a_data), np.mean(AD_a_data)))
               print("{:^10}|{:^11.8f}|{:^11.8f}|{:^11.8f}|".format("Std Dev",np.std(AB_a_data), np.std(AC_a_data), np.std(AD_a_data)))
def table_phase(run_array,phase_array):
        print("PHASE")
        print("{:^10}|{:^10}|{:^10}|{:^10}|".format("Runs", "AB", "AC", "AD"))
        print("---------------------------------------------------------\n")
        for run_val in range(len(run_array)):
            print("{:^10}|".format(run_val),end=" ")
            index_val = run_val*4
            #stop_val = start_val +3
            AB = np.subtract(phase_array[index_val+1], phase_array[index_val])
            np.array(AB_p_data.append(AB))
            AC = np.subtract(phase_array[index_val+2], phase_array[index_val])
            np.array(AC_p_data.append(AC))
            AD = np.subtract(phase_array[index_val+3], phase_array[index_val])
            np.array(AD_p_data.append(AD))
            print("{:^10.8f}|{:^10.8f}|{:^10.8f}|".format(AB,AC,AD))
            if(run_val == 1):
               print("{:^10}|{:^11.8f}|{:^11.8f}|{:^11.8f}|".format("Min diff",min(AB_p_data),min(AC_p_data),min(AD_p_data)))
               print("{:^10}|{:^11.8f}|{:^11.8f}|{:^11.8f}|".format("Max diff",max(AB_p_data),max(AC_p_data),max(AD_p_data)))
               print("{:^10}|{:^11.8f}|{:^11.8f}|{:^11.8f}|".format("Mean Value",np.mean(AB_p_data),np.mean(AC_p_data), np.mean(AD_p_data)))
               print("{:^10}|{:^11.8f}|{:^11.8f}|{:^11.8f}|".format("Std Dev",np.std(AB_p_data), np.std(AC_p_data), np.std(AD_p_data)))

def main(iterations):
    for it in iterations:
        if(runs == 0):
          gen.dump(it)
        # Collect.
        tx_stack = [ (10,     it["sample_rate" ]) ]     # One seconds worth.
        rx_stack = [ (10.5,   it["sample_count"]) ]     # Half a seconds worth.
        vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
        error_detected = 0
        heading_names = ["FREQUENCY","AMPLITUDE","PHASE"]

        run_array.append(runs)

        for ch, channel in enumerate(vsnk):

                     real = [datum.real for datum in channel.data()]
                     imag = [datum.imag for datum in channel.data()]
                     w_freq = it["wave_freq"]
                     time=np.arange(0,it["sample_count"]/it["sample_rate"], 1/it["sample_rate"])

                     xdata = np.asarray(time)
                     rdata = np.asarray(real)
                     idata = np.asarray(imag)

                #real_data = idata*1j + real #Numpy curve fit doesn't handle complex numbers
                     f_data = np.asarray(rdata)


                     rdata_max = max(rdata)
                     # plt.plot(xdata, rdata, 'o')
                     # plt.savefig(fname='dataplot-for-time-amp')
                     #plt.legend(["blue", "green"],fontsize="large",loc ="lower right")
                     guess_opt=[rdata_max, w_freq, 0.75]

                     p_opt,p_cov = curve_fit(fit_func, xdata, rdata, p0=guess_opt)
                     A=p_opt[0]
                     f_wave=p_opt[1]
                     abs_phase=p_opt[2]
                     if ch == 0:
                            np.array(freq_array.append(w_freq))
                            np.asarray(amp_array.append(max(real)))
                            np.asarray(phase_array.append(abs_phase))
                     elif ch == 1:
                            np.array(freq_array.append(w_freq))
                            np.asarray(amp_array.append(max(real)))
                            np.asarray(phase_array.append(abs_phase))
                     elif ch == 2:
                            np.array(freq_array.append(w_freq))
                            np.asarray(amp_array.append(max(real)))
                            np.asarray(phase_array.append(abs_phase))
                     else:
                            np.array(freq_array.append(w_freq))
                            np.asarray(amp_array.append(max(real)))
                            np.asarray(phase_array.append(abs_phase))

                     #table_phase(heading_names,run_array,ch0_p,ch1_p,ch2_p,ch3_p)
                     fit_data = fit_func(xdata, rdata_max, f_wave, abs_phase)
                     # plt.plot(xdata, fit_data, '-')
                     # plt.legend(["blue", "green"],fontsize="large",loc ="lower right")
                     # plt.savefig(fname='fitplot-for-time-amp for {}'.format(it["name"]))

                     # plt.figure()
                     # plt.title("Time plot of {} for wave_freq = {} Hz".format(ch,it["wave_freq"]))
                     # plt.xlabel("time")
                     # plt.ylabel("Amplitude")
                     # plt.plot(time[0:500], real[0:500], color='red', label='real')
                     # plt.plot(time[0:500], imag[0:500], color='green', label='imag')
                     # plt.legend(["blue", "green"],fontsize="large",loc ="lower right")
                     # plt.savefig(fname='timeplot-{}-channel{}-wavefreq-{}'.format(ch,it["wave_freq"],it["name"],format='png'))


    #table_amp(heading_names,run_array,ch0_a,ch1_a,ch2_a,ch3_a)


        # for i, channel in enumerate(vsnk):
        #     fig = plt.figure()
        #     ax = fig.add_subplot(2, 2, i+1)
        #     ax.set_title("Time plot of {} for wave_freq = {} Hz".format(i,it["wave_freq"]),fontsize = 10)
        #     plt.xlabel("time")
        #     plt.ylabel("Amplitude")
        #     ax.plot(time[0:500], real[0:500], color='red', label='real')
        #     ax.plot(time[0:500], imag[0:500], color='green', label='imag')
        #     plt.tight_layout()
        #     plt.savefig(fname='timeplot-all-channel{}-wavefreq-{}'.format(it["wave_freq"],it["name"],format='png'))
            #sys.exit(1)



#def fit_func(idata,rdata, xdata, w_freq, lag):
    #fit_y = (idata * np.cos((2*np.pi*w_freq*xdata)+lag))+(1j * (idata * np.cos((2*np.pi*w_freq*xdata)+lag)))
    #return fit_y
for runs in range(2):
    main(gen.lo_band_tx_ph_coherency(4,runs))
table_freq(run_array,freq_array)
table_amp(run_array,amp_array)
table_phase(run_array,phase_array)
main(gen.lo_band_rx_ph_coherency(4))
