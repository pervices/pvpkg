from common import sigproc
from common import engine
from common import generator as gen
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from rich.console import Console
from rich.table import Table
from rich.text import Text
import sys
import os
import time, datetime

#SHOULD ALL PLOTS BE MADE?
plot_toggle = False

#Calling date and time for simplicity - NOTE: THIS WOULD BE HELPFUL IN MOST CODES, SHOULD WE MAKE FILE IN COMMON FOR IT??
date = datetime.datetime.now()
formattedDate = date.isoformat()
#Formatting the foldernames to be scriptable
formattedDate = formattedDate.replace('-','')
formattedDate = formattedDate.replace(':','')

#Setting up directories for plots
con = Console()
current_dir = os.getcwd()
phase_plot_dir = current_dir + "/phase_coherency_fails"
test_plots = phase_plot_dir + "/" + formattedDate

os.makedirs(phase_plot_dir, exist_ok = True)
os.makedirs(test_plots, exist_ok = True)

#Hard coded values - changing dependent on user
num_channel = 4

#changing global variables - referenced in multiple functions
wave_freq = -1 #set later, when runs are called
runs = -1 #set later when runs are called
iteration_count = -1

#important variables
data = [] #This will hold all output information
reals = []
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
def subPlot(x, y, ax, best_fit, title):

    ax.set_title(title)
    ax.set_xlabel("Time")
    ax.set_ylabel("Amplitude")
    ax.plot(x, y, 'o', color='magenta', label='Real')
    ax.plot(x, best_fit[0], '-', color='black', label='Best Fit')
    ax.axhline(y = best_fit[1], color='green', label='DC Offset')
    ax.legend()


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
    best_fit = waveEquation(x, fit_amp, fit_freq, fit_phase, 0) #making the line of best fit
    
    return (best_fit, fit_offset), (fit_amp, fit_freq, fit_phase) #returns other values as tuple, so they can be easily referenced

'''Does all the comparisons of the data with the givens
PARAMS: criteria, mean, std, mins, maxs
RETURNS: return_array'''
def check(criteria, mean, std, mins, maxs):
    return_array = []
    #check mean
    if (mean < criteria[0] and mean > (-1*criteria[0])): #NOTE: CHECK IF AMPLITUDE NEEDS TO BE A THRESDHOLD - IS OK TO CHECK AS THRESH
        return_array.append(True)
    else:
        return_array.append(False)

    #check min
    if (mins >= criteria[2]):
                return_array.append(True)
    else:
        return_array.append(False)

    #check max
    if (maxs <= criteria[3]):
        return_array.append(True)
    else:
        return_array.append(False)

    #check std
    if (std < criteria[1]):
        return_array.append(True)
    else:
        return_array.append(False)

    return return_array

'''Makes the subtestTables and printst them to console
PARAMS: table, abs_crit, min_crit, max_crit, std_crit, boolean
RETURNS: NONE'''
def subtestTable(table, abs_crit, min_crit, max_crit, std_crit, boolean):

    table.add_column("Test")
    table.add_column("Criteria")
    table.add_column("\u0394BA")
    table.add_column("\u0394CA")
    table.add_column("\u0394DA")

    table.add_row("Mean Absolute Variant", ("\u00B1" + abs_crit), boolToWord(boolean[0][0]), boolToWord(boolean[1][0]), boolToWord(boolean[2][0]))
    table.add_row("Min Value Outliers", (">" + min_crit), boolToWord(boolean[0][1]), boolToWord(boolean[1][1]), boolToWord(boolean[2][1]))
    table.add_row("Max Value Outiers", ("<" + max_crit), boolToWord(boolean[0][2]), boolToWord(boolean[1][2]), boolToWord(boolean[2][2]))
    table.add_row("STD Deviation", ("<" + std_crit), boolToWord(boolean[0][3]), boolToWord(boolean[1][3]), boolToWord(boolean[2][3]))

    con.print(table)

'''Makes summary table and prints to console
PARAMS: run_all, table, mean, minimum, maximum, std, data
RETURNS: NONE'''
def summaryTable(run_all, table, mean, minimum, maximum, std, data):
    table.add_column("Run") #TODO: find better name for this lol
    table.add_column("Baseline A")
    table.add_column("\u0394BA")
    table.add_column("\u0394CA")
    table.add_column("\u0394DA")

    table.add_row("Mean", str(mean[0]), str(mean[1]), str(mean[2]), str(mean[3]))
    table.add_row("Minimum", str(minimum[0]), str(minimum[1]), str(minimum[2]), str(minimum[3]))
    table.add_row("Maximum", str(maximum[0]), str(maximum[1]), str(maximum[2]), str(maximum[3]))
    table.add_row("STD Deviations", str(std[0]), str(std[1]), str(std[2]), str(std[3]))

    if not run_all:
        for i in range(runs + 1):
            table.add_row(str(i), str(data[0][i]), str(data[1][i]), str(data[2][i]), str(data[3][i]))

    con.print(table)


def makePlots():

    os.chdir(test_plots)

    for z in range(runs):
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2)
        plt.suptitle("Individual Channels for Run {}".format(z))

        subPlot(x_time, reals[0+(z*num_channel)], ax1, bestFit(x_time, reals[0])[0], "Amplitude versus Samples: Channel A")
        subPlot(x_time, reals[1+(z*num_channel)], ax2, bestFit(x_time, reals[1])[0], "Amplitude versus Samples: Channel B")
        subPlot(x_time, reals[2+(z*num_channel)], ax3, bestFit(x_time, reals[2])[0], "Amplitude versus Samples: Channel C")
        subPlot(x_time, reals[3+(z*num_channel)], ax4, bestFit(x_time, reals[3])[0], "Amplitude versus Samples: Channel D")

        #fig.show()
        fig.savefig(("run{}_indiv".format(z) + ".svg"), dpi = 300)

        #Layout of the combined plot -- NOTE: ONLY CONTAINS LINE OF BEST FIT, could i some how use the previous answers as guesses, avg
        fig2 = plt.figure()
        plt.title("All Channels for Run {}".format(z))
        plt.xlabel("Time")
        plt.ylabel("Amplitude")
        plt.plot(x_time, reals[0+(z*num_channel)], 'o',  color='lightcoral', label='Real A')
        plt.plot(x_time, reals[1+(z*num_channel)], 'o',  color='indianred', label='Real B')
        plt.plot(x_time, reals[2+(z*num_channel)], 'o',  color='firebrick', label='Real C')
        plt.plot(x_time, reals[3+(z*num_channel)], 'o',  color='salmon', label='Real D')
        plt.plot(x_time, bestFit(x_time, reals[0+(z*num_channel)])[0][0], '-', color='black', label='Best Fit')
        plt.legend()

        #fig2.show()
        fig2.savefig(("run{}_together".format(z) + ".svg"), dpi = 300)

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
def main(iterations):

    '''This iteration loop will run through setting up the channels to the values associated to the generator code. It will also loop through
    each channel and save the information to temp arrays. These temp arrays allow us to format our data into 2D arrays, so it's easier to 
    reference later'''
    vsnks = []
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

    for it in iterations:

        gen.dump(it) #pulling info from generator
        
        #connecting and setting up the uniti
        '''Note how each step of time is equiv to 1/sample_rate
        When you reach sample_rate/sample_rate, one second has passed.
        TX: Below, we will be sending oiut samples equiv. to sample_rate after 10 seconds, so this will end at 11 secondi
        RX: Calculate the oversampling rate to find the number of samples to intake that match your ideal (sample count)'''
        sample_rate = int(it["sample_rate"])
        tx_stack = [ (10.0 , sample_rate)]
        rx_stack = [ (10.25, int(it["sample_count"]))]
        
        #this is the code that will actually tell the unit what values to run at
        vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)


        #Other important variables that require connection to the unit
        global runs
        runs = it["i"] #equal sign because we only care about the last value
        global wave_freq
        wave_freq = it["wave_freq"]
        time = np.arange(0,it["sample_count"]/it["sample_rate"], 1/it["sample_rate"])
        global x_time
        x_time = np.asarray(time)
        vsnks.append(vsnk) #This will loop us through the channels an appropriate amount of time
        for vsnk in vsnks:
            ampl  = []
            freq = []
            phase = []
            offset = []
            for ch, channel in enumerate(vsnk): #Goes through each channel to sve data

                real = [datum.real for datum in channel.data()] # saves data of real data in an array               
              
                reals.append(real) #Used for plots, but doesn't need to be reformatted

                #used for charts 
                hold, param = bestFit(x_time, real)
                ampl.append(param[0])
                freq.append(param[1])
                phase.append(param[2])
                offset.append(hold[1])

        #APPENDING Info
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

    #print(data)

    #STARTING THE CHECKS
    #2D arrays containting summary values
    means = []
    stds = []
    mins = []
    maxs = []
    for test in range(len(data)):
        mean_temp = []
        std_temp = []
        mins_temp = []
        maxs_temp = []
        for ch in range(4):
            mean_temp.append(np.mean(data[test][ch]))
            std_temp.append(np.std(data[test][ch]))
            mins_temp.append(min(data[test][ch]))
            maxs_temp.append(max(data[test][ch]))
        means.append(mean_temp) #for formatting reasonss
        stds.append(std_temp)
        mins.append(mins_temp)
        maxs.append(maxs_temp)

    #Calculating the Criteria
    #2D array holding thresholds of: mean, std, min, max
    criteria = []

    #Frequency
    freq_mean_thresh = 0.1 #Hz bound
    freq_std_thresh = 0.0001
    freq_criteria = []
    for ch in range(1, 4): #starting at 1 because index 0 is A baseline
        freq_criteria.append((freq_mean_thresh, freq_std_thresh, (means[0][ch] - (3*stds[0][ch])), (means[0][ch] + (3*stds[0][ch]))))
    criteria.append(freq_criteria) #Formatting

    #Amplitude
    ampl_std_thresh = 0.0002
    ampl_criteria = []
    for ch in range(1, 4): #starting at 1 because index 0 is A baseline
        ampl_criteria.append((3*stds[1][ch], ampl_std_thresh, (means[1][ch] - (3*stds[1][ch])), (means[1][ch] + (3*stds[1][ch]))))
    criteria.append(ampl_criteria)

    #phase
    phase_mean_thresh = 0.0349066 #rad bound
    phase_std_thresh = 0.006
    phase_criteria = []
    for ch in range(1, 4): #starting at 1 because index 0 is A baseline
        phase_criteria.append((phase_mean_thresh, phase_std_thresh, (means[2][ch] - (3*stds[2][ch])), (means[2][ch] + (3*stds[2][ch]))))
    criteria.append(phase_criteria)

    #doing the checks, setting up subtest booleans
    subtest_bool = [] #[test][channel diff][pass/fail]

    for test in range(len(criteria)):
        temp_hold = []
        for ch in range(len(criteria[test])):
            temp_hold.append((check(criteria[test][ch], means[test][ch], stds[test][ch], mins[test][ch], maxs[test][ch])))
        subtest_bool.append((temp_hold))

    #print(subtest_bool)

    #Overall Tests boolean
    overall_bool = [True, True, True]
    for test in range(len(criteria)):
        if np.prod(subtest_bool[test]) == 0: #If list contains and 0
            overall_bool[test] =  False

    #Checking if plots should print
    if (np.prod(overall_bool) == 0 or plot_toggle):
        makePlots()

    #Outputting tables
    #Output tables and their flags- This allows me to always reference them - no matter the iteration
    overall_tests = Table(title="Overall Tests", show_lines=True)
    overall_tests.add_column("Test")
    overall_tests.add_column("Status")
    overall_tests.add_row("Frequency", boolToWord(overall_bool[0]))
    overall_tests.add_row("Amplitude", boolToWord(overall_bool[1]))
    overall_tests.add_row("Phase", boolToWord(overall_bool[2]))
    con.print(overall_tests)

    #Outputting the subtests
    max_crit = "< mean + 3*std"
    min_crit = "> mean - 3*std"

    #Print subtables of failed overall tests and make their plots
    if not overall_bool[1]:
        st_freq  = Table(title="SubTest Results - Frequency Tests", show_lines=True)
        subtestTable(st_freq, str(freq_mean_thresh), min_crit, max_crit, str(freq_std_thresh), subtest_bool[0])
    if not overall_bool[2]:
        st_ampl  = Table(title="SubTest Results - Amplitude Tests", show_lines=True)
        subtestTable(st_ampl, "3 * STD", min_crit, max_crit, str(ampl_std_thresh), subtest_bool[1])
    if not overall_bool[0]:
        st_phase = Table(title="SubTest Results - Phase Tests", show_lines=True)
        subtestTable(st_phase, str(phase_mean_thresh), min_crit, max_crit, str(phase_std_thresh), subtest_bool[2])

    #Summary Statistics
    sum_freq  = Table(title="Summary Frequency", show_lines=True)
    summaryTable(overall_bool[0], sum_freq, means[0], mins[0], maxs[0], stds[0], data[0])

    sum_ampl  = Table(title="Summary Amplitude", show_lines=True)
    summaryTable(overall_bool[1], sum_ampl, means[1], mins[1], maxs[1], stds[1], data[1])

    sum_phase  = Table(title="Summary Phase", show_lines=True)
    summaryTable(overall_bool[2], sum_phase, means[2], mins[2], maxs[2], stds[2], data[2])

    #DC Offset Table
    dc_offset_table = Table(title="DC Offsets", show_lines=True)
    dc_offset_table.add_column("Run")
    dc_offset_table.add_column("\u0394BA")
    dc_offset_table.add_column("\u0394CA")
    dc_offset_table.add_column("\u0394DA")
    for i in range(len(offsets)):
        dc_offset_table.add_row(str(i), str(offsets[i][0]), str(offsets[i][1]), str(offsets[i][2]))
    con.print(dc_offset_table)
main(gen.lo_band_phaseCoherency(4))                  

