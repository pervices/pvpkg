from common import sigproc
from common import engine
from common import generator as gen
from common import pdf_report
from common import test_args
from common import log

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import stats
import math
import numpy as np
import pandas as pd

from inspect import currentframe, getframeinfo

from common import outputs as out
from inspect import currentframe, getframeinfo
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

# Criteria  
freq_std_thresh = 0.6
# NOTE: ampl_std_thresh may be changed for device specific reasons
ampl_std_thresh = 0.001
phase_mean_thresh = 0.0349066 #rad bound
phase_std_thresh = 0.002

# Number of test runs per frequency
num_runs = 4

now = datetime.now() 
iso_time = now.strftime("%Y%m%d%H%M%S.%f")

#Setting up directories for plots
parent_dir = os.getcwd()
leaf_dir = "dump/"
dump_dir = parent_dir + leaf_dir
dump_path = os.path.join("./", dump_dir)
os.makedirs(dump_path,exist_ok=True)

test_plots = dump_dir + iso_time + "-tx_rx_phase"
os.makedirs(test_plots, exist_ok = True)

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

def bestFit(x, y, wave_freq):
    guess = [max(y), wave_freq, 0.25, 0]
    try:
        param, covariance  = curve_fit(waveEquation, x, y, p0=guess)
    except:
        frameinfo = getframeinfo(currentframe())
        component = "{}:{}".format(frameinfo.filename, frameinfo.lineno)
        log.pvpkg_log_error(component, "Failed to fit curve to data.")
        return (0, 0), (0, 0, 0)
    fit_amp = abs(param[0])
    fit_freq = param[1]
    fit_phase = param[2]
    # inverting the amplitude acts like phase offset by pi rad (180 degrees)
    if param[0] < 0:
        fit_phase += math.pi
    # ensure the 0 <= phase < 2*pi to make comparison easy
    while fit_phase < 0:
        fit_phase += (2*math.pi)
    while fit_phase >= (2*math.pi):
        fit_phase -= (2*math.pi)
    fit_offset = param[3]
    best_fit = waveEquation(x, fit_amp, fit_freq, fit_phase, fit_offset) 

    return (best_fit, fit_offset), (fit_amp, fit_freq, fit_phase) 

def makePlots(x_time, real_data, best_fit_data, offset_data, wave_freq, sample_rate):
    plotted_samples = int(round(1/(int(wave_freq)/sample_rate))*num_output_waves)
    f = open("Data_Plots.txt", "w")
    f.close()

    num_subplot_rows = int(math.ceil(len(targs.channels) / 2))
    for run in range(num_runs):
        fig, axes = plt.subplots(num_subplot_rows, 2)
        plt.suptitle("Amplitude versus Samples: Individual Channels for Run {}".format(run))

        os.chdir(test_plots) #To save to a file

        row = 0
        for ch in range(len(targs.channels)):
            subplot_row = int(ch / 2)
            subPlot(x_time[0:plotted_samples], real_data[run][ch][0:plotted_samples], axes[subplot_row][ch%2], best_fit_data[run][ch][0:plotted_samples], offset_data[run][ch], "Channel {}".format(channel_map[targs.channels[ch]]))

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
            plt.plot(x_time[0:plotted_samples], real_data[run][ch][0:plotted_samples], '.', markersize=3, label="Real {}".format(channel_map[targs.channels[ch]]))

        #Best fits
        for ch in range(len(targs.channels)):
            plt.plot(x_time[0:plotted_samples], best_fit_data[run][ch][0:plotted_samples], '-', linewidth= 0.75, label="Best Fit {}".format(channel_map[targs.channels[ch]]))

        plt.legend()

        fig.savefig(("run{}_together".format(run) + ".svg"))
        s2 = report.get_image_io_stream()
        fig.savefig(s2, format="png", dpi=300)
        img2 = report.get_image_from_io_stream(s2)

        report.buffer_put("image_double", [img1, img2], "Run " + str(run))
        log.pvpkg_log_info("TX_RX_PHASE", "Run figure has been put in buffer")
        plt.clf()

def boolToWord(word):
    if word > 0:
        return("Pass")
    elif word < 0:
        return "N/A"
    else:
        return("Fail")

def main():
    # Add generic test arguments
    global targs
    # To allow for modifying ampl_std_thresh for device specific reasons
    global ampl_std_thresh
    targs = test_args.TestArgs(testDesc="TX/RX phase coherency test")
    fail_flag = 0

    global report
    report = pdf_report.ClassicShipTestReport("tx_rx_phase", targs.serial, targs.report_dir, targs.docker_sha)
    report.insert_title_page("Low Band TX RX Phase Coherency Test")

    if(targs.product == 'Vaunt'):
        iterations = gen.lo_band_phaseCoherency()
    elif(targs.product == 'Tate' or targs.product == "BasebandTate"):
        iterations = gen.cyan.lo_band.phaseCoherency()
    elif(targs.product == 'Lily'):
        iterations = gen.chestnut.lo_band.phaseCoherency()
        # Acceptable threshold is greater for Chestnut since it takes a few runs for amplitude to stabilize, likely an rf thermal issue
        ampl_std_thresh = 0.003
    else:
        log.pvpkg_log_error("TX_RX_PHASE", "Unrecognized product argument")
        fail_flag = 1

    channel_list = channel_map[targs.channels].tolist()
    for ch in range(1, len(channel_list)):
        channel_list[ch] = "\u0394" + channel_list[ch] + channel_map[targs.channels[0]]

    summary_table = [["Center Freq", "Wave Freq", "Freq Result", "Ampl Result", "Phase Result"]]

    for it in iterations:
        gen.dump(it) 

        # First column is the first channel's value. Subsequent columns are the delta between that channel and the first.
        # Example: channel list is [0, 1, 3], freq_delta_matrix for a single iteration would be as follows:
        # [freqCh0, freqCh1 - freqCh0, freqCh3 - freqCh0]
        freq_delta_matrix = np.zeros((num_runs, len(targs.channels)))
        ampl_delta_matrix = np.zeros((num_runs, len(targs.channels)))
        phase_delta_matrix = np.zeros((num_runs, len(targs.channels)))
        offset_delta_matrix = np.zeros((num_runs, len(targs.channels)))

        reals = []
        best_fits = []
        offsets = []
        sample_rate = int(it["sample_rate"])
        sample_count = int(it["sample_count"])
        wave_freq = int(it["wave_freq"])
        for run in range(num_runs):
            log.pvpkg_log_info("TX_RX_PHASE", "Beginning run {}/{}".format(run, num_runs - 1))
            '''
            Note how each step of time is equiv to 1/sample_rate
            When you reach sample_rate/sample_rate, one second has passed.
            TX: Below, we will be sending oiut samples equiv. to sample_rate after 10 seconds, so this will end at 11 seconds
            RX: Calculate the oversampling rate to find the number of samples to intake that match your ideal (sample count)
            '''
            tx_stack = [ (tx_burst , sample_rate)]
            rx_stack = [ (rx_burst, int(it["sample_count"]))]

            try:
                vsnk = engine.run(targs.channels, it["wave_freq"], sample_rate, it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
            except Exception as err:
                frameinfo = getframeinfo(currentframe())
                component = "{}:{}".format(frameinfo.filename, frameinfo.lineno)
                log.pvpkg_log_error(component, "Exception occured while streaming:\n {}".format(err))
                report.draw_from_buffer()
                report.save()
                sys.exit(1)

            if (run == 0):
                table_data = [["Center Frequency (Hz)", "Wave Frequency (Hz)", "Sample Rate (SPS)", "Sample Count", "TX Gain (dB)", "RX Gain (dB)"],
                                [it["center_freq"], it["wave_freq"], sample_rate, it["sample_count"], it["tx_gain"], it["rx_gain"]]]
                report.buffer_put("table_wide", table_data, "Test Configuration")
            

            # Number of waves to cutoff before starting analysis
            begin_cutoff = int(round((1/(wave_freq/sample_rate))*begin_cutoff_waves))

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

                # Explicitly assigning the relevant slice of data to a variable, then passing said variable to bestFit
                # Creating a slice anonymously may cause a crash where somehow data collected the the engine wasn't making it to bestFit
                trimmed_real = real[begin_cutoff:]

                ch_real_data.append(trimmed_real)

                best_fit, param = bestFit(x_time, trimmed_real, wave_freq)

                ampl.append(param[0])
                freq.append(param[1])
                phase.append(param[2])
                best.append(best_fit[0])
                offset.append((best_fit[1]))

            #Appending to the temp variables
            reals.append(ch_real_data)
            best_fits.append(best)
            offsets.append(offset)

            freq_delta_matrix[run][baselineCh_index] = freq[baselineCh_index]
            ampl_delta_matrix[run][baselineCh_index] = ampl[baselineCh_index]
            phase_delta_matrix[run][baselineCh_index] = phase[baselineCh_index]
            offset_delta_matrix[run][baselineCh_index] = offset[baselineCh_index]
            for channel in range(1, len(targs.channels)):
                freq_delta_matrix[run][channel] = freq[channel] - freq[baselineCh_index]
                ampl_delta_matrix[run][channel] = ampl[channel] - ampl[baselineCh_index]
                phase_delta_matrix[run][channel] = phase[channel] - phase[baselineCh_index]
                # Shift phase difference by 2*pi if the difference in phase is greater than pi
                # Since phases that are multiples of 2*pi are equivalent
                while(phase_delta_matrix[run][channel] > math.pi):
                    phase_delta_matrix[run][channel] = phase_delta_matrix[run][channel] - (2 * math.pi)
                while(phase_delta_matrix[run][channel] < -math.pi):
                    phase_delta_matrix[run][channel] = phase_delta_matrix[run][channel] + (2 * math.pi)
                offset_delta_matrix[run][channel] = offset[channel] - offset[baselineCh_index]

        # Organize data into a datatable such that we can manipulate/visualize more easily
        freq_df = pd.DataFrame(columns=channel_list, data=freq_delta_matrix)
        ampl_df = pd.DataFrame(columns=channel_list, data=ampl_delta_matrix)
        phase_df = pd.DataFrame(columns=channel_list, data=phase_delta_matrix)
        offset_df = pd.DataFrame(columns=channel_list, data=offset_delta_matrix)
        
        # Add summary statistics to the dataframes
        freq_df = pd.concat([freq_df.describe().loc[['min', 'max', 'mean', 'std']], freq_df])
        ampl_df = pd.concat([ampl_df.describe().loc[['min', 'max', 'mean', 'std']], ampl_df])
        phase_df = pd.concat([phase_df.describe().loc[['min', 'max', 'mean', 'std']], phase_df])
        offset_df = pd.concat([offset_df.describe().loc[['min', 'max', 'mean', 'std']], offset_df])

        # Increase the std_ratio if the number of iterations implies a substantially smaller std_deviation
        global std_ratio
        alt_std_ratio = math.sqrt(num_runs)
        if alt_std_ratio > std_ratio:
            log.pvpkg_log_info("TX_RX_PHASE", "Replacing old std_ratio (=" + str(std_ratio) + ") with updated str_ratio (="+ str(alt_std_ratio) + ") due to iteration count.")
            std_ratio = alt_std_ratio

        # Increase the std_ratio_phase if the number of iterations implies a substantially smaller std_deviation
        global std_ratio_phase
        alt_std_ratio = math.sqrt(num_runs)
        if alt_std_ratio > std_ratio_phase:
            log.pvpkg_log_info("TX_RX_PHASE", "Replacing old std_ratio_phase (=" + str(std_ratio) + ") with updated std_ratio_phase (="+ str(alt_std_ratio) + ") due to iteration count.")
            std_ratio_phase = alt_std_ratio

        # Basic test to check if signal is present on our baseline channel. 
        if wave_freq - (std_ratio * freq_std_thresh) < freq_df.loc['mean'][channel_list[0]] < wave_freq + (std_ratio * freq_std_thresh):
            frameinfo = getframeinfo(currentframe())
            component = "{}:{}".format(frameinfo.filename, frameinfo.lineno)
            log.pvpkg_log_error(component, "Signal not detected on Ch{}".format(channel_list[0]))

        # Get test results for min, max, and stddev for freq, ampl, and phase
        result_cols = ['Test', 'Criteria'] + channel_list

        freq_res = pd.DataFrame(columns=result_cols)
        freq_res['Test'] = ['min', 'max', 'std']
        freq_res['Criteria'] = ['> mean - 4*std', '< mean + 4*std', "< " + str(freq_std_thresh)]
        freq_res.set_index('Test', drop=False, inplace=True)
        for ch in channel_list:
            freq_res.at['min', ch] = boolToWord(freq_df.loc['min'][ch] > (freq_df.loc['mean'][ch] - 4*freq_df.loc['std'][ch]))
            freq_res.at['max', ch] = boolToWord(freq_df.loc['max'][ch] < (freq_df.loc['mean'][ch] + 4*freq_df.loc['std'][ch]))
            freq_res.at['std', ch] = boolToWord(freq_df.loc['std'][ch] < freq_std_thresh)

        ampl_res = pd.DataFrame(columns=result_cols)
        ampl_res['Test'] = ['min', 'max', 'std']
        ampl_res['Criteria'] = ['> mean - 4*std', '< mean + 4*std', "< " + str(ampl_std_thresh)]
        ampl_res.set_index('Test', drop=False, inplace=True)
        for ch in channel_list:
            ampl_res.at['min', ch] = boolToWord(ampl_df.loc['min'][ch] > (ampl_df.loc['mean'][ch] - 4*ampl_df.loc['std'][ch]))
            ampl_res.at['max', ch] = boolToWord(ampl_df.loc['max'][ch] < (ampl_df.loc['mean'][ch] + 4*ampl_df.loc['std'][ch]))
            ampl_res.at['std', ch] = boolToWord(ampl_df.loc['std'][ch] < ampl_std_thresh)
        
        phase_res = pd.DataFrame(columns=result_cols)
        phase_res['Test'] = ['min', 'max', 'std']
        phase_res['Criteria'] = ['> mean - 4*std', '< mean + 4*std', "< " + str(ampl_std_thresh)]
        phase_res.set_index('Test', drop=False, inplace=True)
        for ch in channel_list:
            phase_res.at['min', ch] = boolToWord(phase_df.loc['min'][ch] > (phase_df.loc['mean'][ch] - 4*phase_df.loc['std'][ch]))
            phase_res.at['max', ch] = boolToWord(phase_df.loc['max'][ch] < (phase_df.loc['mean'][ch] + 4*phase_df.loc['std'][ch]))
            phase_res.at['std', ch] = boolToWord(phase_df.loc['std'][ch] < phase_std_thresh)

        # Return a failure if any of the tests failed
        freq_overall_res = freq_res[channel_list].apply(lambda column: column.str.contains("Pass")).all().all()
        ampl_overall_res = ampl_res[channel_list].apply(lambda column: column.str.contains("Pass")).all().all()
        phase_overall_res = phase_res[channel_list].apply(lambda column: column.str.contains("Pass")).all().all()
        if not freq_overall_res or not ampl_overall_res or not phase_overall_res:
            fail_flag = 1

        # Update overall summary table with this iteration
        summary_table.append([it["center_freq"], it["wave_freq"], boolToWord(freq_overall_res), boolToWord(ampl_overall_res), boolToWord(phase_overall_res)])

        # Print data and results table to console
        log.pvpkg_log_info("TX_RX_PHASE", "Frequency Data:", before="\n")
        log.pvpkg_log(freq_df.to_markdown(index=True))
        log.pvpkg_log_info("TX_RX_PHASE", "Amplitude Data:", before="\n")
        log.pvpkg_log(ampl_df.to_markdown(index=True))
        log.pvpkg_log_info("TX_RX_PHASE", "Phase Data:", before="\n")
        log.pvpkg_log(phase_df.to_markdown(index=True))
        log.pvpkg_log_info("TX_RX_PHASE", "Frequency Results:", before="\n")
        log.pvpkg_log(freq_res.to_markdown(index=False))
        log.pvpkg_log_info("TX_RX_PHASE", "Amplitude Results:", before="\n")
        log.pvpkg_log(ampl_res.to_markdown(index=False))
        log.pvpkg_log_info("TX_RX_PHASE", "Phase Results:", before="\n")
        log.pvpkg_log(phase_res.to_markdown(index=False))

        # Add plots to the report
        makePlots(x_time, reals, best_fits, offsets, wave_freq, sample_rate)

        # If we have more than 4 channels, we need to cap our values at 6 digits such that all channels fit on the page
        if len(channel_list) > 4:
            freq_df = freq_df.round(6)
            ampl_df = ampl_df.round(6)
            phase_df = phase_df.round(6)
            offset_df = offset_df.round(6)

        # Add results tables to the report
        report.buffer_put("table_wide", [tuple(freq_res.columns.tolist())] + freq_res.to_records(index=False).tolist(), "Frequency Results:")
        report.buffer_put("text", " ")
        report.buffer_put("table_wide", [tuple(ampl_res.columns.tolist())] + ampl_res.to_records(index=False).tolist(), "Amplitude Results:")
        report.buffer_put("text", " ")
        report.buffer_put("table_wide", [tuple(phase_res.columns.tolist())] + phase_res.to_records(index=False).tolist(), "Phase Results:")

        # Add data tables to the report
        report.buffer_put("text", " ")
        report.buffer_put("table_wide", [tuple(' ') + tuple(freq_df.columns.tolist())] + freq_df.to_records(index=True).tolist(), "Frequency Data:")
        report.buffer_put("text", " ")
        report.buffer_put("table_wide", [tuple(' ') + tuple(ampl_df.columns.tolist())] + ampl_df.to_records(index=True).tolist(), "Amplitude Data:")
        report.buffer_put("text", " ")
        report.buffer_put("table_wide", [tuple(' ') + tuple(phase_df.columns.tolist())] + phase_df.to_records(index=True).tolist(), "Phase Data:")
        report.buffer_put("text", " ")
        report.buffer_put("table_wide", [tuple(' ') + tuple(offset_df.columns.tolist())] + offset_df.to_records(index=True).tolist(), "Offset Data:")
        report.buffer_put("pagebreak")
    
    # Add overall summary table
    report.insert_text_large("Test Overview:")
    report.insert_table(summary_table, 20)
    report.new_page()
    
    # get back outside to save
    os.chdir(parent_dir)
    report.draw_from_buffer()
    report.save()
    log.pvpkg_log_info("TX_RX_PHASE", "PDF report saved at " + report.get_filename())

    sys.exit(fail_flag)

if __name__ == '__main__':
    main()
