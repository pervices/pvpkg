#IMPORTING LIBRARIES AND MODULES
#Per Vices Imports
from common import sigproc
from common import engine
from common import generator as gen

#GNU radio
from gnuradio import uhd

#Basic imports
import time, datetime
import os
import sys
import subprocess
import threading
import argparse
import numpy as np
import matplotlib
matplotlib.use("TkAgg") #Manually setting up matplotlib to uge the TkAGG in the bkgrd
from matplotlib import rcParams
from sigfig import round as sig

#PDF IMPORTS
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import Image, Paragraph, Table, Frame, TableStyle

#Plot and Data imports
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

# from scipy.optimize import curve_fit
from lmfit import Model, minimize, Parameters, create_params #apparently better for discrete things
from scipy.signal.windows import blackman
from scipy.fft import fft, fftfreq, fftshift
from scipy import signal
from reportlab.lib.utils import ImageReader
from scipy.signal import find_peaks

import traceback

begin_cutoff_waves = 20 #how many waves to cut off before tracking data

#USER SET VARIABLES
channel_names = []

#Setup argument parsing
parser = argparse.ArgumentParser(description = "A basic loopback test verifying gain/frequency tuning works")

parser.add_argument('-d', '--displayed_waves', default=2, type=int, help="Number of wave to print on the graphs")
parser.add_argument('-s', '--sigfigs', default=3, type=int, help="Number of significant digits to display")
#TODO: verify this is a reasonable default value
parser.add_argument('-n', '--snr', default=20, type=int, help="Minimum signal to noise ratio in dBc")
#TODO: verify this is a reasonable default value
parser.add_argument('-o', '--freq_threshold', default=1, type=int, help="Allowable difference in wave frequency from the target")
parser.add_argument('-q', '--spur_threshold', default=20, type=int, help="Minimum acceptable difference between the desired signal and the strongest spur")
parser.add_argument('-g', '--gain_threshold', default = 5, type=int,  help="The maximum allowable difference in gain between channels")
parser.add_argument('-a', '--serial', required=True, help="Serial number of the unit")
parser.add_argument('-p', '--product', required=True, help="The product to be tested. v for Vaunt, t for Tate")
parser.add_argument('-c', '--num_channels', default = 4, type=int,  help="The number of channels to test. Will test ch a, ch b, ...")


args = parser.parse_args()

num_output_waves = args.displayed_waves

#Validates num_output_waves
try:
    assert 1 <= num_output_waves <= 4
except AssertionError:
    print("ERROR: Can only display 1 to 4 waves per graph. Try again: ")
    num_output_waves = int(input("How many waves do you want shown on IQ graphs? "))
except ValueError:
    print("ERROR: Please only input integers. Try again: ")
    num_output_waves = int(input("How many waves do you want shown on IQ graphs? "))

sigfigs = args.sigfigs

# Validate number of sigfigs
try:
    assert 1 <= sigfigs <= 5
except ValueError:
    sys.exit("ERROR: Please only input integers. Try again: ")
except AssertionError:
    sys.exit("ERROR: For formatting, please input a value within 1 to 5. Try again:")

snr_min_check = args.snr

#Frequency offset threshold
freq_check_threshold = args.freq_threshold

spur_check_threshold = args.spur_threshold

gain_check_threshold = args.gain_threshold

serial_num = args.serial

#Making file and doc title
date = datetime.datetime.now()
formattedDate = date.isoformat("-", "minutes")
file_title = "ship_report_" + serial_num + "_" + formattedDate + ".pdf"
doc_title = "ship_report_" + serial_num + "_" + formattedDate

#SETTING UP PATH DIRECTORIES
current_dir = os.getcwd()
output_dir = current_dir + "/ship_reports"
plots_dir = output_dir + "/plots_" + formattedDate
os.makedirs(output_dir, exist_ok=True)
os.makedirs(plots_dir, exist_ok=True)

#Asking what test to run and how many channels to run
#NOTE: I think this could be expanded to just choosing which channels on the unit to test
product = args.product
try:
    if (product != 't' and product != 'v'):
        raise(ValueError)
except:
    sys.exit("Invalid product. Only v (Vaunt) and t (Crimson) supported")

num_channels = args.num_channels
channel_names = ["Channel A", "Channel B", "Channel C", "Channel D", "Channel E", "Channel F", "Channel G", "Channel H"]
if(product == 'v'):
    max_channels = 4
if(product == 't'):
    max_channels = 8

try:
    assert 1 <= num_channels <= max_channels
except AssertionError:
    sys.exit("Invalid number of channels selected")

channel_names = channel_names[0:num_channels]

if(product == 'v'):
    generate = gen.ship_test_crimson(num_channels)
elif(product == 't'):
    generate = gen.ship_test_cyan(num_channels)

#Using the terminal to pull unit info
# os.system('rm ' + current_dir + '/shiptest_out.txt')
os.system('touch shiptest_out.txt')
os.system('uhd_usrp_info  -s > shiptest_out.txt')

#Using terminal grep to set unit data
server_ver = subprocess.getstatusoutput("cat shiptest_out.txt | grep 'Server Version' | cut --complement -d ':' -f1 ")[1]
fpga_ver = subprocess.getstatusoutput("cat shiptest_out.txt | grep 'FPGA' | cut --complement -d ':' -f1")[1]
UHD_ver = subprocess.getstatusoutput("cat shiptest_out.txt | grep 'UHD' | cut --complement -d 'g' -f1")[1]
unit_name = subprocess.getstatusoutput("cat shiptest_out.txt | grep 'Device Type' | cut --complement -d ':' -f1")[1]
unit_time = subprocess.getstatusoutput("cat shiptest_out.txt | grep -m1 'Date' | cut --complement -d ':' -f1")[1]
unit_rtm = subprocess.getstatusoutput("cat shiptest_out.txt | grep 'RTM' | cut --complement -d ':' -f1")[1]

#organizing info in order of time, tx, and rx using gterminal grep
os.system('uhd_usrp_info --all > shiptest_out.txt')
os.system("touch hold.txt")
os.system("grep '0/time/fw_version' shiptest_out.txt -A 15 > hold.txt")

#Setting up time array to hold board data
time = []
time.append(subprocess.getstatusoutput("cat hold.txt | grep 'Board Version' | cut --complement -d ':' -f1")[1])
time.append(subprocess.getstatusoutput("cat hold.txt | grep 'Branch' | cut --complement -d ':' -f1")[1])
time.append(subprocess.getstatusoutput("cat hold.txt | grep -m1 'Revision' | cut --complement -d 'g' -f1")[1])
time.append(subprocess.getstatusoutput("cat hold.txt | grep 'Date' | cut --complement -d ':' -f1")[1])
time.append(subprocess.getstatusoutput("cat hold.txt | grep 'MCU Serial' | cut --complement -d ':' -f1")[1])
time.append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse00' | cut --complement -d ':' -f1")[1])
time.append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse02' | cut --complement -d ':' -f1")[1])
time.append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse03' | cut --complement -d ':' -f1")[1])
time.append(subprocess.getstatusoutput("cat hold.txt | grep 'GCC' | cut --complement -d ':' -f1")[1])

#Setting up rx dictionary to hold board data
rx_info = {}
for i, name in zip(range(num_channels), channel_names): #NOTE: This might be more efficent with numpy arrays
    os.system("grep 'rx/{}/fw_version' shiptest_out.txt -A 15 > hold.txt".format(i))

    rx_info["RX: " + name] = []
    rx_info["RX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Board Version' | cut --complement -d ':' -f1")[1])
    rx_info["RX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Branch' | cut --complement -d ':' -f1")[1])
    rx_info["RX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep -m1 'Revision' | cut --complement -d 'g' -f1")[1])
    rx_info["RX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Date' | cut --complement -d ':' -f1")[1])
    rx_info["RX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'MCU Serial' | cut --complement -d ':' -f1")[1])
    rx_info["RX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse00' | cut --complement -d ':' -f1")[1])
    rx_info["RX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse02' | cut --complement -d ':' -f1")[1])
    rx_info["RX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse03' | cut --complement -d ':' -f1")[1])
    rx_info["RX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'GCC' | cut --complement -d ':' -f1")[1])


#Setting up tx dictionary to hold board data
tx_info = {}
for i, name in zip(range(num_channels), channel_names):
    os.system("grep 'tx/{}/fw_version' shiptest_out.txt -A 15 > hold.txt".format(i))
    tx_info["TX: " + name] = []
    tx_info["TX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Board Version' | cut --complement -d ':' -f1")[1])
    tx_info["TX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Branch' | cut --complement -d ':' -f1")[1])
    tx_info["TX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep -m1 'Revision' | cut --complement -d 'g' -f1")[1])
    tx_info["TX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Date' | cut --complement -d ':' -f1")[1])
    tx_info["TX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'MCU Serial' | cut --complement -d ':' -f1")[1])
    tx_info["TX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse00' | cut --complement -d ':' -f1")[1])
    tx_info["TX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse02' | cut --complement -d ':' -f1")[1])
    tx_info["TX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse03' | cut --complement -d ':' -f1")[1])
    tx_info["TX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'GCC' | cut --complement -d ':' -f1")[1])

#Removing the temp files from the systems
os.system("rm hold.txt")
os.system("rm shiptest_out.txt")

#Globals that will be changed later in the code - all -1 currently because they are dependent on the generator code
center_freq = -1
sample_rate = -1
sample_count = -1
tx_gain = -1
rx_gain = -1
being_cutoff = -1
summary_info = [] #[iteration][[freq][amplitude][snr]]
counter = 0 #Keeps track of run

#page variables
page_count = 1
graph_max = int(np.ceil(num_channels/4))
multi = (graph_max > 1)
#Page total based on the unit your testing
page_total = ((2*graph_max)+2)*(8*(product == 'V' or product == 'v') + 6*(product == 'T' or product == 't')) + graph_max


#Adding logo - more efficent to just initialize at beginning
h_img_data = open(current_dir + "/pervices-logo.png", "rb")
header_img = ImageReader(h_img_data)

#Formatting Variables - just so they're easily accessible
python_to_inch = 72
font = "Times-Roman"
gen_font_size = 12
bold_font = "Times-Bold"
rcParams['agg.path.chunksize'] = 115

'''Creates Title Page with board info, title, and unit info
PARAMS: pdf
RETURNS: NONE'''
def titlePage(pdf):

    #Positional Values
    title_font_size = 26
    title_x = 100
    title_y = 575
    list_font_size = 14
    list_x = title_x - 5
    list_y = title_y - 20
    logo_x, logo_y = 550, 450
    logo_width, logo_height = 200, 100
    board_width, board_height = 100, 100
    colWidth, rowHeight = (1.5*inch), (0.2*inch)
    board_x, board_y = 3, list_y - rowHeight*16.25

    #Setting up title on Title Page
    title = pdf.beginText()
    title.setTextOrigin(title_x, title_y)
    title.setFont(font, title_font_size)
    title.textLine(text=("Ship Test Report: " + unit_name + " - Serial Number: " + serial_num))
    pdf.drawText(title)

    #Printing out Important Details regarding the Machine
    #everything will be attached to unitList text object
    unitList = pdf.beginText(list_x, list_y)

    #Writing Date and TIme Version
    unitList.setFont(bold_font, list_font_size)
    unitList.textOut("Computer Date: ")
    unitList.setFont(font, list_font_size)
    unitList.textLine(formattedDate)

    #Writing UHD Version
    unitList.setFont(bold_font, list_font_size)
    unitList.textOut("UHD Version: ")
    unitList.setFont(font, list_font_size)
    unitList.textLine(UHD_ver)

    #writing rtm Version
    unitList.setFont(bold_font, list_font_size)
    unitList.textOut("RTM: ")
    unitList.setFont(font, list_font_size)
    unitList.textLine(unit_rtm)

    #writing Server Version
    unitList.setFont(bold_font, list_font_size)
    unitList.textOut("Server Version: ")
    unitList.setFont(font, list_font_size)
    unitList.textLine(server_ver)

    #writing FPGa Version
    unitList.setFont(bold_font, list_font_size)
    unitList.textOut("FPGA Version: ")
    unitList.setFont(font, list_font_size)
    unitList.textLine(fpga_ver)

    #writing Unit time
    unitList.setFont(bold_font, list_font_size)
    unitList.textOut("Unit Time: ")
    unitList.setFont(font, list_font_size)
    unitList.textLine(unit_time)
    pdf.drawText(unitList)

    #Drawing Logo
    pdf.drawImage(header_img, logo_x, logo_y, logo_width, logo_height)

    #Adding the time, tx, rx board info in a table
    board_styles = ([('GRID', (0,0), (num_channels+1, 9), 1, colors.black),
                    ('FONTSIZE', (1,4), (num_channels+1, 5),7.8),
                    ('BACKGROUND', (0, 0), (num_channels+1,0), '#D5D6D5'),
                    ('BACKGROUND', (0, 0), (0,9), '#D5D6D5')])

    #Time Board table
    board_info = [["Time Board Information: "], ["Board"], ["Branch"], ["Revision"], ["Date"], ["MCU Serial"], ["Fuse 00"], ["Fuse 02"], ["Fuse 03"], ["GCC"]]
    for z in range(len(time)):
        board_info[z+1].append((time[z]))

    board_table = Table(board_info, colWidths=colWidth, rowHeights=rowHeight, style=board_styles)
    board_table.wrapOn(pdf, board_width, board_height)
    board_table.drawOn(pdf, board_x, board_y)
    board_y -= rowHeight*11

    for z in range(graph_max): #This ensures theres columns per page

        if (z != 0): #If there are more than 4 channels, make another page for the board info
            board_x, board_y = 3, list_y - rowHeight*10
            global page_total
            page_total +=1
            global page_count
            page_count += 1
            pdf.showPage() #Page break on pdf
            pdf.drawText(title)
            pdf.drawImage(header_img, logo_x, logo_y, logo_width, logo_height)
            pg_x, pg_y = 650,10
            pg_num = pdf.beginText()
            pg_num.setTextOrigin(pg_x, pg_y)
            pg_num.setFont(font, 10)
            pg_num.textLine(text=("Page " + str(page_count) + " of " + str(page_total)))
            pdf.drawText(pg_num)

        start, end = z*4, (z*4)+4 #only have to be calculated once

        #Adding Tx Board Table
        board_info = [["TX Board Information: "], ["Board"], ["Branch"], ["Revision"], ["Date"], ["MCU Serial"], ["Fuse 00"], ["Fuse 02"], ["Fuse 03"], ["GCC"]]
        for i, name in zip(range(start, end), channel_names[start:end]):
            board_info[0].append(chr(65+i))
            for z in range(len(tx_info["TX: " + name])):
                board_info[z+1].append((tx_info["TX: " + name][z]))

        board_table = Table(board_info, rowHeights=rowHeight, style=board_styles)
        board_table.wrapOn(pdf, board_width, board_height)
        board_table.drawOn(pdf, board_x, board_y)
        board_y -= rowHeight*11

        #Adding Rx Board Table
        board_info = [["RX Board Information: "], ["Board"], ["Branch"], ["Revision"], ["Date"], ["MCU Serial"], ["Fuse 00"], ["Fuse 02"], ["Fuse 03"], ["GCC"]]

        for q, rxname in zip(range(start, end), channel_names[start:end]):
            board_info[0].append(chr(65+q))
            for z in range(len(rx_info["RX: " + rxname])):
                board_info[z+1].append((rx_info["RX: " + rxname][z]))

        board_table = Table(board_info, colWidths=colWidth, rowHeights=rowHeight, style=board_styles)
        board_table.wrapOn(pdf, board_width, board_height)
        board_table.drawOn(pdf, board_x, board_y)


'''Creates a header for each Run Page and the page number
PARAMS: pdf, it name
RETURNS: None
'''
def topOfPage(pdf, it):
    #Positionalgalues
    title_font_size = 26
    title_x, title_y = 80, 575

    #Setting up title
    title = pdf.beginText()
    title.setTextOrigin(title_x, title_y)
    title.setFont(font, title_font_size)
    title.textLine(text=("Run Number " + str(it) + " - Loopback On " + unit_name))
    pdf.drawText(title)

    #Positional Values
    header_font_size = 10
    header_x, header_y = 633, 584
    logo_width, logo_height = 75, 25
    logo_x, logo_y = header_x - logo_width - 2, header_y - 17
    pg_x, pg_y = 650,10

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
    pdf.drawText(pg_num)

    #positional values
    table_width = 400
    table_height = 50
    table_x = title_x - 5
    table_y = title_y - table_height

    #Table of input data
    data = [["Center Frequency (Hz)", "Wave Frequency (Hz)", "Sample Rate (SPS)", "Sample Count", "TX Gain (dB)", "RX Gain (dB)"],
            [center_freq, wave_freq, sample_rate, sample_count, tx_gain, rx_gain]]

    #Making and styling the table
    inputs = Table(data, style=[('GRID', (0,0), (6,1), 1, colors.black),
                                ('BACKGROUND', (0,0), (6,0), '#D5D6D5')])
    inputs.wrapOn(pdf, table_width, table_height)
    inputs.drawOn(pdf, table_x, table_y)

'''Plots the FFT subplots all in the same format
PARAMS: x, y, ax, imag, title
RETURNS: NONE'''
def subPlotFFTs(x, y, ax, title, max_four, nf):

    ax.set_title(title)
    ax.set_xlim(min(x), max(x))
    fft, = ax.plot(x, y, "-", color='crimson')
    ax.axhline(nf, markersize=0.5, alpha=0.3, label="Noise Floor")

    for i in range(len(max_four)):
        ax.plot(max_four[i][0], max_four[i][1], "x", label="Peak {}".format(i+1))

    return fft

'''Plots the IQ subplots all in the same format
PARAMS: x, real, ax, imag, best_fit_real, best_fit_imag, title
RETURNS: NONE'''
def subPlotIQs (x, real,imag, best_fit_real, best_fit_imag, offset_real, offset_imag, ax, title, period):
    ax.set_title(title)

    ax.axhline(y = offset_imag, markersize=0.025, color='indigo', alpha=0.4, label='Imaginary Offset')
    ax.axhline(y = offset_real, markersize=0.025, color='red', alpha=0.4, label='Real Offset')
    ax.plot(x, best_fit_imag, '-', markersize=0.1, color='darkmagenta', label="Imaginary Best Fit")
    bf_r, = ax.plot(x, best_fit_real, '-', markersize=0.1, color='indianred', label="Real Best Fit")
    ax.plot(x, real, '.', markersize=3, color='crimson', label="Real")
    ax.plot(x, imag, '.', markersize=3, color='purple', label="Imaginary")


    real_peaks = find_peaks(real, distance=period)
    imag_peaks = find_peaks(imag, distance=period)

    for r, i in zip(real_peaks[0], imag_peaks[0]):
        ax.axvline(x = x[r], linestyle='--', alpha=0.5, color='rosybrown', markersize=0.05)
        ax.text(x[r], max(best_fit_real) + (0.05*max(best_fit_real)), "\u2190" + str(sig(x[r], sigfigs=sigfigs)), fontsize=7, verticalalignment='top', )
        ax.axvline(x = x[i],  linestyle='--', alpha=0.5, color='darkslateblue',markersize=0.05)
        ax.text(x[i], min(best_fit_imag) + (min(best_fit_imag)*0.05), "\u2190" + str(sig(x[i], sigfigs=sigfigs)), fontsize=7, verticalalignment='top')

    return bf_r

'''
# Returns the residuals of a predicts sinewave
params['ampl']: predicted amplitude
params['freq']: predicted frequency
params['phase']: predicted phase shift
params['dc_offset']: predicted dc offset
actual_time: the x values from the wave to be fitted
actual_amplitude: the y values from the wave to be fitted
RETUNRS: y'''
def sineResiduals(params, actual_time, actual_amplitude, freq, dc_offset):
    ampl = params['ampl'].value
    phase = params['phase'].value

    # Predicted wave
    model = ampl*np.sin(2*np.pi*freq*(actual_time + phase)) + dc_offset #model for wave equation

    return model - actual_amplitude

'''Creates the line of best fit for the given x and y (normal data, not complx)
PARAMS: x,y
RETURNS: best_fit (y values of the line of best fit '''
def bestFit(x, raw_y, expected_freq):

    # Applies a filter to the signal so we are only looking at the relevant sinewave
    sos = signal.butter(2, [expected_freq * 0.95, expected_freq * 1.05], 'bandpass', output = 'sos', fs = sample_rate)
    y = signal.sosfiltfilt(sos, raw_y)

    max_loc = np.argmax(y)
    period = 1/expected_freq
    predicted_phase = x[max_loc] + (period/4)
    if(predicted_phase < 0):
        predicted_phase += period

    predicted_phase = predicted_phase % period

    dc_offset = y.mean()

    # Predicted amplitude must be above expected to avoid the minimizer going the wrong direction and ending up near 0
    params = create_params(phase={'value': predicted_phase, 'min': 0, 'max': period}, ampl={'value': y[max_loc], 'min': y[max_loc]/10, 'max' : y[max_loc] * 1.1})

    try:
        result = minimize(sineResiduals, params, args=(x,y,expected_freq, dc_offset), max_nfev=25)
    except:
        traceback.print_exc()
    model = result.params['ampl'].value*np.sin(2*np.pi*expected_freq*(x + result.params['phase'].value)) + dc_offset

    return model, (dc_offset, result.params['ampl'])

'''Creates the line of best fit for the given x and y (complex), intended to be called in its ownthread
PARAMS:
channel: The channel number
x: time axis
y_reals: real part of amplitude
y_imags: imaginary part of amplitude
expected_freq: expected frequency, used to determine initial guess

All parameters after this are used to store pseudo return values

best_fit_reals: Array for points on the real lobf for each channel
offset_reals: Array of DC offset for the real lobf for each channel
ampl_reals: Array of amplitude for the real lobf for each channel
freq_reals: Array of frequency for the real lobf for each channel
best_fit_imags: Array for points on the imaginary lobf for each channel
offset_imags: Array of DC offset for the imaginary lobf for each channel
ampl_imags: Array of amplitude for the imaginary lobf for each channel
freq_imags: Array of frequency for the real lobf for each channel
ampl_vec: ? TODO: figure this out

RETURNS none '''
def bestFitComplex(ch, x, y_real, y_imag, expected_freq, best_fit_reals, offset_reals, ampl_reals, best_fit_imags, offset_imags, ampl_imags, ampl_vec):

    #Gets best fit for real part of sinewave
    best_fit, param = bestFit(x, y_real, expected_freq)

    best_fit_reals[ch] = best_fit
    offset_reals[ch] = param[0]
    ampl_reals[ch] = param[1]

    #Gets best fit for complex part of sinewave
    best_fit, param = bestFit(x, y_imag, expected_freq)

    best_fit_imags.append((best_fit))
    offset_imags[ch] = param[0]
    ampl_imags[ch] = param[1]

    ampl_vec[ch] = np.sqrt(param[1]**2 + ampl_reals[len(ampl_reals)-1]**2)

'''Function passed to numpy when normalizing data (shifting the range to be up to 1)
Params:
a: the value to be normalized
peak: the maximum value of the dataset
Returns: ans'''
def safeNormalize(a, peak):
    if(peak != 0):
        return a/peak
    else:
        return 0

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
PARAMS:
channel: the index corresponding to the channle
x: time of the samples
real: real part samples for 1 channel
imag: imagninary part of samples for 1 channel

# The below are used as pseudo return values

fft_xs: array containing the x values for each channel. Writes the result to the channel specified
fft_ys: array containing the y values for each channel in dB. Writes the result to the channel specified
'''
def fftValues(channel, x, real, imag, fft_xs, fft_ys):

    #organizing data
    sort = np.argsort(x)
    sorted_real = real[sort]
    sorted_imag = imag[sort]
    x = x[sort]

    #Getting the magnitude
    mag = np.vectorize(magnitude)
    comp = np.vectorize(complex)
    fft_comp_y = comp(sorted_real, sorted_imag)*blackman(len(x))

    #Turning it into fft
    fft_data = np.fft.fft(fft_comp_y, len(x), norm="backward")
    fft_transform = np.fft.fftshift(fft_data)
    fft_y = abs(mag(fft_transform.imag, fft_transform.real))

    #Transform to dB - code incase there are zero values, but haven't needed to use in a while
    # bools_norms = list(map(isNotZero, norm_y))
    # np.place(norm_y, bools_norms, 20*np.log10(norm_y)) #does not log values that are 0
    fft_ys[channel] = 20*np.log10(abs(fft_y))

    #Setting up the X values
    fft_xs[channel] = np.fft.fftshift(np.fft.fftfreq(len(x), d=(sample_rate))) #NOTEL makin thing is if this is okay

    return

'''Turning the plot figure into a rasterized image and saving it to the directory
PARAMS: plot, title, counter, pdf
RETURNS: NONE'''
def plotToPdf(title, counter):

    #Saving plot to proper directory and converting to png
    os.chdir(plots_dir) #ensuring in right directory
    plt.gcf().set_size_inches(8, 5)

    plt.savefig((title + "_" + str(counter)), format='png', dpi=300)

    #Opening file as io bits, then translating them to image reader
    img_data = open(plots_dir + "/" + title + "_" + str(counter), "rb")
    img = ImageReader(img_data)

    return img

'''Finding the top peaks
PARAMS: y
RETURNS: max_four'''
def numPeaks(x, y, ampl, num):

    peaks, properties = find_peaks(y, height=ampl) #NOTE: What should I use as the height...
    x = np.asarray(x)
    y = np.asarray(y)

    maxs = []
    peaks_arrays = [x[peaks], y[peaks]]

    for i in range(num):
        if(len(peaks_arrays[1] != 0)):
            maxs_indiv = np.argmax(peaks_arrays[1])
            maxs.append([peaks_arrays[0][maxs_indiv], peaks_arrays[1][maxs_indiv]])
            peaks_arrays = np.delete(peaks_arrays, maxs_indiv, axis=1)
        else:
            maxs.append([0,0])

    return maxs

'''Intakes data to find the noise floor avge by removing top 20 peaks and averaging the rest
PARAM: Data
RETURNS: noise_floor_y'''
def noiseFloor(x, y, ampl):
    noise_floor = numPeaks(x, y, ampl, 20)
    return noise_floor

'''Squares the given values
PARMS: V
RETURNS: v**2'''
def square(v):
    return v**2

'''Turning the amplitudes of noise and signal and making the snr
PARAMS:y_vals
RETURNS: SNR in dB'''
def toSNR(noise, signal):
    return (signal - np.max(noise))

'''Splits and swaps elements for the sort function
PARAMS: array, low, high, other_array
RETURN: i +1'''
def partition(array, low, high, other_array):

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
            (array[i], array[j]) = (array[j], array[i])
            (other_array[i], other_array[j]) = (other_array[j], other_array[i])


    # Swap the pivot element with the greater element specified by i
    (array[i + 1], array[high]) = (array[high], array[i + 1])
    (other_array[i + 1], other_array[high]) = (other_array[high], other_array[i + 1])

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
        pi = partition(array, low, high, other_array)

        # Recursive call on the left of pivot
        quickSort(array, low, pi - 1, other_array)

        # Recursive call on the right of pivot
        quickSort(array, pi + 1, high, other_array)

'''Checks if the given is within the SNR bounds
PARAM:
a: the signal to noise ratio
RETURN: Boolean'''
def checkSNR(a):
    return (a > snr_min_check)

'''Checks if the freq is within desired location
PARAM:
a: The difference between that actual wave frequency and the target
RETURN: Bool'''
def checkFreq(a):
    return (a > -freq_check_threshold) and (a < freq_check_threshold)

'''Checks if the difference between the peak and the strongest spur is acceptable
PARAM:
desired_signal: The strength of the signal in dB
strongest_spur: The strength of the strongest spur in dB
RETURN: Bool'''
def checkSpur(peak_values, fail_threshold):
    for ch_peaks in peak_values:
        if ch_peaks[0][1] < (ch_peaks[1][1] + fail_threshold):
            return False
    return True

'''Checks if the difference between channels is acceptable
PARAM:
desired_signal: The strength of the signal in dB
strongest_spur: The strength of the strongest spur in dB
RETURN: Bool'''
def checkGainRelative(peak_values, fail_threshold):
    min_gain = float('inf')
    max_gain = float('-inf')
    for ch_peaks in peak_values:
        min_gain = min(ch_peaks[0][1], min_gain)
        max_gain = max(ch_peaks[0][1], max_gain)

    return (max_gain - min_gain) <= fail_threshold

'''Turns true into "Pass" and false into "fail"
PARAM: a
RETURN: Proper word'''
def isPass(a):
    if a:
        return "Pass"
    else:
        return "False"

'''Runs the tests and data collection, then calls other functions to tests and format the code outputs
PARAMS: iterations
RETURNS: NONE, it is the main function'''
def main(iterations):

    # Changes matplotlib backend. The default ktinker does not work headless
    matplotlib.use('PDF')

    #Create the PDF
    pdf = canvas.Canvas(file_title, pagesize=landscape(letter)) #Setting the page layout and file name
    pdf.setTitle(doc_title)

    #Make title page
    titlePage(pdf)

    # Stores a list containing the 4 peaks from each fft
    # Dimmensions:
    # 0: test iteration len = len(iterations)
    # 1: channel len = number of channels
    # 2: peak pair (peak location, magnitude dB) len = 4
    peaks_list = []

    #start of the testing
    for it in iterations: #Will iterate per Run
        global counter
        counter += 1

        #Initilize Important Arrays
        # Raw real and imaginary samples
        reals = []
        imags = []
        # Time of samples
        x_time = []

        ampl_vec = np.zeros(shape=(num_channels))

        #The data important to the real data
        best_fit_reals = [None] * num_channels
        offset_reals = np.zeros(shape=(num_channels))
        ampl_reals = np.zeros(shape=(num_channels))

        #Data i
        best_fit_imags = []
        offset_imags = np.zeros(shape=(num_channels))
        ampl_imags = np.zeros(shape=(num_channels))

        # x (frequency) values of the fft for each channel
        fft_x = [None] * num_channels
        # y (magnitude) values of the fft for each channel
        fft_y = [None] * num_channels

        gen.dump(it) #pulls info from generator

        #SETING UP TESTS AND GETTING INPUTS
        global sample_rate
        sample_rate = int(it["sample_rate"])
        global sample_count
        sample_count = int(it["sample_count"])
        tx_stack = [(5.0 , sample_rate)] #Equivalent to 1 second
        rx_stack = [(5.25, sample_count)] #TODO: Maybe add the burst start times to table - or title page

        vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)

        period_samples = int(round(1/(it["wave_freq"]/it["sample_rate"])))
        begin_cutoff = int(period_samples*begin_cutoff_waves)


        #X values
        x = np.linspace(start = begin_cutoff/sample_rate, stop = sample_count/sample_rate, num = sample_count - begin_cutoff, endpoint = True) # Vector containing time of each sample in s
        # Samples before begin_cuttoff are ignored to give time for rx to become steady,this may be uneccessary since rx starts after tx so it should be steady anyway
        x_time = np.asarray(x*1000000000) # Converts s to ns

        # Extracts the data from each channel
        for ch, channel in enumerate(vsnk):
            real = np.asarray([datum.real for datum in channel.data()])
            imag = np.asarray([datum.imag for datum in channel.data()])

            # Adds samples to an array of channel samples, ommiting the first few samples
            reals.append(real[begin_cutoff:])
            imags.append(imag[begin_cutoff:])

        #Making them all np.arrays for efficency
        # TODO: make the arrays start as numpy arrays so this conversion isn't needed
        reals = np.asarray(reals)
        imags = np.asarray(imags)

        # Threads for the finding lobf for each channel in the time domain
        time_fitting_threads = []
        fft_threads = []
        for ch in range(num_channels):
            # Starts time domain fitting threads
            time_fitting_threads.append(threading.Thread(target = bestFitComplex, args = (ch, x, reals[ch], imags[ch], it["wave_freq"], best_fit_reals, offset_reals, ampl_reals, best_fit_imags, offset_imags, ampl_imags, ampl_vec)))
            time_fitting_threads[-1].start()

            # Starts fft threads
            fft_threads.append(threading.Thread(target = fftValues, args = (ch, x_time, reals[ch], imags[ch], fft_x, fft_y)))
            fft_threads[-1].start()


        
        # Determines the range of the y axis to plot
        # TODO: get max and min of the displayed range, currently it gets the max and min of everything
        amplYTop = max(reals.max(), imags.max()) * 1.1
        amplYBottom = min(reals.min(), imags.min()) * 1.1

        #Setting up the global variables to be what the test runs'
        global center_freq
        center_freq = int(it["center_freq"])
        global wave_freq
        wave_freq = int(it["wave_freq"])
        global tx_gain
        tx_gain = int(it["tx_gain"])
        global rx_gain
        rx_gain = int(it["rx_gain"])

        #This variable ensures only the number of waves requested will appear on the plots
        plotted_samples = int(period_samples*num_output_waves)

        for thread in time_fitting_threads:
            thread.join()

        # Moved here instead of later because of possible problematic interaction it matplotlib
        for thread in fft_threads:
            thread.join()

        #PDF PREP: Doing the plotting of FFT and IQ prior to making pdf pages to enable having the "together plot" as the first page
        #Plotting IQ Data, but not putting on pdf
        IQ_plots = []
        IQ_plt_img = []
        fig = plt.GridSpec(1, 68, wspace=0.3, hspace=0.3)
        axis = []
        for z in range(graph_max): #Splits the plots up to maximum 4 per page

            plt.suptitle("Individual Channels' Amplitude versus Time for Run {}".format(counter))
            # Padding is to prevent overlap with subplot (for the individual graphs) ticks
            plt.xlabel("Time (nS)", labelpad = 20)
            plt.ylabel("Amplitude(fractional)", labelpad = 40)

            # Hides the axis of the holding plot used to contain the individual plots
            plt.xticks([])
            plt.yticks([])

            #Variables to allow for flexibilty in the code
            start, end = z*4,(z*4)+4
            ax_st, ax_end = 0, 15

            #The actual plotting of the graphs
            for i, title in zip(range(start, end), channel_names[start:end]):
                axis.append(plt.subplot(fig[0:1, ax_st:ax_end])) #Each run will add the next plot area to the axis
                
                # Sets the y axis of each of the individual plots to be the same
                axis[-1].set_ylim(bottom = amplYBottom, top = amplYTop, auto = False)
                
                IQ_plots.append(subPlotIQs(x_time[0:plotted_samples], reals[i][0:plotted_samples], imags[i][0:plotted_samples], best_fit_reals[i][0:plotted_samples], best_fit_imags[i][0:plotted_samples], offset_reals[i], offset_imags[i], axis[i], title, period_samples))
                ax_st = ax_end + 2
                ax_end = ax_st + 15

            #Gets the byte data for the pdf images
            IQ_plt_img.append(plotToPdf(("IQPlots_" + formattedDate), counter))
            plt.clf()

        IQ_plots = np.asarray(IQ_plots)

        # Four highest points in the fft for each channel
        max_fours = []
        # noise of each channel
        noise_floor = []

        #Plotting FFT Data (not putting on page)
        #Calculating the x and y fft and finding the 5 maxs
        std = []

        fft_x = np.asarray(fft_x)
        fft_y = np.asarray(fft_y)

        for i in range(num_channels):
            max_fours.append(numPeaks(fft_x[i], fft_y[i], ampl_vec[i], 4))
            #Noise Floor and std- in db
            noise_floor.append(noiseFloor(fft_x[i], fft_y[i], ampl_vec[i]))
        max_fours = np.asarray(max_fours)
        peaks_list.append(max_fours)
        noise_floor = np.asarray(noise_floor)
        std = np.asarray(std)

        # Determines the range of the y axis to plot
        # TODO: get max and min of the displayed range, currently it gets the max and min of everything
        amplYTop = fft_y.max() * 1.1
        amplYBottom = fft_y.min() * 1.1

        FFT_plots = []
        FFT_plt_img = []
        axis.clear()
        for z in range(graph_max):
            #Splits the plots up to maximum 4 per page
            start, end = z*4,(z*4)+4
            ax_st, ax_end = 0, 15
            #Plotting the individual FFT Plots
            plt.suptitle("Individual Channels' FFTs for Run {}".format(counter))
            # Padding is to prevent overlap with subplot (for the individual graphs) ticks
            plt.xlabel("Frequency (MHz)", labelpad = 20)
            plt.ylabel("Magnitude (dB)", labelpad = 40)

            # Hides the axis of the holding plot used to contain the individual plots
            plt.xticks([])
            plt.yticks([])

            for i, title in zip(range(start, end), channel_names[start:end]):
                axis.append(plt.subplot(fig[0:1, ax_st:ax_end]))
                
                # Sets the y axis of each of the individual plots to be the same
                axis[-1].set_ylim(bottom = amplYBottom, top = amplYTop, auto = False)

                try:
                    FFT_plots.append(subPlotFFTs(fft_x[i], fft_y[i], axis[i], title, max_fours[i], np.mean(noise_floor[1])))
                    ax_st = ax_end + 2
                    ax_end = ax_st + 15
                except:
                    break
                #Rasterizes the plot/figures and converts to png)
            FFT_plt_img.append(plotToPdf(("FFTPlots_" + formattedDate), counter))
            plt.clf()

        FFT_plots = np.asarray(FFT_plots)

        #MAKING THE ACTUAL PDF
        #SECTION ONE OF RUNS: Merged Plots
        pdf.showPage()
        global page_count
        page_count += 1
        topOfPage(pdf, str(counter))

        tgth_width, tgth_height = 700, 450
        tgth_x, tgth_y = 2, 30

        #Setting the plot
        fig = plt.GridSpec(17, 45, wspace=10)
        ax1 = plt.subplot(fig[0:17, 0:20])
        ax2 = plt.subplot(fig[0:17, 20:40])

        colours = ['royalblue', 'maroon', 'darkolivegreen', 'mediumvioletred']

        #plotting them all by pulling previous data
        for i, colour in zip(range(num_channels), colours):
            # Combined amplitude plot
            ax1.set_title("All Channels - Real Data")
            ax1.set_xlabel("Time (nS)")
            ax1.set_ylabel("Amplitude(fraction of max)")
            ax1.plot(IQ_plots[i].get_xdata(), IQ_plots[i].get_ydata(), '-', color=colour, markersize=0.2, label="Channel {}".format(i))

            # Combined frequency plot
            ax2.set_title("All Channels - FFT Graphs")
            ax2.set_xlabel("Frequency (MHz)")
            ax2.set_ylabel("Magnitude (dB)")
            ax2.plot(FFT_plots[i].get_xdata(), FFT_plots[i].get_ydata(), '-', color=colour, markersize=0.2, label="Channel {}".format(i))

        ax2.legend(loc='upper left', bbox_to_anchor=(1,0.5))

        #Rasterizes the plot/figures and converts to png)
        tgth_plt_img = plotToPdf(("TogetherPlots_" + formattedDate), counter)
        pdf.drawImage(tgth_plt_img, tgth_x, tgth_y, tgth_width, tgth_height)
        plt.clf()
        plt.close()

        #SECTION TWO OF RUN: Plotting the Amplitude vs Time
        #Positional Values

        plot_img_width, plot_img_height = 700, 450
        plot_img_pos_x,  plot_img_pos_y = 2, 60
        IQ_width, IQ_height = 250, 105
        IQ_table_x, IQ_table_y = 5,5

        #graphs and table dependent on number of channels
        for z in range(graph_max):
            pdf.showPage() #Page break on pdf
            page_count += 1
            topOfPage(pdf, str(counter))
            start, end = z*4, (z*4)+4

            pdf.drawImage(IQ_plt_img[z], plot_img_pos_x, plot_img_pos_y, plot_img_width, plot_img_height)

            #Table of IQ info
            IQ_table_info = [["IQ Data: "],["Channel"], ["Ampl I (fractional)"], ["Ampl Q (fractional)"]]

            for i in range(start, end):
                # try:
                IQ_table_info[1].append((chr(65+i)))
                IQ_table_info[2].append(sig(ampl_reals[i], sigfigs=sigfigs))
                IQ_table_info[3].append(sig(ampl_imags[i], sigfigs=sigfigs))

                IQ_table = Table(IQ_table_info, style=[('GRID', (0,1), (num_channels+1,4), 1, colors.black),
                                                    ('BACKGROUND', (0, 1), (num_channels+1,1), '#D5D6D5')])
                # except:
                    # break

            IQ_table.wrapOn(pdf, IQ_width, IQ_height)
            IQ_table.drawOn(pdf, IQ_table_x, IQ_table_y)


        #SECTION THREE OF RUN: Plotting Amplitude vs Frequency
        #Positional
        fft_pos_x, fft_pos_y = 10, 100
        fft_width, fft_height = 700, 420
        max_peak_width, max_peak_height = 80, 50
        max_peak_x, max_peak_y = 2, 5

        #making graphs and table dependent on number of channels
        for z in range(graph_max):
            pdf.showPage()
            page_count += 1
            topOfPage(pdf, str(counter))
            start, end = z*4, (z*4)+4
            pdf.drawImage(FFT_plt_img[z], fft_pos_x, fft_pos_y, fft_width, fft_height)

            #Tables stuff
            max_peak_table_info = [["Top Peaks (Frequencty, Amplitude):"], ["Channel"], ["Highest Peak"], ["Second Highest"], ["Third Highest"], ["Fourth Heighest"]]
            for i in range(start, end):
                try:
                    max_peak_table_info[2].append(str((sig(max_fours[i][0][0], sigfigs=sigfigs), sig(max_fours[i][0][1], sigfigs=sigfigs))))
                    max_peak_table_info[3].append(str((sig(max_fours[i][1][0], sigfigs=sigfigs), sig(max_fours[i][1][1], sigfigs=sigfigs))))
                    max_peak_table_info[4].append(str((sig(max_fours[i][2][0], sigfigs=sigfigs), sig(max_fours[i][2][1], sigfigs=sigfigs))))
                    max_peak_table_info[5].append(str((sig(max_fours[i][3][0], sigfigs=sigfigs), sig(max_fours[i][3][1], sigfigs=sigfigs))))
                    max_peak_table_info[1].append((chr(65+i)))

                except:
                    break

            peak_table = Table(max_peak_table_info, style=[('GRID', (0,1), (num_channels+1,5), 1, colors.black),
                                    ('BACKGROUND', (0,1), (num_channels+1,1), '#D5D6D5')])
            peak_table.wrapOn(pdf, max_peak_width, max_peak_height)
            peak_table.drawOn(pdf, max_peak_x, max_peak_y)

        ##SECTION FOUR OF RUNS: SUMMARY PAGE
        pdf.showPage()
        page_count += 1
        topOfPage(pdf, str(counter))

        #NF stuff
        nf_table_width, nf_table_height = 80, 500
        nf_x, nf_y = 10, 400

        #SNR DATA
        snr_width, snr_height = 100, 100
        fft_snr = []
        for i in range(num_channels):
            fft_snr.append(toSNR(noise_floor[i][1], max_fours[i][0][1]))

        fft_snr = np.asarray(fft_snr)

        #At this point, the snr shoud be in order of max peak
        summary_info.append((max_fours[0][0][0], max_fours[0][0][1], fft_snr[0]))

        #Sorting according to SNR
        max_top = []
        for first_max in max_fours:
            max_top.append((first_max[0][0], first_max[0][1]))

        quickSort(fft_snr, 0, num_channels-1 , max_top) #X also gets sorted, so that the p/f is easier to check

        #Tables stuff
        for z in range(graph_max): #NOTE: It doesn't have to use graph max here, any value with the layout should be fine
            snr_x, snr_y = nf_x, nf_y - snr_height
            start, end = z*4, (z*4)+num_channels
            nf_table_info = [["All Noise Floor Data :"], ["Channel"],["Maximum"], ["Minimum"], ["Mean"], ["Diff to A"], ["STD"]]
            mean_a = np.mean(noise_floor[0][1])
            snr_table_info = [["Top Peak Information", "(Based on Highest SNR):"], ["Channel"], ["Location (Hz)"], ["Amplitude (dB)"], ["SNR (dBc)"]]
            snr_style = []

            for i in range(start, end):
                #Calculations for Noisefloor
                max_loc = np.argmax(noise_floor[i][1])
                min_loc = np.argmin(noise_floor[i][1])
                mean = np.mean(noise_floor[i][1])

                #Inputting data into noise floor table
                nf_table_info[1].append((chr(65+i)))
                nf_table_info[2].append(str((sig(noise_floor[i][0][max_loc], sigfigs=sigfigs), sig(noise_floor[i][1][max_loc], sigfigs=sigfigs))))
                nf_table_info[3].append(str((sig(noise_floor[i][0][min_loc], sigfigs=sigfigs), sig(noise_floor[i][1][min_loc], sigfigs=sigfigs))))
                nf_table_info[4].append(str(sig(mean, sigfigs=sigfigs)))
                nf_table_info[5].append(str(sig(mean - mean_a, sigfigs=sigfigs)))
                nf_table_info[6].append(str(sig(np.std(noise_floor[i][1]), sigfigs=sigfigs)))

                #Inputting data into the snr table
                snr_table_info[1].append((chr(65+i)))
                snr_table_info[2].append(str(sig(max_top[i][0], sigfigs=sigfigs)))
                snr_table_info[3].append(str(sig(max_top[i][1], sigfigs=sigfigs)))
                snr_table_info[4].append(str(sig(fft_snr[i], sigfigs=sigfigs)))

            #making and placing NF table
            nf_table = Table(nf_table_info, style=[('GRID', (0,1), (num_channels+1,6), 1, colors.black),
                                    ('BACKGROUND', (0,1), (num_channels+1,1), '#D5D6D5')])
            nf_table.wrapOn(pdf, nf_table_width, nf_table_height)
            nf_table.drawOn(pdf, nf_x, nf_y)

            #making and placing SNR table
            snr_table = Table(snr_table_info, style=[('GRID', (0,1), (num_channels+1,4), 1, colors.black),
                                    ('BACKGROUND', (0,1), (num_channels+1,1), '#D5D6D5')])
            snr_table.wrapOn(pdf, snr_width, snr_height)
            snr_table.drawOn(pdf, snr_x, snr_y)

            if (multi):
                nf_y -=230
                snr_y -=230
            else:
                break

    print("Data collection complete")

    #Pass/Fail final page
    pdf.showPage()
    page_count += 1

    #Only sections of the header, so coded seperately
    #Positional Values
    header_font_size = 10
    header_x, header_y = 633, 584
    logo_width, logo_height = 75, 25
    logo_x, logo_y = header_x - logo_width - 2, header_y - 17
    pg_x, pg_y = 650,10

    #Header Writing
    header = pdf.beginText()
    header.setTextOrigin(header_x, header_y)
    header.setFont(font, header_font_size*0.6)
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
    pdf.drawText(pg_num)


    #Positional values
    title_font_size = 26
    title_x, title_y = 2, 575
    summary_width, summary_height = 250, 150
    summary_x, summary_y = 10, title_y - summary_height - 30
    snr_x=  summary_x

    #Setting up title
    title = pdf.beginText()
    title.setTextOrigin(title_x, title_y)
    title.setFont(font, title_font_size)
    title.textLine(text=("Summary Page for: " + unit_name + " - " + formattedDate))
    pdf.drawText(title)

    summary_nump = np.asarray(summary_info)

    #Checking the snr
    snr_bools = list(map(checkSNR, summary_nump[:, 2]))

    #Checking the Freq
    freq_bools = list(map(checkFreq, summary_nump[:, 0]))

    # Checking if spurs are acceptable
    spur_check_thresholds = [spur_check_threshold] * len(peaks_list)
    spur_bools = list(map(checkSpur, peaks_list[:], spur_check_thresholds))

    # Checking if gains are close enough together
    gain_check_thresholds = [gain_check_threshold] * len(peaks_list)
    gain_bools = list(map(checkGainRelative, peaks_list[:], gain_check_thresholds))

    summary_table_info = [["Summary Table: "], ["Run", "SNR check", "Frequency check", "Spur check", "Gain variation check"]]

    for i, snr, freq, spur, gain in zip(range(counter), snr_bools, freq_bools, spur_bools, gain_bools):
        summary_table_info.append([str(i+1), isPass(snr), isPass(freq), isPass(spur), isPass(gain)])

    summary = Table(summary_table_info, style=[('GRID', (0,1), (4, counter+1), 1, colors.black),
                                ('BACKGROUND', (0,1), (2,1), '#D5D6D5')])

    summary.wrapOn(pdf, summary_width, summary_height)
    summary.drawOn(pdf, summary_x, summary_y)

    #What the fails are
    if False in snr_bools:
        snr_x += summary_width + 5
        fail_info = [["Fails in SNR: ", ("Not greater than " + str(snr_min_check) + "dBc")], ["Run", "SNR Value"]]

        for i, snr in zip(range(counter), summary_nump[:,2]):
            fail_info.append([str(i+1), str(snr)])

        fail_table = Table(fail_info, style=[('GRID', (0,1), (4, counter+1), 1, colors.black),
                                    ('BACKGROUND', (0,1), (4,1), '#D5D6D5')])
        fail_table.wrapOn(pdf, summary_width, summary_height)
        fail_table.drawOn(pdf, snr_x, summary_y)
            #What the fails are
    if False in freq_bools:
        freq_x = snr_x + summary_width - 2

        fail_info = [["Fails in Frequency: ", ("Not within " + str(freq_check_threshold) + "Hz of given")], ["Run"]]

        for i, freq in zip(range(counter), summary_nump[:,0]):
            fail_info.append([str(i+1), str(freq)])

        fail_table = Table(fail_info, style=[('GRID', (0,1), (4, counter+1), 1, colors.black),
                                    ('BACKGROUND', (0,1), (2,1), '#D5D6D5')])

        fail_table.wrapOn(pdf, summary_width, summary_height)
        fail_table.drawOn(pdf, freq_x, summary_y)

    os.chdir(output_dir) #Ensuring we are saving in the output directory
    pdf.save() #saving the pdf

main(generate)


