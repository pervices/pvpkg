from common import sigproc
from common import engine
from common import generator as gen
from common import pdf_report
from common import test_args

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import stats
import math

from common import outputs as out
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import norm
from scipy.signal import find_peaks
from scipy import signal
import sys
import os
from datetime import datetime
import time
from math import pi

import argparse

#USER CHOSEN VALUES
num_channel = 4 #dependent on unit
num_output_waves =1 #depends what plots look like
begin_cutoff_waves = 1 #0.00000425 #e(-5) - guessed from previous diagrams (but seconds)
tx_burst = 5.0 #burst should be slightly delayed to ensure all data is being collected
rx_burst = 5.25

std_ratio = 4  #number std gets multiplied by for checks, normalized to a sample size of 10
               #This value is adjusted later depending on the number of runs.

std_ratio_phase = 8  #number std gets multiplied by for checks, normalized to a sample size of 10
                     #This value is adjusted later depending on the number of runs.

#changing global variables - referenced in multiple functions
wave_freq = -1 #set later, when runs are called
runs = -1 #set later when runs are called
iteration_count = -1
sample_rate = -1
plotted_samples = -1
sample_count = -1

freq_alignment_thresh = 10      # Hz
ampl_alignment_thresh = 0.1
phase_alignment_thresh = 0.1    # rad

#SHOULD ALL PLOTS BE MADE?
            #Frequency , Ampl, Phase
plot_toggle = [True, True, True]
#Calling date and time for simplicity - NOTE: THIS WOULD BE HELPFUL IN MOST CODES, SHOULD WE MAKE FILE IN COMMON FOR IT??
now = datetime.now()
iso_time = now.strftime("%Y%m%d%H%M%S.%f")

#Setting up directories for plots
parent_dir = os.getcwd()
leaf_dir = "dump/"
dump_dir = parent_dir + leaf_dir
dump_path = os.path.join("./", dump_dir)
os.makedirs(dump_path,exist_ok=True)

test_plots = dump_dir + iso_time + "-channel_alignment"
os.makedirs(test_plots, exist_ok = True)

#important variables
data = [] #This will hold all output information
reals = []
best_fits = []
x_time = []
offsets = []

'''
Represents the wave equation
PARAMS: time, ampl, freq, phase
RETUNRS: y'''
def waveEquation(time, ampl, freq, phase, dc_offset):

    y = ampl*np.cos((2*np.pi*freq*time + phase)) + dc_offset #model for wave equation
    return y

'''Plots the subplots all in the same format
PARAMS: x, y, ax, best_fit, title
RETURNS: NONE'''

def subPlot(x, y, ax, best_fit, offset, title):
    ax.set_title(title)
    ax.set_xlabel("Time")
    ax.set_ylabel("Amplitude")
    ax.set_ylim(-0.475, 0.475)
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


'''Creates the line of best fit for the given x and y
PARAMS: x,y
RETURNS: best_fit (y values of the line of best fit '''
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

    #reals
    for z in range(runs+1):
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2)
        plt.suptitle("Amplitude versus Samples: Individual Channels for Run {}".format(z))
        shift = z*num_channel

        os.chdir(test_plots) #To save to a filels

        subPlot(x_time[0:plotted_samples], reals[z][0][0:plotted_samples], ax1, best_fits[z][0][0:plotted_samples], offsets[z][0], "Channel A")
        subPlot(x_time[0:plotted_samples], reals[z][1][0:plotted_samples], ax2, best_fits[z][1][0:plotted_samples], offsets[z][1], "Channel B")
        subPlot(x_time[0:plotted_samples], reals[z][2][0:plotted_samples], ax3, best_fits[z][2][0:plotted_samples], offsets[z][2], "Channel C")
        subPlot(x_time[0:plotted_samples], reals[z][3][0:plotted_samples], ax4, best_fits[z][3][0:plotted_samples], offsets[z][3], "Channel D")
        plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0) #Formatting the plots nicely

        # plt.show()
        os.chdir(test_plots)
        fig.savefig(("run{}_indiv".format(z) + ".svg"))
        s1 = report.get_image_io_stream()
        fig.savefig(s1, format="png", dpi=300)
        img1 = report.get_image_from_io_stream(s1)
        plt.clf()


        #Layout of the combined plot -- NOTE: ONLY CONTAINS LINE OF BEST FIT, could i some how use the previous answers as guesses, avg
        fig = plt.figure("Amplitude vs Time All Channels")
        plt.title("Amplitude versus Samples: All Channels for Run {}".format(z))
        plt.xlabel("Time")
        plt.ylabel("Amplitude")
        plt.ylim(-0.475, 0.475)

        #dots
        plt.plot(x_time[0:plotted_samples], reals[z][0][0:plotted_samples], '.', markersize=3,  color='lightcoral', label='Real A')
        plt.plot(x_time[0:plotted_samples], reals[z][1][0:plotted_samples], '.', markersize=3, color='coral', label='Real B')
        plt.plot(x_time[0:plotted_samples], reals[z][2][0:plotted_samples], '.', markersize=3, color='lightgreen', label='Real C')
        plt.plot(x_time[0:plotted_samples], reals[z][3][0:plotted_samples], '.', markersize=3, color='paleturquoise', label='Real D')

        #Best fits
        plt.plot(x_time[0:plotted_samples], best_fits[z][0][0:plotted_samples], '-', color='red', linewidth= 0.75, label='Best Fit A')
        plt.plot(x_time[0:plotted_samples], best_fits[z][1][0:plotted_samples], '-', color='darkorange', linewidth= 0.75, label='Best Fit B')
        plt.plot(x_time[0:plotted_samples], best_fits[z][2][0:plotted_samples], '-', color='limegreen', linewidth= 0.75, label='Best Fit C')
        plt.plot(x_time[0:plotted_samples], best_fits[z][3][0:plotted_samples], '-', color='darkslategrey', linewidth= 0.75, label='Best Fit D')
        plt.legend()

        #plt.show()
        fig.savefig(("run{}_together".format(z) + ".svg"))
        s2 = report.get_image_io_stream()
        fig.savefig(s2, format="png", dpi=300)
        img2 = report.get_image_from_io_stream(s2)

        report.buffer_put("image_double", [img1, img2], "Run " + str(z))
        print("Run figure has been put in buffer")
        plt.clf()

'''Turns the boolean into pass/fail NOTE: NOT SURE IF I NEED THIS
PARAM: Word
RETURNS: Pass or Fail'''
def boolToWord(word):
    if word:
        return("Pass")
    else:
        return("Fail")

'''Sets up output data, sets up test (and connecting to unit), sets up plots
PARAMS: iterations
RETURNS: <on console>'''
def main():
    # Add test specific arguments
    p = argparse.ArgumentParser(description = "Loopback channel alignment test")
    p.add_argument('-r', '--rate', default=25000000, type=int, help="Sample rate in samples per second")
    p.add_argument('-b', '--band', default=False, type=bool, help="Apply a band pass filter to the data")
    # Add generic test arguments
    targs = test_args.TestArgs(parser=p, testDesc="Loopback channel alignment test")

    args = p.parse_args()

    # PDF Report
    global report
    report = pdf_report.ClassicShipTestReport("channel_alignment", targs.serial, targs.report_dir, targs.docker_sha)
    report.insert_title_page("Low Band TX RX Channel Alignment Test")

    print("Title page generated")
    '''This iteration loop will run through setting up the channels to the values associated to the generator code. It will also loop through
    each channel and save the information to temp arrays. These temp arrays allow us to format our data into 2D arrays, so it's easier to
    reference later'''
    freq_A = []
    freq_AB_diff = []
    freq_AC_diff = []
    freq_AD_diff = []
    ampl_A = []
    ampl_AB_diff = []
    ampl_AC_diff = []
    ampl_AD_diff = []
    phase_A = []
    phase_AB_diff = []
    phase_AC_diff = []
    phase_AD_diff = []

    table_printed_once = 0

    if(targs.product == 'Vaunt'):
        iterations = gen.lo_band_phaseCoherency_short(4)
    else:
        iterations = gen.cyan.lo_band.phaseCoherency_short(4)

    num_iter = 0

    for it in iterations:

        num_iter = num_iter + 1
        gen.dump(it) #pulling info from generator
        #connecting and setting up the uniti
        '''Note how each step of time is equiv to 1/sample_rate
        When you reach sample_rate/sample_rate, one second has passed.
        TX: Below, we will be sending oiut samples equiv. to sample_rate after 10 seconds, so this will end at 11 secondi
        RX: Calculate the oversampling rate to find the number of samples to intake that match your ideal (sample count)'''
        global sample_rate
        sample_rate = args.rate
        tx_stack = [ (tx_burst , sample_rate)]
        rx_stack = [ (rx_burst, int(it["sample_count"]))]
        #this is the code that will actually tell the unit what values to run at
        try:
            vsnk = engine.run(it["channels"], it["wave_freq"], sample_rate, it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
        except Exception as err:
            report.draw_from_buffer()
            report.save()
            sys.exit(1)

        if (table_printed_once == 0):
            table_data = [["Center Frequency (Hz)", "Wave Frequency (Hz)", "Sample Rate (SPS)", "Sample Count", "TX Gain (dB)", "RX Gain (dB)"],
                            [it["center_freq"], it["wave_freq"], sample_rate, it["sample_count"], it["tx_gain"], it["rx_gain"]]]
            report.buffer_put("table_wide", table_data, "Test Configuration")
            table_printed_once = 1

        #Other important variables that require connection to the unit
        global sample_count
        sample_count = int(it["sample_count"])
        global runs
        runs = it["i"] #equal sign because we only care about the last value
        global wave_freq
        wave_freq = int(it["wave_freq"])

        #Making this start after specified number of waves have passed
        global begin_cutoff_waves
        begin_cutoff = int(round((1/(wave_freq/sample_rate))*begin_cutoff_waves))

        #Making the time array, starting at the cut off
        global x_time
        x_time = np.linspace(begin_cutoff/sample_rate, sample_count/sample_rate, num=sample_count-begin_cutoff)

        ampl = []
        freq = []
        phase = []
        offset = []
        best = []
        real_hold = []

        #Clearing, so the appended values after this loop are only related to the latest channels
        ampl.clear()
        freq.clear()
        phase.clear()
        offset.clear()
        best.clear()
        real_hold.clear()

        for ch, channel in enumerate(vsnk): #Goes through each channel to sve data

            real = [datum.real for datum in channel.data()] # saves data of real data in an array

            if len(real) == 0:
                raise Exception ("No data received on rx")
            elif len(real) <= begin_cutoff:
                raise Exception ("Rx received less data than cutoff. Received: " + str(len(real)) + " required more than " + str(begin_cutoff))


            # Filter data so we only see the phase of the intended signal if requested by user
            if args.band:
                b,a = signal.bessel(1, [wave_freq * 0.9, wave_freq * 1.1], 'bandpass', analog=False, norm='delay', fs = sample_rate)
                real = signal.filtfilt(b, a, real, padtype=None)

                if len(real) <= begin_cutoff:
                    raise Exception ("Filter error, rx data lost")

            # Explicitly assigning the relevant slice of data to a variable, then passing said variable to bestFit
            # Creating a slice anonymously may cause a crash where somehow data collected the the engine wasn't making it to bestFit
            trimmed_real = real[begin_cutoff:]

            real_hold.append(trimmed_real)

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
        reals.append(real_hold)
        best_fits.append(best)
        offsets.append(offset)
        freq_A.append(freq[0])
        freq_AB_diff.append(freq[1]-freq[0])
        freq_AC_diff.append(freq[2]-freq[0])
        freq_AD_diff.append(freq[3]-freq[0])
        ampl_A.append(ampl[0])
        ampl_AB_diff.append(ampl[1]-ampl[0])
        ampl_AC_diff.append(ampl[2]-ampl[0])
        ampl_AD_diff.append(ampl[3]-ampl[0])
        phase_A.append(phase[0])
        phase_AB_diff.append(phase[1]-phase[0])
        phase_AC_diff.append(phase[2]-phase[0])
        phase_AD_diff.append(phase[3]-phase[0])

    #Formatting into easily referencable 3D array
    data.append((freq_A, freq_AB_diff, freq_AC_diff, freq_AD_diff))
    data.append((ampl_A, ampl_AB_diff, ampl_AC_diff, ampl_AD_diff))
    data.append((phase_A, phase_AB_diff, phase_AC_diff, phase_AD_diff))


    #2D arrays containting summary values
    means = [] #[test (with base)][ch]
    stds = []
    mins = []
    maxs = []
    for test in range(len(data)): #freq, ampl, phase
        mean_temp = []
        std_temp = []
        mins_temp = []
        maxs_temp = []
        for ch in range(num_channel): #column of chart
            mean_temp.append(np.mean(data[test][ch]))
            std_temp.append(np.std(data[test][ch]))
            mins_temp.append(min(data[test][ch]))
            maxs_temp.append(max(data[test][ch]))
        means.append(mean_temp) #for formatting reasonss
        stds.append(std_temp)
        mins.append(mins_temp)
        maxs.append(maxs_temp)


    # Note 3 separate for loops are not the most efficient, but better for code readability for future maintenance
    test_fail = 0
    ch_frequency_results = ["Pass", "Pass", "Pass"]
    ch_ampl_results = ["Pass", "Pass", "Pass"]
    ch_phase_results = ["Pass", "Pass", "Pass"]

    for ch in range(1, num_channel):
        if abs(maxs[0][ch]) > freq_alignment_thresh or abs(mins[0][ch]) > freq_alignment_thresh:
            test_fail = 1
            ch_frequency_results[ch - 1] = "Fail"

    for ch in range(1, num_channel):
        if abs(maxs[1][ch]) > ampl_alignment_thresh or abs(mins[1][ch]) > ampl_alignment_thresh:
            test_fail = 1
            ch_ampl_results[ch - 1] = "Fail"

    for ch in range(1, num_channel):
        if abs(maxs[2][ch]) > phase_alignment_thresh or abs(mins[2][ch]) > phase_alignment_thresh:
            test_fail = 1
            ch_phase_results[ch - 1] = "Fail"

    makePlots()

    overall_tests = out.Table("Overall Tests")
    overall_tests.addColumn("Test")
    overall_tests.addColumn("Status")
    overall_tests.addRow("Frequency Alignment", boolToWord(not ("Fail" in ch_frequency_results)))
    overall_tests.addRow("Amplitude Alignment", boolToWord(not ("Fail" in ch_ampl_results)))
    overall_tests.addRow("Phase Alignment", boolToWord(not ("Fail" in ch_phase_results)))
    overall_tests.printData()

    # PDF Overall Table
    overall_table = [
        ["Test", "Status"],
        ["Frequency Alignment", boolToWord(not ("Fail" in ch_frequency_results))],
        ["Amplitude Alignment", boolToWord(not ("Fail" in ch_ampl_results))],
        ["Phase Alignment", boolToWord(not ("Fail" in ch_phase_results))]
        ]

    # report.new_page()
    report.insert_text_large("Overall and Subtests Tables: ")
    report.insert_text(" ")
    report.insert_table(overall_table, 20, "Overall Tests")

    # PDF Subtest Table
    subtest_freq_table = [
        ["Test", "Criteria", "\u0394BA", "\u0394CA", "\u0394DA"],
        ["Frequency Alignment", ("|\u0394| < " + str(freq_alignment_thresh)), ch_frequency_results[0], ch_frequency_results[1], ch_frequency_results[2]]
    ]
    subtest_ampl_table = [
        ["Test", "Criteria", "\u0394BA", "\u0394CA", "\u0394DA"],
        ["Amplitude Alignment", ("|\u0394| < " + str(ampl_alignment_thresh)), ch_ampl_results[0], ch_ampl_results[1], ch_ampl_results[2]]
    ]
    subtest_phase_table = [
        ["Test", "Criteria", "\u0394BA", "\u0394CA", "\u0394DA"],
        ["Phase Alignment", ("|\u0394| < " + str(phase_alignment_thresh)), ch_phase_results[0], ch_phase_results[1], ch_phase_results[2]]
    ]

    #Summary Statistics
    sum_freq_table = [
        ["Run", "Baseline A", "\u0394BA", "\u0394CA", "\u0394DA"],
        ["Mean", str(means[0][0]), str(means[0][1]), str(means[0][2]), str(means[0][3])],
        ["Minimum", str(mins[0][0]), str(mins[0][1]), str(mins[0][2]), str(mins[0][3])],
        ["Maximum", str(maxs[0][0]), str(maxs[0][1]), str(maxs[0][2]), str(maxs[0][3])],
        ["STD Deviations", str(stds[0][0]), str(stds[0][1]), str(stds[0][2]), str(stds[0][3])]
    ]
    for i in range(runs + 1):
        sum_freq_table.append(["Run " + str(i), str(data[0][0][i]), str(data[0][1][i]), str(data[0][2][i]), str(data[0][3][i])])

    sum_ampl_table = [
        ["Run", "Baseline A", "\u0394BA", "\u0394CA", "\u0394DA"],
        ["Mean", str(means[1][0]), str(means[1][1]), str(means[1][2]), str(means[1][3])],
        ["Minimum", str(mins[1][0]), str(mins[1][1]), str(mins[1][2]), str(mins[1][3])],
        ["Maximum", str(maxs[1][0]), str(maxs[1][1]), str(maxs[1][2]), str(maxs[1][3])],
        ["STD Deviations", str(stds[1][0]), str(stds[1][1]), str(stds[1][2]), str(stds[1][3])]
    ]
    for i in range(runs + 1):
        sum_ampl_table.append(["Run " + str(i), str(data[1][0][i]), str(data[1][1][i]), str(data[1][2][i]), str(data[1][3][i])])

    sum_phase_table = [
        ["Run", "Baseline A", "\u0394BA", "\u0394CA", "\u0394DA"],
        ["Mean", str(means[2][0]), str(means[2][1]), str(means[2][2]), str(means[2][3])],
        ["Minimum", str(mins[2][0]), str(mins[2][1]), str(mins[2][2]), str(mins[2][3])],
        ["Maximum", str(maxs[2][0]), str(maxs[2][1]), str(maxs[2][2]), str(maxs[2][3])],
        ["STD Deviations", str(stds[2][0]), str(stds[2][1]), str(stds[2][2]), str(stds[2][3])]
    ]
    for i in range(runs + 1):
        sum_phase_table.append(["Run " + str(i), str(data[2][0][i]), str(data[2][1][i]), str(data[2][2][i]), str(data[2][3][i])])

    dc_offset_table_pdf = [
        ["Run", "\u0394BA", "\u0394CA", "\u0394DA"],
    ]
    for i in range(len(offsets)):
        dc_offset_table_pdf.append(["Run " + str(i), str(offsets[i][0]), str(offsets[i][1]), str(offsets[i][2]), str(offsets[i][3])])

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

    sys.exit(test_fail)

# main(gen.lo_band_phaseCoherency_short(4))
if __name__ == '__main__':
    main()
