from common import sigproc
from common import engine
from common import generator as gen
from retrying import retry
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import sys
import statistics
import os
f_array = []
run_array_tx =[]
run_array_rx =[]
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
x_array = []
r_array = []
script_dir = os.path.dirname(__file__)
results_dir = os.path.join(script_dir, 'Test_Results/')
frequency_filepath = os.path.join(results_dir, 'freq_result_file.txt')
amp_filepath = os.path.join(results_dir, 'amp_result_file.txt')
phase_filepath = os.path.join(results_dir, 'phase_result_file.txt')

if not os.path.isdir(results_dir):
    os.makedirs(results_dir)
def fit_func(xdata, A, f_wave, abs_phase):
    #fit_y = A*np.exp((2*np.pi*f_wave*xdata)+abs_phase)
    fit_y = A*np.cos(2*np.pi*f_wave*xdata+abs_phase)
    return fit_y
def table_freq(run_array,f_array):
    for run_val in range(len(run_array)):
        index_val = run_val*4
        AB = np.subtract(f_array[index_val], f_array[index_val+1])
        np.array(AB_f_data.append(AB))
        AC = np.subtract(f_array[index_val], f_array[index_val+2])
        np.array(AC_f_data.append(AC))
        AD = np.subtract(f_array[index_val], f_array[index_val+3])
        np.array(AD_f_data.append(AD))
        if(run_val == (len(run_array)-1)):
          min_AB = min(AB_f_data)
          min_AC = min(AC_f_data)
          min_AD = min(AD_f_data)
          max_AB = max(AB_f_data)
          max_AC = max(AC_f_data)
          max_AD = max(AD_f_data)
          mean_AB = np.mean(AB_f_data)
          mean_AC = np.mean(AC_f_data)
          mean_AD = np.mean(AD_f_data)
          std_AB = np.std(AB_f_data)
          std_AC = np.std(AC_f_data)
          std_AD = np.std(AD_f_data)
          return [min_AB,min_AC,min_AD,max_AB,max_AC,max_AD,mean_AB,mean_AC,mean_AD,std_AB,std_AC,std_AD,AB_f_data,AC_f_data,AD_f_data]
def table_amp(run_array,amp_array):
        for run_val in range(len(run_array)):
            index_val = run_val*4
            AB = np.subtract(amp_array[index_val+1], amp_array[index_val])
            np.array(AB_a_data.append(AB))
            AC = np.subtract(amp_array[index_val+2], amp_array[index_val])
            np.array(AC_a_data.append(AC))
            AD = np.subtract(amp_array[index_val+3], amp_array[index_val])
            np.array(AD_a_data.append(AD))
            if(run_val == (len(run_array)-1)):
               min_AB = min(AB_a_data)
               min_AC = min(AC_a_data)
               min_AD = min(AD_a_data)
               max_AB = max(AB_a_data)
               max_AC = max(AC_a_data)
               max_AD = max(AD_a_data)
               mean_AB = np.mean(AB_a_data)
               mean_AC = np.mean(AC_a_data)
               mean_AD = np.mean(AD_a_data)
               std_AB = np.std(AB_a_data)
               std_AC = np.std(AC_a_data)
               std_AD = np.std(AD_a_data)
               return [min_AB,min_AC,min_AD,max_AB,max_AC,max_AD,mean_AB,mean_AC,mean_AD,std_AB,std_AC,std_AD,AB_a_data,AC_a_data,AD_a_data]

def table_phase(run_array,phase_array):
        for run_val in range(len(run_array)):
            index_val = run_val*4
            AB = np.subtract(phase_array[index_val], phase_array[index_val+1])
            np.array(AB_p_data.append(AB))
            AC = np.subtract(phase_array[index_val], phase_array[index_val+2])
            np.array(AC_p_data.append(AC))
            AD = np.subtract(phase_array[index_val], phase_array[index_val+3])
            np.array(AD_p_data.append(AD))
            if(run_val == (len(run_array)-1)):
               min_AB = np.degrees(min(AB_p_data))
               min_AC = np.degrees(min(AC_p_data))
               min_AD = np.degrees(min(AD_p_data))
               max_AB = np.degrees(max(AB_p_data))
               max_AC = np.degrees(max(AC_p_data))
               max_AD = np.degrees(max(AD_p_data))
               mean_AB = np.degrees(np.mean(AB_p_data))
               mean_AC = np.degrees(np.mean(AC_p_data))
               mean_AD = np.degrees(np.mean(AD_p_data))
               std_AB = np.degrees(np.std(AB_p_data))
               std_AC = np.degrees(np.std(AC_p_data))
               std_AD = np.degrees(np.std(AD_p_data))
               return [min_AB,min_AC,min_AD,max_AB,max_AC,max_AD,mean_AB,mean_AC,mean_AD,std_AB,std_AC,std_AD,AB_p_data,AC_p_data,AD_p_data]

def main(iterations):
    for it in iterations:
        if(runs_tx == 0):
          gen.dump(it)
        # Collect.
        tx_stack = [ (10,     it["sample_rate" ]) ]     # One seconds worth.
        rx_stack = [ (10.5,     it["sample_count"])]     # Half a seconds worth.
        vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
        error_detected = 0
        run_array_tx.append(runs_tx)
        #run_array_rx.append(runs_rx)

        for ch, channel in enumerate(vsnk):

                     real = [datum.real for datum in channel.data()]
                     imag = [datum.imag for datum in channel.data()]
                     w_freq = it["wave_freq"]
                     time=np.arange(0,it["sample_count"]/it["sample_rate"], 1/it["sample_rate"])

                     xdata = np.asarray(time)

                     rdata = np.asarray(real)
                     #print(rdata)
                     idata = np.asarray(imag)

                     #real_data = idata*1j + real #Numpy curve fit doesn't handle complex numbers

                     rdata_max = max(rdata)
                     guess_opt=[rdata_max, w_freq, 0.75]
                     p_opt,p_cov = curve_fit(fit_func, xdata, rdata, p0=guess_opt)
                     A=p_opt[0]
                     f_wave=p_opt[1]
                     abs_phase=p_opt[2]
                     if ch == 0:
                            np.array(f_array.append(f_wave))
                            np.asarray(x_array.append(xdata))
                            np.asarray(r_array.append(rdata))
                            np.asarray(amp_array.append(A))
                            np.asarray(phase_array.append(abs_phase))
                     elif ch == 1:
                            np.array(f_array.append(f_wave))
                            np.asarray(x_array.append(xdata))
                            np.asarray(r_array.append(rdata))
                            np.asarray(amp_array.append(A))
                            np.asarray(phase_array.append(abs_phase))
                     elif ch == 2:
                            np.array(f_array.append(f_wave))
                            np.asarray(x_array.append(xdata))
                            np.asarray(r_array.append(rdata))
                            np.asarray(amp_array.append(A))
                            np.asarray(phase_array.append(abs_phase))
                     else:
                            np.array(f_array.append(f_wave))
                            np.asarray(x_array.append(xdata))
                            np.asarray(r_array.append(rdata))
                            np.asarray(amp_array.append(A))
                            np.asarray(phase_array.append(abs_phase))
        if(runs_tx == 9):
          freq_stat  = table_freq(run_array_tx,f_array)
          amp_stat   = table_amp(run_array_tx,amp_array)
          phase_stat = table_phase(run_array_tx,phase_array)
          #FREQUENCY
          try:
                    assert (freq_stat[6] < 0.1 and freq_stat[7] < 0.1 and freq_stat[8] < 0.1) and (freq_stat[9] < 0.0001 and freq_stat[10] < 0.0001 and freq_stat[11] < 0.0001) and (freq_stat[3] <= (freq_stat[6] + 3*freq_stat[9]) and freq_stat[4] <= (freq_stat[7] + 3*freq_stat[10]) and freq_stat[5] <= (freq_stat[8] + 3*freq_stat[11])) and (freq_stat[0] >= (freq_stat[6] - 3*freq_stat[9]) and freq_stat[1] >= (freq_stat[7] - 3*freq_stat[10]) and freq_stat[2] >= (freq_stat[8] - 3*freq_stat[11]))
          except:
                    f_result_file= open(frequency_filepath,"w")
                    print("\n")
                    print("FREQUENCY TEST FAILED")
                    f_result_file.write("FREQUENCY TEST FAILED \n")
                    print("{:^12}|{:^12}|{:^12}|{:^12}|".format( "Runs", "AB", "AC","AD"))
                    f_result_file.write("{:^12}|{:^12}|{:^12}|{:^12}|\n".format( "Runs", "AB", "AC","AD"))
                    print("---------------------------------------------------------\n")
                    f_result_file.write("---------------------------------------------------------\n")
                    AB_freq = freq_stat[12]
                    AC_freq = freq_stat[13]
                    AD_freq = freq_stat[14]
                    freq_results_dir = os.path.join(results_dir, 'Frequency_Test_Results/')
                    if not os.path.isdir(freq_results_dir):
                       os.makedirs(freq_results_dir)
                    for run in range(len(run_array_tx)):
                        print("{:^12}|".format(run),end=" ")
                        f_result_file.write("{:^12}|".format(run))
                        print("{:^12.8f}|{:^12.8f}|{:^12.8f}|".format(AB_freq[run],AC_freq[run],AD_freq[run]))
                        f_result_file.write("{:^12.8f}|{:^12.8f}|{:^12.8f}|\n".format(AB_freq[run],AC_freq[run],AD_freq[run]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Min diff",freq_stat[0],freq_stat[1],freq_stat[2]))
                    f_result_file.write("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|\n".format("Min diff",freq_stat[0],freq_stat[1],freq_stat[2]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Max diff",freq_stat[3],freq_stat[4],freq_stat[5]))
                    f_result_file.write("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|\n".format("Min diff",freq_stat[3],freq_stat[4],freq_stat[5]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Mean Value",freq_stat[6],freq_stat[7],freq_stat[8]))
                    f_result_file.write("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|\n".format("Mean Value",freq_stat[6],freq_stat[7],freq_stat[8]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Std Dev",freq_stat[9],freq_stat[10],freq_stat[11]))
                    f_result_file.write("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|\n".format("Std Dev",freq_stat[9],freq_stat[10],freq_stat[11]))
                    fig = plt.figure()
                    for i, channel in enumerate(vsnk):
                        #print("plots")
                        ax = fig.add_subplot(2, 2, i+1)
                        ax.set_title("Time Plot for channel {}".format(i))
                        plt.xlabel("time")
                        plt.ylabel("Amplitude")
                        time_array = x_array[i]
                        real_array = r_array[i]
                        #print(real_array)
                        ax.plot(time_array[0:500], real_array[0:500], color='red', label='real')
                        plt.tight_layout()
                        file_name = "timeplot-all-channel{}-wavefreq-{}.png".format(it["wave_freq"],it["name"])
                        plt.savefig(os.path.join(freq_results_dir, file_name))
                        #plt.savefig(fname='Amplitude plot'.format(format='png'))
                    for c_plot, channel in enumerate(vsnk):
                        plt.figure()
                        c_x_array = x_array[c_plot]
                        c_r_array = r_array[c_plot]
                        r_max = max(c_r_array)
                        plt.plot(c_x_array[0:250], c_r_array[0:250], 'o')
                        file_name = "dataplot-for-channel {}".format(c_plot)
                        plt.savefig(os.path.join(freq_results_dir, file_name))
                        #plt.savefig(fname='dataplot-for-channels')
                        plt.legend(["blue", "green"],fontsize="large",loc ="lower right")
                        fit_data = fit_func(c_x_array, r_max, f_array[c_plot], phase_array[c_plot])
                        plt.plot(c_x_array[0:250], fit_data[0:250], '-')
                        plt.legend(["blue", "green"],fontsize="large",loc ="lower right")
                        file_name = "Fitplot for channel {}".format(c_plot)
                        plt.savefig(os.path.join(freq_results_dir, file_name))

          else:
                    print("\n")
                    print("FREQUENCY TEST PASSED")
                    print("Summary of Frequency Test for {} Runs".format(len(run_array_tx)))
                    print("{:^12}|{:^12}|{:^12}|{:^12}|".format("Parameters","AB", "AC", "AD"))
                    print("--------------------------------------------\n")
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Min diff",freq_stat[0],freq_stat[1],freq_stat[2]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Max diff",freq_stat[3],freq_stat[4],freq_stat[5]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Mean Value",freq_stat[6],freq_stat[7],freq_stat[8]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Std Dev",freq_stat[9],freq_stat[10],freq_stat[11]))
          #AMPLITUDE
          try:
                    assert (amp_stat[6] > 3*amp_stat[9]  and amp_stat[7] > 3*amp_stat[10]  and amp_stat[8] > 3*amp_stat[11]) and (amp_stat[9] < 0.0002 and amp_stat[10] < 0.0002 and amp_stat[11] < 0.0002) and (amp_stat[3] <= (amp_stat[6] + 3*amp_stat[9]) and amp_stat[4] <= (amp_stat[7] + 3*amp_stat[10]) and amp_stat[5] <= (amp_stat[8] + 3*amp_stat[11])) and (amp_stat[0] >= (amp_stat[6] - 3*amp_stat[9]) and amp_stat[1] >= (amp_stat[7] - 3*amp_stat[10]) and amp_stat[2] >= (amp_stat[8] - 3*amp_stat[11]))
          except:
                    a_result_file= open(amp_filepath,"w")
                    print("\n")
                    print("AMPLITUDE TEST FAILED")
                    a_result_file.write("AMPLITUDE TEST FAILED \n")
                    print("{:^12}|{:^12}|{:^12}|{:^12}|".format( "Runs", "AB", "AC","AD"))
                    a_result_file.write("{:^12}|{:^12}|{:^12}|{:^12}|\n".format( "Runs", "AB", "AC","AD"))
                    print("---------------------------------------------------------\n")
                    a_result_file.write("---------------------------------------------------------\n")
                    AB_amp = amp_stat[12]
                    AC_amp = amp_stat[13]
                    AD_amp = amp_stat[14]
                    amp_results_dir = os.path.join(results_dir, 'Amplitude_Test_Results/')
                    if not os.path.isdir(amp_results_dir):
                       os.makedirs(amp_results_dir)
                    for run in range(len(run_array_tx)):
                        print("{:^12}|".format(run),end=" ")
                        a_result_file.write("{:^12}|".format(run))
                        print("{:^12.8f}|{:^12.8f}|{:^12.8f}|".format(AB_amp[run],AC_amp[run],AD_amp[run]))
                        a_result_file.write("{:^12.8f}|{:^12.8f}|{:^12.8f}|\n".format(AB_amp[run],AC_amp[run],AD_amp[run]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Min diff",amp_stat[0],amp_stat[1],amp_stat[2]))
                    a_result_file.write("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|\n".format("Min diff",amp_stat[0],amp_stat[1],amp_stat[2]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Max diff",amp_stat[3],amp_stat[4],amp_stat[5]))
                    a_result_file.write("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|\n".format("Min diff",amp_stat[3],amp_stat[4],amp_stat[5]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Mean Value",amp_stat[6],amp_stat[7],amp_stat[8]))
                    a_result_file.write("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|\n".format("Mean Value",amp_stat[6],amp_stat[7],amp_stat[8]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Std Dev",amp_stat[9],amp_stat[10],amp_stat[11]))
                    a_result_file.write("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|\n".format("Std Dev",amp_stat[9],amp_stat[10],amp_stat[11]))
                    fig = plt.figure()
                    for i, channel in enumerate(vsnk):
                        #print("plots")
                        ax = fig.add_subplot(2, 2, i+1)
                        ax.set_title("Time Plot for channel {}".format(i))
                        plt.xlabel("time")
                        plt.ylabel("Amplitude")
                        time_array = x_array[i]
                        real_array = r_array[i]
                        #print(real_array)
                        ax.plot(time_array[0:500], real_array[0:500], color='red', label='real')
                        plt.tight_layout()
                        file_name = "timeplot-all-channel{}-wavefreq-{}.png".format(it["wave_freq"],it["name"])
                        plt.savefig(os.path.join(amp_results_dir, file_name))
                        #plt.savefig(fname='Amplitude plot'.format(format='png'))
                    for c_plot, channel in enumerate(vsnk):
                        plt.figure()
                        c_x_array = x_array[c_plot]
                        c_r_array = r_array[c_plot]
                        r_max = max(c_r_array)
                        plt.plot(c_x_array[0:250], c_r_array[0:250], 'o')
                        file_name = "dataplot-for-channel {}".format(c_plot)
                        plt.savefig(os.path.join(amp_results_dir, file_name))
                        #plt.savefig(fname='dataplot-for-channels')
                        plt.legend(["blue", "green"],fontsize="large",loc ="lower right")
                        fit_data = fit_func(c_x_array, r_max, f_array[c_plot], phase_array[c_plot])
                        plt.plot(c_x_array[0:250], fit_data[0:250], '-')
                        plt.legend(["blue", "green"],fontsize="large",loc ="lower right")
                        file_name = "Fitplot for channel {}".format(c_plot)
                        plt.savefig(os.path.join(amp_results_dir, file_name))
          else:
                    print("\n")
                    print("AMPLITUDE TEST PASSED")
                    print("Summary of Amplitude Test for {} Runs".format(len(run_array_tx)))
                    print("{:^12}|{:^12}|{:^12}|{:^12}|".format("Parameters","AB", "AC", "AD"))
                    print("--------------------------------------------\n")
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Min diff",amp_stat[0],amp_stat[1],amp_stat[2]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Max diff",amp_stat[3],amp_stat[4],amp_stat[5]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Mean Value",amp_stat[6],amp_stat[7],amp_stat[8]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Std Dev",amp_stat[9],amp_stat[10],amp_stat[11]))
          #PHASE
          try:
                    assert ((phase_stat[6] > -2 and phase_stat[6] < 2) and (phase_stat[7] > -2 and phase_stat[7] < 2) and (phase_stat[8] > -2 and phase_stat[8] < 2)) and (phase_stat[9] < 0.006 and phase_stat[10] < 0.006 and phase_stat[11] < 0.006) and (phase_stat[3] <= (phase_stat[6] + 3*phase_stat[9]) and phase_stat[4] <= (phase_stat[7] + 3*phase_stat[10]) and phase_stat[5] <= (phase_stat[8] + 3*phase_stat[11])) and (phase_stat[0] >= (phase_stat[6] - 3*phase_stat[9]) and phase_stat[1] >= (phase_stat[7] - 3*phase_stat[10]) and phase_stat[2] >= (phase_stat[8] - 3*phase_stat[11]))
          except:
                    p_result_file= open(phase_filepath,"w")
                    print("\n")
                    print("PHASE TEST FAILED")
                    p_result_file.write("PHASE TEST FAILED \n")
                    print("{:^12}|{:^12}|{:^12}|{:^12}|".format( "Runs", "AB", "AC","AD"))
                    p_result_file.write("{:^12}|{:^12}|{:^12}|{:^12}|\n".format( "Runs", "AB", "AC","AD"))
                    print("---------------------------------------------------------\n")
                    p_result_file.write("---------------------------------------------------------\n")
                    AB_phase = phase_stat[12]
                    AC_phase = phase_stat[13]
                    AD_phase = phase_stat[14]
                    phase_results_dir = os.path.join(results_dir, 'Phase_Test_Results/')
                    if not os.path.isdir(phase_results_dir):
                       os.makedirs(phase_results_dir)
                    for run in range(len(run_array_tx)):
                        print("{:^12}|".format(run),end=" ")
                        p_result_file.write("{:^12}|".format(run))
                        print("{:^12.8f}|{:^12.8f}|{:^12.8f}|".format(np.degrees(AB_phase[run]),np.degrees(AC_phase[run]),np.degrees(AD_phase[run])))
                        p_result_file.write("{:^12.8f}|{:^12.8f}|{:^12.8f}|\n".format(AB_phase[run],AC_phase[run],AD_phase[run]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Min diff",phase_stat[0],phase_stat[1],phase_stat[2]))
                    p_result_file.write("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|\n".format("Min diff",phase_stat[0],phase_stat[1],phase_stat[2]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Max diff",phase_stat[3],phase_stat[4],phase_stat[5]))
                    p_result_file.write("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|\n".format("Max diff",phase_stat[3],phase_stat[4],phase_stat[5]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Mean Value",phase_stat[6],phase_stat[7],phase_stat[8]))
                    p_result_file.write("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|\n".format("Mean Value",phase_stat[6],phase_stat[7],phase_stat[8]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Std Dev",phase_stat[9],phase_stat[10],phase_stat[11]))
                    p_result_file.write("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|\n".format("Std Dev",phase_stat[9],phase_stat[10],phase_stat[11]))
                    p_result_file.close()
                    fig = plt.figure()
                    for i, channel in enumerate(vsnk):
                        #print("plots")
                        ax = fig.add_subplot(2, 2, i+1)
                        ax.set_title("Time Plot for channel {}".format(i))
                        plt.xlabel("time")
                        plt.ylabel("Amplitude")
                        time_array = x_array[i]
                        real_array = r_array[i]
                        #print(real_array)
                        ax.plot(time_array[0:500], real_array[0:500], color='red', label='real')
                        plt.tight_layout()
                        file_name = "timeplot-all-channel{}-wavefreq-{}.png".format(it["wave_freq"],it["name"])
                        plt.savefig(os.path.join(phase_results_dir, file_name))
                        #plt.savefig(fname='Amplitude plot'.format(format='png'))
                    for c_plot, channel in enumerate(vsnk):
                        plt.figure()
                        c_x_array = x_array[c_plot]
                        c_r_array = r_array[c_plot]
                        r_max = max(c_r_array)
                        plt.plot(c_x_array[0:250], c_r_array[0:250], 'o')
                        file_name = "dataplot-for-channel {}".format(c_plot)
                        plt.savefig(os.path.join(phase_results_dir, file_name))
                        #plt.savefig(fname='dataplot-for-channels')
                        plt.legend(["blue", "green"],fontsize="large",loc ="lower right")
                        fit_data = fit_func(c_x_array, r_max, f_array[c_plot], phase_array[c_plot])
                        plt.plot(c_x_array[0:250], fit_data[0:250], '-')
                        plt.legend(["blue", "green"],fontsize="large",loc ="lower right")
                        file_name = "Fitplot for channel {}".format(c_plot)
                        plt.savefig(os.path.join(phase_results_dir, file_name))
          else:
                    print("\n")
                    print("PHASE TEST PASSED")
                    print("Summary of Phase Test for {} Runs".format(len(run_array_tx)))
                    print("{:^12}|{:^12}|{:^12}|{:^12}|".format("Parameters","AB", "AC", "AD"))
                    print("--------------------------------------------\n")
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Min diff",phase_stat[0],phase_stat[1],phase_stat[2]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Max diff",phase_stat[3],phase_stat[4],phase_stat[5]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Mean Value",phase_stat[6],phase_stat[7],phase_stat[8]))
                    print("{:^12}|{:^12.8f}|{:^12.8f}|{:^12.8f}|".format("Std Dev",phase_stat[9],phase_stat[10],phase_stat[11]))



for runs_tx in range(10):
    main(gen.lo_band_tx_ph_coherency(4,runs_tx))
# freq_stat  = table_freq(run_array_tx,f_array)
# amp_stat   = table_amp(run_array_tx,amp_array)
# phase_stat = table_phase(run_array_tx,phase_array)
#print(real_array_0)
#disp_test(freq_stat,amp_stat,phase_stat,f_array,amp_array,phase_array,x_data_0,real_array_0)

