from common import sigproc
from common import engine
from common import generator as gen
from retrying import retry
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import sys
import statistics

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
        heading_names = ["FREQUENCY","AMPLITUDE","PHASE"]
        ch0 = []
        ch1 = []
        ch2 = []
        ch3 = []
        AB_data = []
        AC_data = []
        AD_data = []
        print("Difference in Frequency, Amplitude and Phase of channels with respect to channel A \n")
        for index , h in enumerate(heading_names, start = 0):
            print(h)
            print("{:^10}|{:^10}|{:^10}|{:^10}|".format("Runs", "AB", "AC", "AD"))
            print("---------------------------------------------------------\n")
            for runs in range(2):
               print("{:^10}|".format(runs),end=" ")
               ch0.clear()
               ch1.clear()
               ch2.clear()
               ch3.clear()
               AB_data.clear()
               AC_data.clear()
               AD_data.clear()
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
                        if index == 0:
                            np.array(ch0.append(w_freq))
                        elif index == 1:
                            np.asarray(ch0.append(max(real)))
                        else:
                            np.asarray(ch0.append(abs_phase))
                     elif ch == 1:
                         if index == 0:
                            np.array(ch1.append(w_freq))
                         elif index == 1:
                            np.asarray(ch1.append(max(real)))
                         else:
                            np.asarray(ch1.append(abs_phase))
                     elif ch == 2:
                         if index == 0:
                            np.array(ch2.append(w_freq))
                         elif index == 1:
                            np.asarray(ch2.append(max(real)))
                         else:
                            np.asarray(ch2.append(abs_phase))
                     else:
                         if index == 0:
                            np.array(ch3.append(w_freq))
                         elif index == 1:
                            np.asarray(ch3.append(max(real)))
                         else:
                            np.asarray(ch3.append(abs_phase))
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


               AB = np.subtract(ch1, ch0)
               np.array(AB_data.append(AB))
               AC = np.subtract(ch2, ch0)
               np.array(AC_data.append(AC))
               AD = np.subtract(ch3, ch0)
               np.array(AD_data.append(AD))
               #print("Channel parameters",*ch0,*ch1,*ch2,*ch3, sep = " ")
               print("{:^10.8f}|{:^10.8f}|{:^10.8f}|".format(*AB,*AC,*AD))
               # print("                      ",end=" ")
               #print(*AB,*AC,*AD, sep = "                   ")
               if(runs == 1):
                  print("{:^10}|{:^11.8f}|{:^11.8f}|{:^11.8f}|".format("Min diff",min(AB),min(AC),min(AD)))
                  # print("Min difference", min(AB), min(AC), min(AD), sep = "                    ")
                  # print("\n")
                  print("{:^10}|{:^11.8f}|{:^11.8f}|{:^11.8f}|".format("Max diff",max(AB),max(AC),max(AD)))
                  # print("Max difference", max(AB), max(AC), max(AD), sep = "                    ")
                  # print("\n")
                  print("{:^10}|{:^11.8f}|{:^11.8f}|{:^11.8f}|".format("Mean Value",np.mean(AB_data),np.mean(AC_data), np.mean(AD_data)))
                  # print("Mean Value", np.mean(AB_data), np.mean(AC_data), np.mean(AD_data), sep = "                    ")
                  # print("\n")
                  print("{:^10}|{:^11.8f}|{:^11.8f}|{:^11.8f}|".format("Std Dev",np.std(AB_data), np.std(AC_data), np.std(AD_data)))
                  # print("Std Deviation", np.std(AB_data), np.std(AC_data), np.std(AD_data), sep = "                     ")
                  print("\n\n")

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

main(gen.lo_band_tx_ph_coherency(4))
main(gen.lo_band_rx_ph_coherency(4))
