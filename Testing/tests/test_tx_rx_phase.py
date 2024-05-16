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
from datetime import datetime
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

#changing global variables - referenced in multiple functions
wave_freq = -1 #set later, when runs are called
runs = -1 #set later when runs are called
iteration_count = -1
sample_rate = -1
plotted_samples = -1
begin_cuttoff = -1
sample_count = -1

#Frequeny Checks
freq_mean_thresh = 5 #Hz bound
freq_std_thresh = 0.6

#Amplitude Checks
ampl_std_thresh = 0.001

#phase CHecks
phase_mean_thresh = 0.0349066 #rad bound
phase_std_thresh = 0.002

#SHOULD ALL PLOTS BE MADE?
            #Frequency , Ampl, Phase
plot_toggle = [True, True, True]
#Calling date and time for simplicity - NOTE: THIS WOULD BE HELPFUL IN MOST CODES, SHOULD WE MAKE FILE IN COMMON FOR IT??
now = datetime.now() #current date and time
iso_time = now.strftime("%Y%m%d%H%M%S.%f")

#Setting up directories for plots

parent_dir = os.getcwd()
leaf_dir = "dump/"
dump_dir = parent_dir + leaf_dir
dump_path = os.path.join("./", dump_dir)
os.makedirs(dump_path,exist_ok=True)

test_plots = dump_dir + iso_time + "-tx_rx_phase"
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

    f = open("Data_Plots.txt", "a")
    f.write("\n" + title + ": " + str(y[find_peaks(y)[0][0]]))
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

'''Does all the comparisons of the data with the givens
PARAMS: criteria, mean, std, mins, maxs
RETURNS: return_array'''
def check(criteria, mean, std, mins, maxs):
    return_array = []

    # #check individual means
    # if criteria[4]:
    #     if (mean < criteria[0] and mean > (-1*criteria[0])):
    #         return_array.append(True)
    #     else:
    #         return_array.append(False)
    # else: #if it's ampl it only checks greater than
    #     if (mean > criteria[0]):
    #         return_array.append(True)
    #     else:
    #         return_array.append(False)

    #check min
    if (mins >= criteria[1]):
        return_array.append(True)
    else:
        return_array.append(False)
    #check max
    if (maxs <= criteria[2]):
        return_array.append(True)
    else:
        return_array.append(False)

    #check std


    if (std < criteria[0]):
        return_array.append(True)
    else:
        return_array.append(False)

    return return_array

'''Makes the subtestTables and printst them to console
PARAMS: table, min_crit, max_crit, std_crit, boolean
RETURNS: NONE'''
def subtestTable(table, min_crit, max_crit, std_crit, boolean, bounds=True):

    table.addColumn("Test")
    table.addColumn("Criteria")
    table.addColumn("\u0394BA")
    table.addColumn("\u0394CA")
    table.addColumn("\u0394DA")

    #print(boolean)
    # if bounds:
    #     table.addRow("Mean Absolute Variant", ("\u00B1" + abs_crit), boolToWord(boolean[0][0]), boolToWord(boolean[1][0]), boolToWord(boolean[2][0]))
    # else:
    #     table.addRow("Mean Absolute Variant", (">" + abs_crit), boolToWord(boolean[0][0]), boolToWord(boolean[1][0]), boolToWord(boolean[2][0]))
    table.addRow("Min Value Outliers", (">" + min_crit), boolToWord(boolean[0][0]), boolToWord(boolean[1][0]), boolToWord(boolean[2][0]))
    table.addRow("Max Value Outiers", ("<" + max_crit), boolToWord(boolean[0][1]), boolToWord(boolean[1][1]), boolToWord(boolean[2][1]))
    table.addRow("STD Deviation", ("<" + std_crit), boolToWord(boolean[0][2]), boolToWord(boolean[1][2]), boolToWord(boolean[2][2]))

    table.printData()

'''Makes summary table and prints to console
PARAMS: run_all, table, mean, minimum, maximum, std, data
RETURNS: NONE'''

def summaryTable(run_all, abs_bool, table, mean, minimum, maximum, std, data):
    table.addColumn("Run") #TODO: find better name for this lol
    table.addColumn("Baseline A")
    table.addColumn("\u0394BA")
    table.addColumn("\u0394CA")
    table.addColumn("\u0394DA")

    table.addRow("Mean", str(mean[0]), str(mean[1]), str(mean[2]), str(mean[3]))
    table.addRow("Minimum", str(minimum[0]), str(minimum[1]), str(minimum[2]), str(minimum[3]))
    table.addRow("Maximum", str(maximum[0]), str(maximum[1]), str(maximum[2]), str(maximum[3]))
    table.addRow("STD Deviations", str(std[0]), str(std[1]), str(std[2]), str(std[3]))

    if not run_all or abs_bool > 0:
        for i in range(runs + 1):
            table.addRow(str(i), str(data[0][i]), str(data[1][i]), str(data[2][i]), str(data[3][i]))

    table.printData()

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
    p = argparse.ArgumentParser(description = "Loopback phase coherency test")
    p.add_argument('-r', '--rate', default=25000000, type=int, help="Sample rate in samples per second")
    p.add_argument('-b', '--band', default=False, type=bool, help="Apply a band pass filter to the data")
    # Add generic test arguments
    targs = test_args.TestArgs(parser=p, testDesc="Loopback phase coherency test")

    args = p.parse_args()

    # PDF Report
    global report
    report = pdf_report.ClassicShipTestReport("tx_rx_phase", targs.serial, targs.report_dir, targs.docker_sha)
    report.insert_title_page("Low Band TX RX Phase Coherency Test")

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
        vsnk = engine.run(it["channels"], it["wave_freq"], sample_rate, it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)

        if (table_printed_once == 0):
            table_data = [["Center Frequency (Hz)", "Wave Frequency (Hz)", "Sample Rate (SPS)", "Sample Count", "TX Gain (dB)", "RX Gain (dB)"],
                            [it["center_freq"], it["wave_freq"], sample_rate, it["sample_count"], it["tx_gain"], it["rx_gain"]]]
            report.buffer_put("table_wide", table_data, "Test Configuration")
            # report.insert_table(table_data, 0 , "Test Configuration")
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

            # Explicitly assigning the relevant slice of data to a variable, then passing said variable to bestFit
            # Creating a slice anonymously may cause a crash where somehow data collected the the engine wasn't making it to bestFit
            trimmed_real = real[begin_cutoff:]

            real_hold.append(trimmed_real)

            best_fit, param = bestFit(x_time, trimmed_real)

            real_hold.append(real[begin_cutoff:])

            best_fit, param = bestFit(x_time, real[begin_cutoff:])

            ampl.append(param[0])
            freq.append(param[1])
            phase.append(param[2])
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


    #STARTING THE CHECKS
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

    #Increase the std_ratio if the number of iterations implies a substantially
    #smaller std_deviation
    global std_ratio
    alt_std_ratio = math.sqrt(num_iter)
    if alt_std_ratio > std_ratio:
        print("Replacing old std_ratio (=" + str(std_ratio) + ") with updated str_ratio (="+ str(alt_std_ratio) + ")due to iteration count.")
        std_ratio = alt_std_ratio

    #Calculating the Criteria
    #2D array holding thresholds of: mean, std, min, max
    criteria = [] #[Test][crit]ls
    #Frequency
    freq_criteria = []
    for ch in range(1, 4): #starting at 1 because index 0 is A baseline
        freq_criteria.append((freq_std_thresh, (means[0][ch] - (std_ratio*stds[0][ch])), (means[0][ch] + (std_ratio*stds[0][ch])), True))
    criteria.append(freq_criteria) #Formatting

    #Amplitude
    ampl_criteria = []
    for ch in range(1, 4): #starting at 1 because index 0 is A baseline
        ampl_criteria.append((ampl_std_thresh, (means[1][ch] - (std_ratio*stds[1][ch])), (means[1][ch] + (std_ratio*stds[1][ch])), False)) #final variable toggles the boundaries
    criteria.append(ampl_criteria)
    # print(ampl_criteria)
    #phase
    phase_criteria = []
    for ch in range(1, 4): #starting at 1 because index 0 is A baseline
        phase_criteria.append((phase_std_thresh, (means[2][ch] - (std_ratio*stds[2][ch])), (means[2][ch] + (std_ratio*stds[2][ch])), True))
    criteria.append(phase_criteria)

    #Absolute checks (from baseline)
    abs_bool = [False, False, False] #if the summary tables will fully print
    try:
        means[0][0] < wave_freq + (stds[0][0]*std_ratio)
        means[0][0] > wave_freq - (stds[0][0]*std_ratio)
        print("Mean of the Wave Frequency mean is within \u00B1" + str(std_ratio) +" * std bounds of " + str(wave_freq))
    except:
        print("The Wave Frequency mean failed to be within \u00B1" + str(std_ratio) +" * std bounds of " + str(wave_freq))
        abs_bool[0] = True

    try:
        means[1][0] > std_ratio*stds[1][0]
        print("Signal present on Ch A (Amplitude greater than " + str(std_ratio) +" * std)" )
    except:
        print("Signal possibly absent (Amplitude is less than " + str(std_ratio) +" * std)" )
        abs_bool[1] = True

    try:
        mins[2][0] > ( means[2][0] - (std_ratio*std[2][0]) )
        maxs[2][0] < ( means[2][0] + (std_ratio*std[2][0]) )
    except:
        print("The Phase failed to be within \u00B1" + str(std_ratio) +" * std")
        abs_bool[2] = True

    #doing the checks for the differnces, setting up subtest booleans
    subtest_bool = [] #[test][channel diff][pass/fail]
    for test in range(len(criteria)):
        temp_hold = []
        for ch in range(len(criteria[test])): #columns, account for the extra baseline
            temp_hold.append((check(criteria[test][ch], means[test][ch+1], stds[test][ch+1], mins[test][ch+1], maxs[test][ch+1])))
        subtest_bool.append((temp_hold))

    #print(subtest_bool)

    fail_flag = 0

    #Overall Tests boolean
    overall_bool = [True, True, True]
    for test in range(len(criteria)):
        if np.prod(subtest_bool[test]) == 0: #If list contains and 0
            overall_bool[test] =  False
            fail_flag = 1

    # Check run-to-run phase coherency for channel A only.
    # If the STD exceeds threshold, then it's likely that channel A has non-uniform start time.
    if (stds[2][0] < phase_std_thresh):
        overall_bool.append(True)
    else:
        overall_bool.append(False)
        fail_flag = 1

    #Checking if plots should print
    if (np.prod(overall_bool) == 0 or plot_toggle or np.prod(abs_bool) == 0):
        makePlots()

    #Outputting tables
    #Output tables and their flags- This allows me to always reference them - no matter the iteration
    overall_tests = out.Table("Overall Tests")
    overall_tests.addColumn("Test")
    overall_tests.addColumn("Status")
    overall_tests.addRow("Frequency", boolToWord(overall_bool[0]))
    overall_tests.addRow("Amplitude", boolToWord(overall_bool[1]))
    overall_tests.addRow("Phase", boolToWord(overall_bool[2]))
    overall_tests.addRow("Run-Run Phase", boolToWord(overall_bool[3]))
    overall_tests.printData()

    # PDF Overall Table
    overall_table = [
        ["Test", "Status"],
        ["Frequency", boolToWord(overall_bool[0])],
        ["Amplitude", boolToWord(overall_bool[1])],
        ["Phase", boolToWord(overall_bool[2])],
        ["Run-to-Run Phase Consistency", boolToWord(overall_bool[3])]
        ]

    # report.new_page()
    report.insert_text_large("Overall and Subtests Tables: ")
    report.insert_text(" ")
    report.insert_table(overall_table, 20, "Overall Tests")

    #Outputting the subtests
    max_crit = "< mean + " + str(std_ratio) + "*std"
    min_crit = "> mean - " + str(std_ratio) + "*std"

    #Print subtables of failed overall tests and make their plots
    if not overall_bool[0]:
        st_freq  = out.Table(title="SubTest Results - Frequency Tests")
        subtestTable(st_freq, min_crit, max_crit, str(freq_std_thresh), subtest_bool[0])
    if not overall_bool[1]:
        st_ampl  = out.Table(title="SubTest Results - Amplitude Tests")
        subtestTable(st_ampl, min_crit, max_crit, str(ampl_std_thresh), subtest_bool[1], bounds=False)
    if (not overall_bool[2]) or (not overall_bool[3]):
        st_phase = out.Table(title="SubTest Results - Phase Tests")
        subtestTable(st_phase, min_crit, max_crit, str(phase_std_thresh), subtest_bool[2])

    # PDF Subtest Table
    subtest_freq_table = [
        ["Test", "Criteria", "\u0394BA", "\u0394CA", "\u0394DA"],
        ["Min Value Outliers", (">" + min_crit), boolToWord(subtest_bool[0][0][0]), boolToWord(subtest_bool[0][1][0]), boolToWord(subtest_bool[0][2][0])],
        ["Max Value Outliers", ("<" + max_crit), boolToWord(subtest_bool[0][0][1]), boolToWord(subtest_bool[0][1][1]), boolToWord(subtest_bool[0][2][1])],
        ["STD Deviation", ("<" + str(freq_std_thresh)), boolToWord(subtest_bool[0][0][2]), boolToWord(subtest_bool[0][1][2]), boolToWord(subtest_bool[0][2][2])]
    ]
    subtest_ampl_table = [
        ["Test", "Criteria", "\u0394BA", "\u0394CA", "\u0394DA"],
        ["Min Value Outliers", (">" + min_crit), boolToWord(subtest_bool[1][0][0]), boolToWord(subtest_bool[1][1][0]), boolToWord(subtest_bool[1][2][0])],
        ["Max Value Outliers", ("<" + max_crit), boolToWord(subtest_bool[1][0][1]), boolToWord(subtest_bool[1][1][1]), boolToWord(subtest_bool[1][2][1])],
        ["STD Deviation", ("<" + str(ampl_std_thresh)), boolToWord(subtest_bool[1][0][2]), boolToWord(subtest_bool[1][1][2]), boolToWord(subtest_bool[1][2][2])]
    ]
    subtest_phase_table = [
        ["Test", "Criteria", "\u0394BA", "\u0394CA", "\u0394DA"],
        ["Min Value Outliers", (">" + min_crit), boolToWord(subtest_bool[2][0][0]), boolToWord(subtest_bool[2][1][0]), boolToWord(subtest_bool[2][2][0])],
        ["Max Value Outliers", ("<" + max_crit), boolToWord(subtest_bool[2][0][1]), boolToWord(subtest_bool[2][1][1]), boolToWord(subtest_bool[2][2][1])],
        ["STD Deviation", ("<" + str(phase_std_thresh)), boolToWord(subtest_bool[2][0][2]), boolToWord(subtest_bool[2][1][2]), boolToWord(subtest_bool[2][2][2])]
    ]

    subtest_phase_consistency = [
        ["Test", "Criteria", "Ch A."],
        ["Run-to-Run Phase Consistency", ("std <" + str(phase_std_thresh)), boolToWord(overall_bool[3]) ]
    ]

    #Summary Statistics
    sum_freq  = out.Table(title="Summary Frequency")
    summaryTable(overall_bool[0], abs_bool[0], sum_freq, means[0], mins[0], maxs[0], stds[0], data[0])

    sum_ampl  = out.Table(title="Summary Amplitude")
    summaryTable(overall_bool[1], abs_bool[1], sum_ampl, means[1], mins[1], maxs[1], stds[1], data[1])

    sum_phase  = out.Table(title="Summary Phase")
    summaryTable(overall_bool[2], abs_bool[2], sum_phase, means[2], mins[2], maxs[2], stds[2], data[2])

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

    #DC Offset Table
    dc_offset_table = out.Table(title="DC Offsets")
    dc_offset_table.addColumn("Run")
    dc_offset_table.addColumn("\u0394BA")
    dc_offset_table.addColumn("\u0394CA")
    dc_offset_table.addColumn("\u0394DA")
    for i in range(len(offsets)):
        dc_offset_table.addRow(str(i), str(offsets[i][0]), str(offsets[i][1]), str(offsets[i][2]), str(offsets[i][3]))
    dc_offset_table.printData()

    # Summary PDF Table
    report.insert_table(subtest_freq_table, 20, "SubTest Results - Frequency Test")
    report.insert_text(" ")
    report.insert_table(subtest_ampl_table, 20, "SubTest Results - Amplitude Test")
    report.insert_text(" ")
    report.insert_table(subtest_phase_table, 20, "SubTest Results - Phase Test")
    report.insert_text(" ")
    report.insert_table(subtest_phase_consistency, 20, "SubTest Results - Run-to-Run Phase Consistency Test")

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

# main(gen.lo_band_phaseCoherency_short(4))
if __name__ == '__main__':
    main()
