#IMPORTING LIBRARIES AND MODULES
#TODO: go through these imports and libraries to see if we really need EVERY one -- add them in order of use
#Per Vices Imports
from common import sigproc
from common import engine
from common import generator as gen

#GNU radio
from gnuradio import uhd

#Basic imports
import time, datetime
import os
import numpy as np

#PDF IMPORTS
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import Image, Paragraph, Table, Frame

#Plot and Data imports
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
from scipy.optimize import curve_fit
from scipy.signal import blackman
from scipy.fft import fft, fftfreq, fftshift
from reportlab.lib.utils import ImageReader
from scipy.signal import find_peaks

import glob
#import test_ship_collection as tsc
import re

from matplotlib import rcParams
import math

#Have chosn toe put some variables as global, so they're easy to access
#TODO: Check where the final file should go
#Making file and doc title
date = datetime.datetime.now()
formattedDate = date.isoformat("_")
file_title = "ship_report_" + formattedDate + ".pdf"
doc_title = "ship_report_" + formattedDate

#SETTING UP PATH DIRECTORIES
current_dir = os.getcwd()
output_dir = current_dir + "/ship_reports"
plots_dir = output_dir + "/plots_" + formattedDate
os.makedirs(output_dir, exist_ok=True)
os.makedirs(plots_dir, exist_ok=True)

#USER SET VARIABLES
begin_cutoff_waves = 17.20 #how many waves to cut off before tracking data
num_output_waves = 2 #number of waves shown on the final plots (IQ)
decimal_round = 5
specified_SNR = 41 #dB

#Unit Info
#TODO: MAKE THIS PULL REVISION NUMBERS - DID DOUG WANT TO DO THAT?
test = uhd.usrp_sink(device_addr=args, stream_args=uhd.stream_args('sc16'))
print(test)
unit_name = "Crimson"
serial_num = "12345" #NOTE: Is this the same as unit number??
UHD_ver = "UHD later"
server_ver = "Server Later"
fpga_ver = "FPGA Later"
MCU_ver = "MCU Later"
num_channels = 4

#Globals that will be changed later
center_freq = -1
wave_freq = -1
sample_rate = -1
sample_count = -1
period = -1 #how many samples per one period or one wave
being_cutoff = -1
summary_info = [] #[iteration][[freq][amplitude][snr]]

#page stuff
page_count = 0
page_total = num_channels*4 + 2


#Adding logo - more efficent to just initialize at beginning
h_img_data = open(current_dir + "/pervices-logo.png", "rb")
header_img = ImageReader(h_img_data)

#Formatting Variables
python_to_inch = 72
font = "Times-Roman"
gen_font_size = 12
bold_font = "Times-Bold"

rcParams['agg.path.chunksize'] = 115


''' DEBUGGER: Prints out the x and y placements of the pixels, to allow for nice layout
PARAMS: c (name of pdf)
RETURNS: none'''
def drawMyRuler(c):
    c.drawString(100,10, 'y100')
    c.drawString(200,10, 'y200')
    c.drawString(300,10, 'y300')
    c.drawString(400,10, 'y400')
    c.drawString(500,10, 'y500')

    c.drawString(10,100, 'x100')
    c.drawString(10,200, 'x200')
    c.drawString(10,300, 'x300')
    c.drawString(10,400, 'x400')
    c.drawString(10,500, 'x500')
    c.drawString(10,600, 'x600')
    c.drawString(10,700, 'x700')
    c.drawString(10,800, 'x800')

'''Creates Title Page
PARAMS: pdf
RETURNS: NONE'''
def titlePage(pdf):
    #Positional Values
    title_font_size = 26
    title_x = 100
    title_y = 575
    list_font_size = 14
    list_x = title_x - 5
    list_y = title_y - 75
    logo_x, logo_y = 200, 100
    logo_width, logo_height = 400, 300
    #Setting up title on Title Page
    title = pdf.beginText()
    title.setTextOrigin(title_x, title_y)
    title.setFont(font, title_font_size)
    title.textLine(text=("Ship Test Report: " + unit_name + " - Serial Number: " + serial_num))
    title.setFont(font, title_font_size/2)
    title.textLine("Date and Time: " + formattedDate)
    pdf.drawText(title)

    #Printing out Important Details regarding the Machine
    #everything will be attached to unitList text object
    unitList = pdf.beginText(list_x, list_y)

    #UHD Version
    unitList.setFont(bold_font, list_font_size)
    unitList.textOut("UHD Version: ")
    unitList.setFont(font, list_font_size)
    unitList.textLine(UHD_ver)

    #Server Version
    unitList.setFont(bold_font, list_font_size)
    unitList.textOut("Server Version: ")
    unitList.setFont(font, list_font_size)
    unitList.textLine(server_ver)

    #FPGa Version
    unitList.setFont(bold_font, list_font_size)
    unitList.textOut("FPGA Version: ")
    unitList.setFont(font, list_font_size)
    unitList.textLine(fpga_ver)

    #Server Version
    unitList.setFont(bold_font, list_font_size)
    unitList.textOut("MCU Version: ")
    unitList.setFont(font, list_font_size)
    unitList.textLine(MCU_ver)

    #TODO: SET UP THE REST OF THE VERSION VALUES ONCE THEY ARE PROPERLY DECLARED AT THE BEGINNING OF THE CODE
    #TODO: ADD COMPANY LOGO?

    pdf.drawText(unitList)

    #Adding Logo
    pdf.drawImage(header_img, logo_x, logo_y, logo_width, logo_height)

'''Creates a title for each Run Page
PARAMS: pdf, it name
RETURNS: None
'''
def runTitle(pdf, it):
    #Positionalgalues
    title_font_size = 26
    title_x, title_y = 100, 575

    #Setting up title on Title Page
    title = pdf.beginText()
    title.setTextOrigin(title_x, title_y)
    title.setFont(font, title_font_size)
    title.textLine(text=("Run Number " + str(it) + " - Loopback On " + unit_name))
    pdf.drawText(title)

'''Creates a header for each page of document
PARAMS: pdf
RETURNS: None'''
def header(pdf):
    #Positional Values
    header_font_size = 10
    header_x, header_y = 633, 584
    logo_width, logo_height = 75, 25
    logo_x, logo_y = header_x - logo_width - 2, header_y - 17
    pg_x, pg_y = 700,10

    #Header Writing
    header = pdf.beginText()
    header.setTextOrigin(header_x, header_y)
    header.setFont(font, header_font_size)
    header.textLine(text=("Unit Number: " + serial_num))
    header.textLine(text=(formattedDate))
    pdf.drawText(header)

    #Drawing logo
    pdf.drawImage(header_img, logo_x, logo_y, logo_width, logo_height)

    #Page Number
    pg_num = pdf.beginText()
    pg_num.setTextOrigin(pg_x, pg_y)
    pg_num.setFont(font, header_font_size)
    pg_num.textLine(text=("Page " + str(page_count) + " of " + str(page_total)))

'''Creates a table that shows the input values of each Run
PARAMS: pdf, center_freq, wave_freq, sample_rate, sample_count, tx_gain, rx_gain
RETURNS: None'''
def inputTable(pdf, center_freq, wave_freq, sample_rate, sample_count, tx_gain, rx_gain):
    #positional values
    label_x = 40
    label_y = 525
    table_width = 400
    table_height = 75
    table_x = label_x - 5
    table_y = label_y - (table_height/2) - 3

    #Labelling input data
    label = pdf.beginText()
    label.setTextOrigin(label_x, label_y)
    label.setFont(font, 14)
    label.textLine(text=("Input Values: "))
    pdf.drawText(label)

    #Setting up 2D array holding input data
    data = [["Center Frequency (Hz)", "Wave Frequency (Hz)", "Sample Rate (SPS)", "Sample Count", "TX Gain (dB)", "RX Gain (dB)"],
            [center_freq, wave_freq, sample_rate, sample_count, tx_gain, rx_gain]]

    #Making and styling the table
    inputs = Table(data, style=[('GRID', (0,0), (6,1), 1, colors.black),
                                ('BACKGROUND', (0,0), (6,0), '#D5D6D5')])
    inputs.wrapOn(pdf, table_width, table_height)
    inputs.drawOn(pdf, table_x, table_y)

'''
Represents the wave equation
PARAMS: time, ampl, freq, phase
RETUNRS: y'''
def waveEquation(time, ampl, freq, phase, dc_offset):


    y = ampl*np.cos((2*np.pi*freq*time + phase)) + dc_offset #model for wave equation

    return y

'''Plots the FFT subplots all in the same format
PARAMS: x, rea;, ax, imag, title
RETURNS: NONE'''
def subPlotFFTs(x, y, ax, title, max_five, nf): #TODO: Add points on top of peaks

    ax.set_title(title)
    ax.set_ylim(0, max(y) + max(y)*0.1)
    # ax.set_xlim(min(x)/2, max(x)/2)
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Amplitude (dB)")
    fft, = ax.plot(x, y, color='crimson')
    ax.axhline(y = nf, markersize=0.5, alpha=0.3, label="Noise Floor")

    for i in range(len(max_five)):
        ax.plot(max_five[i][0], max_five[i][1], "x")

    return fft

'''Plots the IQ subplots all in the same format
PARAMS: x, real, ax, imag, best_fit_real, best_fit_imag, title
RETURNS: NONE'''
def subPlotIQs (x, real,imag, best_fit_real, best_fit_imag, offset_real, offset_imag, ax, title):
    ax.set_title(title)
    best_fit_real *= 1000
    best_fit_imag *= 1000
    ax.set_xlabel("Time")
    ax.set_ylabel("Amplitude (kV)") #NOTE: I HOPE THIS IS RIGHT
    bf_r, = ax.plot(x, best_fit_real, '-', markersize=0.1, color='indianred', label="Real Best Fit")
    ax.plot(x, real, '.', markersize=2, color='crimson', label="Real")
    ax.axhline(y = offset_real, markersize=0.025, color='red', alpha=0.4, label='Real Offset')
    ax.plot(x, best_fit_imag, '-', markersize=0.1, color='darkmagenta', label="Imaginary Best Fit")
    ax.plot(x, imag, '.', markersize=2, color='purple', label="Imaginary")
    ax.axhline(y = offset_imag, markersize=0.025, color='indigo', alpha=0.4, label='Imaginary Offset')

    real_peaks = find_peaks(real, distance=period)
    imag_peaks = find_peaks(imag, distance=period)

    for r, i in zip(real_peaks[0], imag_peaks[0]):
        ax.axvline(x = x[r], linestyle='--', alpha=0.5, color='rosybrown', markersize=0.05)
        ax.text(x[r], max(best_fit_real) + 1, "\u2190" + str(round(x[r], 3)), fontsize=7, verticalalignment='top', )
        ax.axvline(x = x[i],  linestyle='--', alpha=0.5, color='darkslateblue',markersize=0.05)
        ax.text(x[i], min(best_fit_imag) - 1, "\u2190" + str(round(x[i], 3)), fontsize=7, verticalalignment='top')

    return bf_r

'''Creates the line of best fit for the given x and y
PARAMS: x,y
RETURNS: best_fit (y values of the line of best fit '''
def bestFit(x, y):
    guess = [max(y), wave_freq, 0, 0] #Based off generator code
    param, covariance  = curve_fit(waveEquation, x, y, p0=guess) #using curve fit to give parameters
    fit_amp = param[0]  #for wave equation that make a line of best fit
    fit_freq = param[1]
    fit_phase = param[2]
    fit_offset = param[3]
    best_fit = waveEquation(x, fit_amp, fit_freq, fit_phase, fit_offset) #making the line of best fit
    return (best_fit, fit_offset), (fit_amp, fit_freq, fit_phase) #returns other values as tuple, so they can be easily referenced

'''Divides given by peak
Params: a, peak
Returns: ans'''
def byOne(a, peak):
    ans = a/peak
    return  ans

'''Calculates the magnitude of the two given values
PARAMS: a, b
RETURNS: ans'''
def magnitude(a,b):
    ans = np.sqrt((a**2) + (b**2))
    return ans

'''returns a bool value to check if the thing is 0
PARAMS: a
returns: a != 0'''
def isNotZero(a):
    return (a != 0)

'''Turns the values recieved into values for the FFT plots
PARAMS: sample_count, reals, imags
RETURNS: freq, normalized_ys'''
def fftValues(x, reals, imags): #TODO: THIS IS A MESS, MUST FIX

    #organizing data
    sort = np.argsort(x)
    reals = reals[sort]
    imags = imags[sort]
    x = x[sort]

    #Getting the magnitude
    mag = np.vectorize(magnitude)
    comp = np.vectorize(complex)
    fft_comp_y = comp(reals, imags)*blackman(len(x))

    #Turning it into fft
    fft_transform = np.fft.fftshift(np.fft.fft(fft_comp_y, len(x), norm="forward"))
    fft_y = abs(mag(fft_transform.imag, fft_transform.real))

    #Finding largest value
    peaks_indices = find_peaks(fft_y)
    max_peak = fft_y[np.argmax(fft_y[[peaks_indices[0]]])]

    normalize = np.vectorize(byOne)
    norm_y = normalize(fft_y, max_peak)

    #Transform to dB
    bools_norms = list(map(isNotZero, norm_y))
    np.place(norm_y, bools_norms, 20*np.log10(norm_y)) #does not log values that are 0

    #Setting up the X values
    freq = np.fft.fftshift(np.fft.fftfreq(len(x), d=(1/sample_rate)))

    return freq, norm_y

'''Turning the plot figure into a rasterized image, saving it to the directory, and putting the plot onto the pdf
PARAMS: plot, title, counter, pdf
RETURNS: NONE'''
def plotToPdf(plt, title, counter, pdf, plot_img_width, plot_img_height, plot_img_pos_x, plot_img_pos_y):

    #Saving plot to proper directory and converting to png
    os.chdir(plots_dir) #ensuring in right directory
    plt.gcf().set_size_inches(8, 5)
    plt.savefig((title + "_" + str(counter)), format='png', dpi=300)

    #Opening file as io bits, then translating them to image reader
    img_data = open(plots_dir + "/" + title + "_" + str(counter), "rb")
    img = ImageReader(img_data)

    pdf.drawImage(img, plot_img_pos_x, plot_img_pos_y, plot_img_width, plot_img_height)

'''Finding the top five peaks
PARAMS: y
RETURNS: max_five'''
def fivePeaks(x, y, ampl):

    max_five = []
    max_five_rounded = []
    peaks, properties = find_peaks(y, height=ampl) #NOTE: What should I use as the height...

    for i in range(5):
        max_peak = peaks[np.argmax(properties['peak_heights'])]
        x_peak, y_peak = x[max_peak], y[max_peak]
        max_five.append((x_peak, y_peak))
        max_five_rounded.append((round(x_peak, decimal_round), round(y_peak, decimal_round)))

        peaks = np.delete(peaks, (np.where(peaks == max_peak)))

    return max_five_rounded, max_five

'''Intakes data to find the noise floor
PARAM: Data
RETURNS: noise_floor_y'''
def noiseFloor(data):

    bin_width = sample_rate/sample_count
    noise_floors  = []

    for ch in range(len(data)):
        n = len(data[ch])
        coherent_gain = sum(data[ch])/n
        noise_gain = sum(data[ch]**2)/n
        noise_floor = bin_width*noise_gain/coherent_gain**2
        noise_floors.append(noise_floor)

    return noise_floors

'''Squares the given values
PARMS: V
RETURNS: v**2'''
def square(v):
    return v**2

'''Turning the amplitudes (volts) into RMS SNR Values
PARAMS:y_vals'''
def toSNR(y_vals):
    #Calculating the RMS Signal Voltage
    #The RMS is one standard deviation of the FFT STD
    rms_signal = np.std(y_vals)

    #Calculating the RMS Signal Voltage - NOTE: how to get instantaneous value
    squares = np.vectorize(square)
    rms_V = sum(squares(y_vals))

    snr = rms_signal/rms_V

    return snr

def partition(array, low, high, other_arrays):

    # choose the rightmost element as pivot
    pivot = array[high]

    # pointer for greater element
    i = low - 1

    # traverse through all elements
    # compare each element with pivot
    for j in range(low, high):
        if array[j] <= pivot:

            # If element smaller than pivot is found
            # swap it with the greater element pointed by i
            i = i + 1
            # print(i)
            # print(j)
            # Swapping element at i with element at j
            (array[i], array[j]) = (array[j], array[i])
            for ar in range(len(other_arrays)):
                # print("ar: " + str(other_arrays[ar]))
                # print("ar: " + str(other_arrays[ar][i]))
                hold = other_arrays[ar][i]
                other_arrays[ar][i] = other_arrays[ar][j]
                other_arrays[ar][j] = hold


    # Swap the pivot element with the greater element specified by i
    (array[i + 1], array[high]) = (array[high], array[i + 1])
    for ar in range(len(other_arrays)):
            hold = other_arrays[ar][i + 1]
            other_arrays[ar][i + 1] =  other_arrays[ar][high]
            other_arrays[ar][high] = hold

    # Return the position from where partition is done
    return i + 1

'''Quick sorts given data
PARAM: array, low, high, optional: Other arrays to be sorted
RETURNS: N/A'''
def quickSort(array, low, high, other_array):
    if low < high:

        # Find pivot element such that
        # element smaller than pivot are on the left
        # element greater than pivot are on the right
        #print("IN QS: " + str(other_array))
        pi = partition(array, low, high, other_array)

        # Recursive call on the left of pivot
        quickSort(array, low, pi - 1, other_array)

        # Recursive call on the right of pivot
        quickSort(array, pi + 1, high, other_array)

'''Runs the tests and data collection, then calls other functions to tests and format the code outputs
PARAMS: iterations
RETURNS: NONE, it is the main function'''
def main(iterations):

    ##MAKING PDF and Title page
    pdf = canvas.Canvas(file_title, pagesize=landscape(letter)) #Setting the page layout and file name
    pdf.setTitle(doc_title)

    #Title page
    drawMyRuler(pdf) #TODO: REMOVE AT THE END
    titlePage(pdf)

    counter = 0 #Keeps track of run
    for it in iterations: #Will iterate per Run
        counter += 1

        #Page One Set up
        pdf.showPage() #Page break on pdf
        global page_count
        page_count += 1
        drawMyRuler(pdf)
        header(pdf)
        runTitle(pdf, str(counter))


        #Initilize Important Arrays
        reals = []
        imags = []
        x_time = []
        ampl_vec = []

        freq_reals = []
        phase_reals = []
        best_fit_reals = []
        offset_reals = []
        ampl_reals = []

        freq_imags = []
        phase_imags = []
        best_fit_imags = []
        offset_imags = []
        ampl_imags = []

        gen.dump(it) #pulls info form generator

        #Prints table showing inputs used on unit
        inputTable(pdf, it["center_freq"], it["wave_freq"], it["sample_rate"], it["sample_count"], it["tx_gain"], it["rx_gain"])

        ##SETING UP TESTS AND GETTING INPUTS
        vsnks = []
        global sample_rate
        sample_rate = int(it["sample_rate"])
        global sample_count
        sample_count = int(it["sample_count"])
        tx_stack = [ (10.0 , sample_rate)] #Equivalent to 1 second
        rx_stack = [ (10.25, sample_count)] #TODO: Maybe add the burst start times to table - or title page

        vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)

        #Other Variables
        global center_freq
        center_freq = int(it["center_freq"])
        global wave_freq
        wave_freq = int(it["wave_freq"])
        global period
        period = int(round(1/(wave_freq/sample_rate)))
        global begin_cutoff
        begin_cutoff = int(period*begin_cutoff_waves)

        #X values
        x = np.arange(begin_cutoff/sample_rate, (sample_count/sample_rate), 1/sample_rate) #0 to max time, taking the 1/sr step
        x_time = np.asarray(x*1000000) # This is for the actual output of IQ plots

        vsnks.append(vsnk) #This will loop us through the channels an appropriate amount of time
        for vsnk in vsnks:

            for ch, channel in enumerate(vsnk): #Goes through each channel to sve data

                real = [datum.real for datum in channel.data()]
                imag = [datum.imag for datum in channel.data()]

                reals.append(real[begin_cutoff:]) #Formats real data into a 2D array
                imags.append(imag[begin_cutoff:])

                best_fit, param = bestFit(x, real[begin_cutoff:])

                ampl_reals.append(param[0])
                freq_reals.append(param[1])
                phase_reals.append(param[2])
                best_fit_reals.append(best_fit[0])
                offset_reals.append((best_fit[1]))

                best_fit, param = bestFit(x, imag[begin_cutoff:])

                ampl_imags.append(param[0])
                ampl_vec.append(20*np.log10(np.sqrt(param[0]**2 + ampl_reals[len(ampl_reals)-1]**2)))
                freq_imags.append(param[1])
                phase_imags.append(param[2])
                best_fit_imags.append(best_fit[0])
                offset_imags.append((best_fit[1]))

        #Making them all np.arrays
        #this for efficency, it is easier to initalize as non-numpy bc allows for flexibility in code
        reals = np.asarray(reals)
        imags = np.asarray(imags)
        ampl_reals = np.asarray(ampl_reals)
        freq_reals = np.asarray(freq_reals)
        phase_reals = np.asarray(phase_reals)
        best_fit_reals = np.asarray(best_fit_reals)
        offset_reals = np.asarray(offset_reals)

        ampl_vecs = np.asarray(ampl_vec)
        ampl_imags = np.asarray(ampl_imags)
        freq_imags = np.asarray(freq_imags)
        phase_imags = np.asarray(phase_imags)
        best_fit_imags = np.asarray(best_fit_imags)
        offset_imags = np.asarray(offset_imags)


        #VISUALS on PDF
        #IMAG AND REAL
        '''Following the steps of: Setting up variables, making the individiual plots on the figure,
        rasterizing onto the PDF, adding note to ensure readers know there are less than tested samples visible'''
        #variables for placement of plot
        plot_img_width, plot_img_height = 700, 450
        plot_img_pos_x,  plot_img_pos_y = 2, 20
        IQ_width, IQ_height = 250, 105
        IQ_table_x, IQ_table_y = 565,15

        #calculating plot_sample_ratio
        plotted_samples = int(period*num_output_waves)

        IQ_plots = []
        #Plotting the imaginary and real values
        fig = plt.GridSpec(1, 28, wspace=1, hspace=0.3)

        plt.suptitle("Individual Channels' Amplitude versus Time for Run {}".format(counter))
        ax1 = plt.subplot(fig[0:1, 0:5])
        ax2 = plt.subplot(fig[0:1, 6:11])
        ax3 = plt.subplot(fig[0:1, 12:17])
        ax4 = plt.subplot(fig[0:1, 18:23])

        IQ_plots.append(subPlotIQs(x_time[0:plotted_samples], reals[0][0:plotted_samples], imags[0][0:plotted_samples], best_fit_reals[0][0:plotted_samples], best_fit_imags[0][0:plotted_samples], offset_reals[0], offset_imags[0], ax1, "Channel A"))
        IQ_plots.append(subPlotIQs(x_time[0:plotted_samples], reals[1][0:plotted_samples], imags[1][0:plotted_samples], best_fit_reals[1][0:plotted_samples], best_fit_imags[1][0:plotted_samples], offset_reals[1], offset_imags[1], ax2, "Channel B"))
        IQ_plots.append(subPlotIQs(x_time[0:plotted_samples], reals[2][0:plotted_samples], imags[2][0:plotted_samples], best_fit_reals[2][0:plotted_samples], best_fit_imags[2][0:plotted_samples], offset_reals[2], offset_imags[2], ax3, "Channel C"))
        IQ_plots.append(subPlotIQs(x_time[0:plotted_samples], reals[3][0:plotted_samples], imags[3][0:plotted_samples], best_fit_reals[3][0:plotted_samples], best_fit_imags[3][0:plotted_samples], offset_reals[3], offset_imags[3], ax4, "Channel D"))
        ax4.legend(loc='upper left', bbox_to_anchor=(1.05,0.5))

        IQ_plots = np.asarray(IQ_plots)
        # plt.show()
        #Rasterizes the plot/figures and converts to png)
        plotToPdf(plt, ("IQPlots_" + formattedDate), counter, pdf, plot_img_width, plot_img_height, plot_img_pos_x, plot_img_pos_y)
        plt.clf()

        #Table of IQ info
        IQ_table_info = [["IQ Data: "],
                            ["Channel", "Real Frequency", "Real Amplitude"],
                           ["A", np.round(freq_reals[0], decimal_round), np.round(ampl_reals[0], decimal_round)],
                           ["B", np.round(freq_reals[1], decimal_round), np.round(ampl_reals[1], decimal_round)],
                           ["C", np.round(freq_reals[2], decimal_round), np.round(ampl_reals[2], decimal_round)],
                           ["D", np.round(freq_reals[3], decimal_round), np.round(ampl_reals[3], decimal_round)]]

        IQ_table = Table(IQ_table_info, style=[('GRID', (0,1), (2,5), 1, colors.black),
                                ('BACKGROUND', (0, 1), (2,1), '#D5D6D5')])

        IQ_table.wrapOn(pdf, IQ_width, IQ_height)
        IQ_table.drawOn(pdf, IQ_table_x, IQ_table_y)


        ##FFT PLOT AND TABLE
        pdf.showPage()
        page_count += 1
        header(pdf)
        #Positional
        fft_pos_x, fft_pos_y = 10, 135
        fft_width, fft_height = 650, 450
        max_peak_width, max_peak_height = 80, 100
        max_peak_x, max_peak_y = fft_pos_x, fft_pos_y - max_peak_height

        #Calculating the x and y fft and finding the 5 maxs
        max_fives = []
        max_fives_rounded = []
        fft_x = []
        fft_y = []
        for i in range(0, num_channels):
            x, y = fftValues(x_time, reals[i], imags[i])
            fft_x.append(x)
            fft_y.append(y)
            rounded, normal = fivePeaks(fft_x[i], fft_y[i], ampl_vec[i])
            max_fives_rounded.append(rounded) #Allows for charts to be printed nicer
            max_fives.append(normal)#Doesn't cut off important values for math

        max_fives = np.asarray(max_fives)
        max_fives_rounded = np.asarray(max_fives_rounded)
        fft_x = np.asarray(fft_x)
        fft_y = np.asarray(fft_y)

        FFT_plots = []
        #Plotting the individual FFT Plots
        fig = plt.GridSpec(1, 44, wspace=5, hspace=0.3)
        plt.suptitle("Individual Channels' FFTs for Run {}".format(counter))\

        #Noise Floor
        noise_floor = noiseFloor(fft_y)
        noise_floor = np.asarray(np.asarray(noise_floor))

        ax1 = plt.subplot(fig[0:1, 0:10])
        ax2 = plt.subplot(fig[0:1, 11:21])
        ax3 = plt.subplot(fig[0:1, 22:32])
        ax4 = plt.subplot(fig[0:1, 33:43])
        fft_x = np.asarray(fft_x)
        fft_y = np.asarray(fft_y)
        FFT_plots.append(subPlotFFTs(fft_x[0], fft_y[0], ax1, "Channel A", max_fives[0], noise_floor[0]))
        FFT_plots.append(subPlotFFTs(fft_x[1], fft_y[1], ax2, "Channel B", max_fives[1], noise_floor[1]))
        FFT_plots.append(subPlotFFTs(fft_x[2], fft_y[2], ax3, "Channel C", max_fives[2], noise_floor[2]))
        FFT_plots.append(subPlotFFTs(fft_x[3], fft_y[3], ax4, "Channel D", max_fives[3], noise_floor[3]))

        FFT_plots = np.asarray(FFT_plots)
        #Rasterizes the plot/figures and converts to png)
        plotToPdf(plt, ("FFTPlots_" + formattedDate), counter, pdf, fft_width, fft_height, fft_pos_x, fft_pos_y)
        plt.clf()

        #Tables stuff
        max_peak_table_info = [["Top Five Peaks:"],
                                ["Channel A", "Channel B", "Channel C", "Channel D"],
                                [str(max_fives_rounded[0][0]), str(max_fives_rounded[0][1]), str(max_fives_rounded[0][2]), str(max_fives_rounded[0][3])],
                                [str(max_fives_rounded[1][0]), str(max_fives_rounded[1][1]), str(max_fives_rounded[1][2]), str(max_fives_rounded[1][3])],
                                [str(max_fives_rounded[2][0]), str(max_fives_rounded[2][1]), str(max_fives_rounded[2][2]), str(max_fives_rounded[2][3])],
                                [str(max_fives_rounded[3][0]), str(max_fives_rounded[3][1]), str(max_fives_rounded[3][2]), str(max_fives_rounded[3][3])]]

        peak_table = Table(max_peak_table_info, style=[('GRID', (0,1), (4,8), 1, colors.black),
                                ('BACKGROUND', (0,1), (6,1), '#D5D6D5')])
        #print(type(peak_table))
        peak_table.wrapOn(pdf, max_peak_width, max_peak_height)
        peak_table.drawOn(pdf, max_peak_x  + 40, max_peak_y)

        # table_title = pdf.beginText()
        # table_title.setTextOrigin(max_peak_x, max_peak_y - max_peak_height - 3)
        # table_title.setFont(font, gen_font_size)
        # table_title.textLine(text=("Top Five Peaks: "))
        # pdf.drawText(table_title)

        ##All merged plots
        pdf.showPage()
        page_count += 1
        header(pdf)

        tgth_width, tgth_height = 800, 600
        tgth_x, tgth_y = 2, 3

        #Setting the plot
        fig = plt.GridSpec(17, 45, wspace=5, hspace=0.3)
        ax1 = plt.subplot(fig[0:17, 0:20])
        ax2 = plt.subplot(fig[0:17, 20:40])

        colours = ['royalblue', 'maroon', 'darkolivegreen', 'mediumvioletred']

        #plotting them all by pulling previous data
        for i, colour in zip(range(4), colours):
            ax1.set_title("All Channels - Real Data")
            ax1.plot(IQ_plots[i].get_xdata(), IQ_plots[i].get_ydata(), '-', color=colour, markersize=0.2, label="Channel {}".format(i))
            ax2.set_title("All Channels - FFT Graphs")
            ax2.plot(FFT_plots[i].get_xdata(), FFT_plots[i].get_ydata(), '-', color=colour, markersize=0.2, label="Channel {}".format(i))

        ax2.legend(loc='upper left', bbox_to_anchor=(1.05,0.5))

        # plt.show()
        #Rasterizes the plot/figures and converts to png)
        plotToPdf(plt, ("TogetherPlots_" + formattedDate), counter, pdf, tgth_width, tgth_height, tgth_x, tgth_y)
        plt.clf()

        ##SUMMARY PAGE
        header(pdf)
        page_count += 1
        pdf.showPage()

        stats_summary_x, stats_summary_y = 15, 500
        nf_table_width, nf_table_height = 600, 20
        nf_x, nf_y = stats_summary_x, stats_summary_y -150

        stats_summary = pdf.beginText()
        stats_summary.setTextOrigin(stats_summary_x, stats_summary_y)
        stats_summary.setFont(font, 2*gen_font_size)
        stats_summary.textLine(text=("Noise Floor Data: "))
        stats_summary.setFont(font, 1.75*gen_font_size)
        stats_summary.textLine("Maximum is Channel " + str(np.argmax(noise_floor)) + " with value " + str(max(noise_floor)))
        stats_summary.textLine("Minimum is Channel " + str(np.argmin(noise_floor)) + " with value " + str(min(noise_floor)))
        stats_summary.textLine("The Mean of the Noise Floor Data is " + str(np.mean(noise_floor)))

        pdf.drawText(stats_summary)

        #Tables stuff
        nf_table_info = [["All Noise Floor Data:"],
                                ["Channel A", "Channel B", "Channel C", "Channel D"],
                                [str(round(noise_floor[0], decimal_round)), str(round(noise_floor[1], decimal_round)), str(round(noise_floor[2], decimal_round)), str(round(noise_floor[3], decimal_round))]]

        nf_table = Table(nf_table_info, style=[('GRID', (0,1), (4,8), 1, colors.black),
                                ('BACKGROUND', (0,1), (6,1), '#D5D6D5')])
        #print(type(peak_table))
        nf_table.wrapOn(pdf, nf_table_width, nf_table_height)
        nf_table.drawOn(pdf, nf_x, nf_y)

        #Top 5 Peaks info
        #SNR DATA
        snr_width, snr_height = 100, 315
        snr_x, snr_y = nf_x, nf_y - snr_height
        fft_snr = []
        for i in range(num_channels):
            fft_snr.append(toSNR(fft_y[i]))

        fft_snr = np.asarray(fft_snr)

        #At this point, the snr shoud be in order of max peak
        summary_info.append((max_fives[0][0][0], max_fives[0][0][1], fft_snr[0]))

        #Sorting according to SNR
        quickSort(fft_snr, 0, len(fft_snr)-1, max_fives_rounded)


        #Tables stuff
        snr_table_info = [["More Top Peak Information:"],
                          ["Channel A: "],
                          ["Location (Hz)", str(max_fives_rounded[0][0][0]), str(max_fives_rounded[0][1][0]), str(max_fives_rounded[0][2][0]), str(max_fives_rounded[0][3][0])],
                          ["Amplitude (dB)", str(max_fives_rounded[0][0][1]), str(max_fives_rounded[0][1][1]), str(max_fives_rounded[0][2][1]), str(max_fives_rounded[0][3][1])],
                          ["SNR (dBc)", str(fft_snr[0])],
                          ["Channel B: "],
                          ["Location (Hz)", str(max_fives_rounded[1][0][0]), str(max_fives_rounded[1][1][0]), str(max_fives_rounded[1][2][0]), str(max_fives_rounded[1][3][0])],
                          ["Amplitude (dB)", str(max_fives_rounded[1][0][1]), str(max_fives_rounded[1][1][1]), str(max_fives_rounded[1][2][1]), str(max_fives_rounded[1][3][1])],
                          ["SNR (dBc)", str(fft_snr[1])],
                          ["Channel C: "],
                          ["Location (Hz)", str(max_fives_rounded[2][0][0]), str(max_fives_rounded[2][1][0]), str(max_fives_rounded[2][2][0]), str(max_fives_rounded[2][3][0])],
                          ["Amplitude (dB)", str(max_fives_rounded[2][0][1]), str(max_fives_rounded[2][1][1]), str(max_fives_rounded[2][2][1]), str(max_fives_rounded[2][3][1])],
                          ["SNR (dBc)", str(fft_snr[2])],
                          ["Channel D: "],
                          ["Location (Hz)", str(max_fives_rounded[3][0][0]), str(max_fives_rounded[3][1][0]), str(max_fives_rounded[3][2][0]), str(max_fives_rounded[3][3][0])],
                          ["Amplitude (dB)", str(max_fives_rounded[3][0][1]), str(max_fives_rounded[3][1][1]), str(max_fives_rounded[3][2][1]), str(max_fives_rounded[3][3][1])],
                          ["SNR (dBc)", str(fft_snr[3])]]

        snr_table = Table(snr_table_info, style=[('GRID', (0,2), (5,4), 1, colors.black),
                                               ('GRID', (0,6), (5,8), 1, colors.black),
                                               ('GRID', (0,10), (5,12), 1, colors.black),
                                               ('GRID', (0,14), (5,16), 1, colors.black),
                                            ('BACKGROUND', (0,1), (6,1), '#D5D6D5'),
                                            ('BACKGROUND', (0,5), (6,5), '#D5D6D5'),
                                            ('BACKGROUND', (0,9), (6,9), '#D5D6D5'),
                                            ('BACKGROUND', (0,13), (6,13), '#D5D6D5')])

        #print(type(peak_table))
        snr_table.wrapOn(pdf, snr_width, snr_height)
        snr_table.drawOn(pdf, snr_x, snr_y)

    #Pass/Fail final page
    pdf.showPage()
    page_count += 1
    header(pdf)

    #Positionalgalues
    title_font_size = 26
    title_x, title_y = 100, 575

    #Setting up title on Title Page
    title = pdf.beginText()
    title.setTextOrigin(title_x, title_y)
    title.setFont(font, title_font_size)
    title.textLine(text=("Summary Page for: " + unit_name + " - " + formattedDate))
    pdf.drawText(title)

    print(summary_info)




    os.chdir(output_dir) #Ensuring we are saving in the output directory
    pdf.save() #saving the pdf

main(gen.ship_test_tx(4))









