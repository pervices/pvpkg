from common import sigproc
from common import engine
from common import generator as gen
from common import pdf_report
from common import test_args

import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import stats
import math

from common import outputs as out
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import norm
from scipy.signal import find_peaks
from scipy import signal
import sys
import os
from datetime import datetime
import time
import argparse

#USER CHOSEN VALUES
num_output_waves =1 #depends what plots look like
begin_cutoff_waves = 1 #0.00000425 #e(-5) - guessed from previous diagrams (but seconds)
tx_burst = 5.0 #burst should be slightly delayed to ensure all data is being collected
rx_burst = 5.25

std_ratio = 4  #number std gets multiplied by for checks, normalized to a sample size of 10
               #This value is adjusted later depending on the number of runs.

std_ratio_phase = 8  #number std gets multiplied by for checks, normalized to a sample size of 10
                     #This value is adjusted later depending on the number of runs.

wave_freq = -1 
runs = -1 
iteration_count = -1
sample_rate = -1
plotted_samples = -1
sample_count = -1

# Criteria  
freq_std_thresh = 0.6    
ampl_std_thresh = 0.001
phase_mean_thresh = 0.0349066 #rad bound
phase_std_thresh = 0.002

now = datetime.now() 
iso_time = now.strftime("%Y%m%d%H%M%S.%f")

#Setting up directories for plots
parent_dir = os.getcwd()
leaf_dir = "dump/"
dump_dir = parent_dir + leaf_dir
dump_path = os.path.join("./", dump_dir)
os.makedirs(dump_path,exist_ok=True)

test_plots = dump_dir + iso_time + "-tx_rx_phase_2"
os.makedirs(test_plots, exist_ok = True)

reals = []
best_fits = []
x_time = []
offsets = []

baselineCh_index = 0
channel_map = np.array(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])

def waveEquation(time, ampl, freq, phase, dc_offset):

    y = ampl*np.cos((2*np.pi*freq*time + phase)) + dc_offset #model for wave equation
    return y

def subPlot(x, y, ax, best_fit, offset, title):
    ax.set_title(title)
    ax.set_xlabel("Time")
    ax.set_ylabel("Amplitude")
    ax.plot(x, y, '.', color='magenta', label='Real')
    ax.plot(x, best_fit, '-', color='black', label='Best Fit')
    #ax.plot(x, offset, color='green', label='DC Offset')
    ax.axhline(y = offset, color='green', label='DC Offset')
    ax.legend()

    peaks = find_peaks(y)
    f = open("Data_Plots.txt", "a")
    if len(peaks[0]) > 0:
        f.write("\n" + title + ": " + str(y[peaks[0][0]]))
    else:
        f.write("\n" + title + ": 0 find_peaks fail")
    f.write("\n" + str(y))
    f.close()

def bestFit(x, y):
    guess = [max(y), wave_freq, 0.25, 0] #Based off generator code
    param, covariance  = curve_fit(waveEquation, x, y, p0=guess) #using curve fit to give parameters
    fit_amp = param[0]                                           #for wave equation that make a line of best fit
    fit_freq = param[1]
    fit_phase = param[2]
    fit_offset = param[3]
    best_fit = waveEquation(x, fit_amp, fit_freq, fit_phase, fit_offset) #making the line of best fit

    return (best_fit, fit_offset), (fit_amp, fit_freq, fit_phase) #returns other values as tuple, so they can be easily referenced

def makePlots():

    global plotted_samples
    plotted_samples = int(round(1/(int(wave_freq)/sample_rate))*num_output_waves)
    f = open("Data_Plots.txt", "w")
    f.close()

    num_subplot_rows = int(math.ceil(len(targs.channels) / 2))
    for run in range(runs+1):
        fig, axes = plt.subplots(num_subplot_rows, 2)
        plt.suptitle("Amplitude versus Samples: Individual Channels for Run {}".format(run))

        os.chdir(test_plots) #To save to a file

        row = 0
        for ch in range(len(targs.channels)):
            subplot_row = int(ch / 2)
            subPlot(x_time[0:plotted_samples], reals[run][ch][0:plotted_samples], axes[subplot_row][ch%2], best_fits[run][ch][0:plotted_samples], offsets[run][ch], "Channel {}".format(channel_map[targs.channels[ch]]))

        plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0) #Formatting the plots nicely

        os.chdir(test_plots)
        fig.savefig(("run{}_indiv".format(ch) + ".svg"))
        s1 = report.get_image_io_stream()
        fig.savefig(s1, format="png", dpi=300)
        img1 = report.get_image_from_io_stream(s1)
        plt.clf()

        #Layout of the combined plot 
        fig = plt.figure("Amplitude vs Time All Channels")
        plt.title("Amplitude versus Samples: All Channels for Run {}".format(run))
        plt.xlabel("Time")
        plt.ylabel("Amplitude")

        #dots
        for ch in range(len(targs.channels)):
            plt.plot(x_time[0:plotted_samples], reals[run][ch][0:plotted_samples], '.', markersize=3, label="Real {}".format(channel_map[targs.channels[ch]]))

        #Best fits
        for ch in range(len(targs.channels)):
            plt.plot(x_time[0:plotted_samples], best_fits[run][ch][0:plotted_samples], '-', linewidth= 0.75, label="Best Fit {}".format(channel_map[targs.channels[ch]]))

        plt.legend()

        fig.savefig(("run{}_together".format(run) + ".svg"))
        s2 = report.get_image_io_stream()
        fig.savefig(s2, format="png", dpi=300)
        img2 = report.get_image_from_io_stream(s2)

        report.buffer_put("image_double", [img1, img2], "Run " + str(run))
        print("Run figure has been put in buffer")
        plt.clf()

def boolToWord(word):
    if word > 0:
        return("Pass")
    elif word < 0:
        return "N/A"
    else:
        return("Fail")

def main():
    # Add test specific arguments
    p = argparse.ArgumentParser(description = "Loopback phase coherency test")
    p.add_argument('-r', '--rate', default=25000000, type=int, help="Sample rate in samples per second")
    p.add_argument('-b', '--band', default=False, type=bool, help="Apply a band pass filter to the data")
    # Add generic test arguments
    global targs 
    targs = test_args.TestArgs(parser=p, testDesc="Loopback phase coherency test")

    args = p.parse_args()

    # PDF Report
    global report
    report = pdf_report.ClassicShipTestReport("tx_rx_phase_2", targs.serial, targs.report_dir, targs.docker_sha)
    report.insert_title_page("Low Band TX RX Phase Coherency Test 2")

    print("Title page generated")
    '''This iteration loop will run through setting up the channels to the values associated to the generator code. It will also loop through
    each channel and save the information to temp arrays. These temp arrays allow us to format our data into 2D arrays, so it's easier to
    reference later'''

    table_printed_once = 0
    num_runs = 2

    if(targs.product == 'Vaunt'):
        iterations = gen.lo_band_phaseCoherency(num_runs)
    elif(targs.product == 'Tate'):
        iterations = gen.cyan.lo_band.phaseCoherency(num_runs)
    elif(targs.product == 'Lily'):
        iterations = gen.chestnut.lo_band.phaseCoherency(num_runs)

    
    # First column is the first channel's value. Subsequent columns are the delta between that channel and the first.
    # Example: channel list is [0, 1, 3], freq_delta_matrix for a single iteration would be as follows:
    # [freqCh0, freqCh1 - freqCh0, freqCh3 - freqCh0]
    freq_delta_matrix = np.zeros((num_runs, len(targs.channels)))
    ampl_delta_matrix = np.zeros((num_runs, len(targs.channels)))
    phase_delta_matrix = np.zeros((num_runs, len(targs.channels)))
    offset_delta_matrix = np.zeros((num_runs, len(targs.channels)))

    num_iter = 0
    for it in iterations:
        num_iter+=1
        gen.dump(it) 

        '''
        Note how each step of time is equiv to 1/sample_rate
        When you reach sample_rate/sample_rate, one second has passed.
        TX: Below, we will be sending oiut samples equiv. to sample_rate after 10 seconds, so this will end at 11 seconds
        RX: Calculate the oversampling rate to find the number of samples to intake that match your ideal (sample count)
        '''

        global sample_rate
        sample_rate = args.rate
        tx_stack = [ (tx_burst , sample_rate)]
        rx_stack = [ (rx_burst, int(it["sample_count"]))]

        try:
            vsnk = engine.run(targs.channels, it["wave_freq"], sample_rate, it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
        except Exception as err:
            report.draw_from_buffer()
            report.save()
            sys.exit(1)

        if (table_printed_once == 0):
            table_data = [["Center Frequency (Hz)", "Wave Frequency (Hz)", "Sample Rate (SPS)", "Sample Count", "TX Gain (dB)", "RX Gain (dB)"],
                            [it["center_freq"], it["wave_freq"], sample_rate, it["sample_count"], it["tx_gain"], it["rx_gain"]]]
            report.buffer_put("table_wide", table_data, "Test Configuration")
            table_printed_once = 1

        global sample_count
        sample_count = int(it["sample_count"])
        global runs
        runs = it["i"] #equal sign because we only care about the last value
        global wave_freq
        wave_freq = int(it["wave_freq"])

        # Number of waves to cutoff before starting analysis
        global begin_cutoff_waves
        begin_cutoff = int(round((1/(wave_freq/sample_rate))*begin_cutoff_waves))

        global x_time
        x_time = np.linspace(begin_cutoff/sample_rate, sample_count/sample_rate, num=sample_count-begin_cutoff)

        ampl = []
        freq = []
        phase = []
        offset = []
        best = []
        ch_real_data = []

        for ch, channel in enumerate(vsnk): 
            real = [datum.real for datum in channel.data()]

            if len(real) == 0:
                raise Exception ("No data received on rx")
            elif len(real) <= begin_cutoff:
                raise Exception ("Rx received less data than cutoff. Received: " + str(len(real)) + ". Required: " + str(begin_cutoff))

            # Filter data so we only see the phase of the intended signal if requested by user
            if args.band:
                b,a = signal.bessel(1, [wave_freq * 0.9, wave_freq * 1.1], 'bandpass', analog=False, norm='delay', fs = sample_rate)
                real = signal.filtfilt(b, a, real, padtype=None)

                if len(real) <= begin_cutoff:
                    raise Exception ("Filter error, rx data lost")

            # Explicitly assigning the relevant slice of data to a variable, then passing said variable to bestFit
            # Creating a slice anonymously may cause a crash where somehow data collected the the engine wasn't making it to bestFit
            trimmed_real = real[begin_cutoff:]

            ch_real_data.append(trimmed_real)

            best_fit, param = bestFit(x_time, trimmed_real)

            # For intuitive phase comparison, amplitudes need to either be all pos or all neg. Here we'll take the absolute
            # value of amplitude, and adjust the phase by pi if the amplitude was negative. Wrap phase if it exceeds 2pi.
            adjusted_phase = param[2]
            if param[0] < 0:
                adjusted_phase += math.pi
                if adjusted_phase > (2*math.pi):
                    adjusted_phase -= (2*math.pi)

            abs_ampl = abs(param[0])

            ampl.append(abs_ampl)
            freq.append(param[1])
            phase.append(adjusted_phase)
            best.append(best_fit[0])
            offset.append((best_fit[1]))

        #Appending to the temp variables
        reals.append(ch_real_data)
        best_fits.append(best)
        offsets.append(offset)

        freq_delta_matrix[runs][baselineCh_index] = freq[baselineCh_index]
        ampl_delta_matrix[runs][baselineCh_index] = ampl[baselineCh_index]
        phase_delta_matrix[runs][baselineCh_index] = phase[baselineCh_index]
        offset_delta_matrix[runs][baselineCh_index] = offset[baselineCh_index]
        for channel in range(1, len(targs.channels)):
            freq_delta_matrix[runs][channel] = freq[channel] - freq[baselineCh_index]
            ampl_delta_matrix[runs][channel] = ampl[channel] - ampl[baselineCh_index]
            phase_delta_matrix[runs][channel] = phase[channel] - phase[baselineCh_index]
            offset_delta_matrix[runs][channel] = offset[channel] - offset[baselineCh_index]

    # Basic stats for freq, ampl, and phase
    freq_index = 0                          # Row 0 - Freq
    ampl_index = 1                          # Row 1 - Ampl
    phase_index = 2                         # Row 2 - Phase
    means = np.zeros((3, len(targs.channels)))
    stds = np.zeros((3, len(targs.channels)))
    mins = np.zeros((3, len(targs.channels)))
    maxs = np.zeros((3, len(targs.channels)))

    means[freq_index][:] = np.mean(freq_delta_matrix, axis=0)  # setting axis to 0 will return an array of the mean of each column (channels)
    means[ampl_index][:] = np.mean(ampl_delta_matrix, axis=0)  
    means[phase_index][:] = np.mean(phase_delta_matrix, axis=0)  

    stds[freq_index][:] = np.std(freq_delta_matrix, axis=0)
    stds[ampl_index][:] = np.std(ampl_delta_matrix, axis=0)
    stds[phase_index][:] = np.std(phase_delta_matrix, axis=0)

    mins[freq_index][:] = np.min(freq_delta_matrix, axis=0)
    mins[ampl_index][:] = np.min(ampl_delta_matrix, axis=0)
    mins[phase_index][:] = np.min(phase_delta_matrix, axis=0)

    maxs[freq_index][:] = np.max(freq_delta_matrix, axis=0)
    maxs[ampl_index][:] = np.max(ampl_delta_matrix, axis=0)
    maxs[phase_index][:] = np.max(phase_delta_matrix, axis=0)

    # Increase the std_ratio if the number of iterations implies a substantially smaller std_deviation
    global std_ratio
    alt_std_ratio = math.sqrt(num_iter)
    if alt_std_ratio > std_ratio:
        print("Replacing old std_ratio (=" + str(std_ratio) + ") with updated str_ratio (="+ str(alt_std_ratio) + ") due to iteration count.")
        std_ratio = alt_std_ratio

    # Increase the std_ratio_phase if the number of iterations implies a substantially smaller std_deviation
    global std_ratio_phase
    alt_std_ratio = math.sqrt(num_iter)
    if alt_std_ratio > std_ratio_phase:
        print("Replacing old std_ratio_phase (=" + str(std_ratio) + ") with updated std_ratio_phase (="+ str(alt_std_ratio) + ") due to iteration count.")
        std_ratio_phase = alt_std_ratio

    # Basic test to check if signal is present on our baseline channel. 
    if wave_freq - (std_ratio * freq_std_thresh) < means[freq_index][0] < wave_freq + (std_ratio * freq_std_thresh):
        print("[ERROR][{}][{}]: Signal not detected on Ch{}".format(frameinfo.filename, frameinfo.lineno, targs.channels[0]))

    # Results arrays are structured as:
    # ch0 [baselinestd, min_res, max_res, std_res]
    # ...
    # chN [-1, min_res, max_res, std_res]
    # Note that baselinestd will only apply for ch0, for the rest of the channels this value will be -1
    baselineCh_std_index = 0
    min_index = 1
    max_index = 2
    delta_std_index = 3
    freq_res = np.full((4, len(targs.channels)), -1)
    ampl_res = np.full((4, len(targs.channels)), -1)
    phase_res = np.full((4, len(targs.channels)), -1)

    freq_res[baselineCh_index][baselineCh_std_index] = stds[freq_index][baselineCh_index] < freq_std_thresh
    freq_res[1:, min_index] = [value > -std_ratio * freq_std_thresh for value in mins[freq_index,1:]]
    freq_res[1:, max_index] = [value < std_ratio * freq_std_thresh for value in maxs[freq_index, 1:]]
    freq_res[1:, delta_std_index] = [value < freq_std_thresh for value in stds[freq_index, 1:]]

    ampl_res[baselineCh_index][baselineCh_std_index] = stds[ampl_index][baselineCh_index] < ampl_std_thresh
    ampl_res[1:, min_index] = [value > -std_ratio * ampl_std_thresh for value in mins[ampl_index, 1:]]
    ampl_res[1:, max_index] = [value < std_ratio * ampl_std_thresh for value in maxs[ampl_index, 1:]]
    ampl_res[1:, delta_std_index] = [value < ampl_std_thresh for value in stds[ampl_index, 1:]]

    phase_res[baselineCh_index][baselineCh_std_index] = stds[phase_index][baselineCh_index] < phase_std_thresh
    phase_res[1:, min_index] = [value > -std_ratio * phase_std_thresh for value in mins[phase_index, 1:]]
    phase_res[1:, max_index] = [value < std_ratio * phase_std_thresh for value in maxs[phase_index, 1:]]
    phase_res[1:, delta_std_index] = [value < phase_std_thresh for value in stds[phase_index, 1:]]

    makePlots()

    # Print results table to console
    overall_tests = out.Table("Overall Tests")
    overall_tests.addColumn("Test")
    overall_tests.addColumn("Status")
    overall_tests.addRow("Frequency", boolToWord(freq_res[baselineCh_index, baselineCh_std_index] and freq_res[1:, 1:].all()))   # Check baseline ch std and ch to ch tests (min, max, std)
    overall_tests.addRow("Amplitude", boolToWord(ampl_res[baselineCh_index, baselineCh_std_index] and ampl_res[1:, 1:].all()))
    overall_tests.addRow("Phase", boolToWord(phase_res[baselineCh_index, baselineCh_std_index] and phase_res[1:, 1:].all()))
    overall_tests.printData()

    # PDF Overall Table
    overall_table = [
        ["Test", "Status"],
        ["Frequency", boolToWord(freq_res[baselineCh_index, baselineCh_std_index] and freq_res[1:, 1:].all())],
        ["Amplitude", boolToWord(ampl_res[baselineCh_index, baselineCh_std_index] and ampl_res[1:, 1:].all())],
        ["Phase", boolToWord(phase_res[baselineCh_index, baselineCh_std_index] and phase_res[1:, 1:].all())]
        ]

    report.insert_text_large("Overall and Subtests Tables: ")
    report.insert_text(" ")
    report.insert_table(overall_table, 20, "Overall Tests")

    max_crit = "< baselineCh + " + str(std_ratio) + "*std"
    min_crit = "> baselineCh - " + str(std_ratio) + "*std"

    channel_list = channel_map[targs.channels].tolist()
    for ch in range(1, len(channel_list)):
        channel_list[ch] = "\u0394" + channel_list[ch] + channel_map[targs.channels[0]]

    # Result tables
    subtest_freq_table = np.zeros((4, len(targs.channels) + 2)).tolist()
    subtest_freq_table[:][0] = ["Test", "Min Value Outlier", "Max Value Outlier", "STD Deviation"]
    subtest_freq_table[:][1] = ["Criteria", ">" + min_crit, "<" + max_crit, "<" + str(freq_std_thresh)]
    subtest_freq_table[0][2:] = channel_list
    subtest_freq_table[min_index][2:] = [boolToWord(val) for val in freq_res[:][min_index]]
    subtest_freq_table[max_index][2:] = [boolToWord(val) for val in freq_res[:][max_index]]
    subtest_freq_table[delta_std_index][2:] = [boolToWord(val) for val in freq_res[:][delta_std_index]]

    subtest_ampl_table = np.zeros((4, len(targs.channels) + 2)).tolist()
    subtest_ampl_table[:][0] = ["Test", "Min Value Outlier", "Max Value Outlier", "STD Deviation"]
    subtest_ampl_table[:][1] = ["Criteria", ">" + min_crit, "<" + max_crit, "<" + str(freq_std_thresh)]
    subtest_ampl_table[0][2:] = channel_list
    subtest_ampl_table[min_index][2:] = [boolToWord(val) for val in ampl_res[:][min_index]]
    subtest_ampl_table[max_index][2:] = [boolToWord(val) for val in ampl_res[:][max_index]]
    subtest_ampl_table[delta_std_index][2:] = [boolToWord(val) for val in ampl_res[:][delta_std_index]]

    subtest_phase_table = np.zeros((4, len(targs.channels) + 2)).tolist()
    subtest_phase_table[:][0] = ["Test", "Min Value Outlier", "Max Value Outlier", "STD Deviation"]
    subtest_phase_table[:][1] = ["Criteria", ">" + min_crit, "<" + max_crit, "<" + str(freq_std_thresh)]
    subtest_phase_table[0][2:] = channel_list
    subtest_phase_table[min_index][2:] = [boolToWord(val) for val in phase_res[:][min_index]]
    subtest_phase_table[max_index][2:] = [boolToWord(val) for val in phase_res[:][max_index]]
    subtest_phase_table[delta_std_index][2:] = [boolToWord(val) for val in phase_res[:][delta_std_index]]

    # Data tables
    sum_freq_table = np.full((5, len(targs.channels) + 1), "").tolist()     # need to explicitly convert to list when working with strings (numpy uses its own str data type)
    sum_freq_table[:][0] = ["Run", "Mean", "Minimum", "Maximum", "STD Deviation"]
    sum_freq_table[0][1:] = channel_list
    sum_freq_table[1][1:] = means[freq_index][:]
    sum_freq_table[2][1:] = mins[freq_index][:]
    sum_freq_table[3][1:] = maxs[freq_index][:]
    sum_freq_table[4][1:] = stds[freq_index][:]
    for i in range(runs + 1):
        sum_freq_table.append(["Run " + str(i)] + freq_delta_matrix[i][:].tolist())

    sum_ampl_table = np.full((5, len(targs.channels) + 1), "").tolist()    
    sum_ampl_table[:][0] = ["Run", "Mean", "Minimum", "Maximum", "STD Deviation"]
    sum_ampl_table[0][1:] = channel_list
    sum_ampl_table[1][1:] = means[ampl_index][:]
    sum_ampl_table[2][1:] = mins[ampl_index][:]
    sum_ampl_table[3][1:] = maxs[ampl_index][:]
    sum_ampl_table[4][1:] = stds[ampl_index][:]
    for i in range(runs + 1):
        sum_ampl_table.append(["Run " + str(i)] + ampl_delta_matrix[i][:].tolist())

    sum_phase_table = np.full((5, len(targs.channels) + 1), "").tolist()    
    sum_phase_table[:][0] = ["Run", "Mean", "Minimum", "Maximum", "STD Deviation"]
    sum_phase_table[0][1:] = channel_list
    sum_phase_table[1][1:] = means[phase_index][:]
    sum_phase_table[2][1:] = mins[phase_index][:]
    sum_phase_table[3][1:] = maxs[phase_index][:]
    sum_phase_table[4][1:] = stds[phase_index][:]
    for i in range(runs + 1):
        sum_ampl_table.append(["Run " + str(i)] + phase_delta_matrix[i][:].tolist())

    dc_offset_table_pdf = ["Run"] + channel_list 
    for i in range(runs + 1):
        dc_offset_table_pdf.append(["Run " + str(i)] + offset_delta_matrix[i][:].tolist())

    # Summary PDF Table
    report.insert_table(subtest_freq_table, 20, "SubTest Results - Frequency Test")
    report.insert_text(" ")
    report.insert_table(subtest_ampl_table, 20, "SubTest Results - Amplitude Test")
    report.insert_text(" ")
    report.insert_table(subtest_phase_table, 20, "SubTest Results - Phase Test")

    report.new_page()
    report.insert_text_large("Summary Statistics: ")
    report.insert_text(" ")
    report.insert_text(" ")
    report.insert_table(sum_freq_table, -10, "Summary Frequency")
    report.insert_text(" ")
    report.insert_table(sum_ampl_table, -10, "Summary Amplitude")
    report.insert_text(" ")
    report.insert_table(sum_phase_table, -10, "Summary Phase")
    report.insert_text(" ")
    report.insert_table(dc_offset_table_pdf, -10, "DC Offsets")
    report.new_page()

    # get back outside to save
    os.chdir(parent_dir)
    # os.system("mkdir report_output")
    # os.chdir("report_output")
    report.draw_from_buffer()
    report.save()
    print("PDF report saved at " + report.get_filename())

    if (fail_flag == 1):
        sys.exit(1)

if __name__ == '__main__':
    main()