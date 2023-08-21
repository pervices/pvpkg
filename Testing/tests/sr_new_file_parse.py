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
import subprocess
import numpy as np
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
from reportlab.lib.utils import ImageReader
from scipy.signal import find_peaks

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
begin_cutoff_waves = 20 #how many waves to cut off before tracking data
num_output_waves = 2 #number of waves shown on the final plots (IQ)
sigfigs = 3
SNR_min_check = 40 #dB
freq_check_offset = 1 #Hz
serial_num = ""
num_channels = 3
channel_names = ["Channel A", "Channel B", "Channel C"]#TODO: SWAP THIS BASED ON UNIT USED

# #Getting num_output_waves
# while(true):
#     try:
#         num_output_waves = int(input("How many waves do you want shown on IQ graphs? "))
#         assert 1 <= num_output_waves <= 4
#         break
#     except AssertionError:
#         print("ERROR: Please input a value within 1 to 4. Try again: ")
#     except ValueError:
#         print("ERROR: Please only input integers. Try again: ")

#Getting number of sigfigss
# while(true):
#     try:
#         sigfigs = int(input("How many waves do you want shown on IQ graphs? "))
#         assert 1 <= sigfigs <= 5
#         break
#     except ValueError:
#         print("ERROR: Please only input integers. Try again: ")
#     except AssertionError:
#         print("ERROR: For formatting, please input a value within 1 to 5. Try again:")

# #SNR threshold
# while(true):
#     try:
#         snr_min_check = float(input("What is the minimum value SNR can be (in dBc)? "))
#         break
#     except ValueError:
#         print("ERROR: Please only input numbers. Try again: ")

# #Frequency offset threshold
# while(true):
#     try:
#         freq_check_offset = float(input("What is the offset for the freq threshold? (in Hz)"))
#         break
#     except ValueError:
#         print("ERROR: Please only input numbers. Try again: ")

#Unit Info
#Asking the user to type serial number into the terminal
# #Serial Number
# while(true):
#     try:
#         serial_num = input("What is the serial number of the unit? ")
#
#     except ValueError:
#         print("ERROR: Please only input integers. Try again: ")

# #Channel numbers
# while(true):
#     hold = ["Channel A", "Channel B", "Channel C", "Channel D", "Channel E", "Channel F", "Channel G", "Channel H"]
#     try:
#         num_channels = int(input("How many Channels are you testing? "))
#         assert 1 <= num_channels <= 8
#         break
#         channel_names = hold[0:num_channels]
#     except ValueError:
#         print("ERROR: Please only input integers. Try again: ")
#     except AssertionError:
#         print("ERROR: Please input a value within 1 to 8. Try again: ")

#Using the terminal to pull unit info
# os.system('rm ' + current_dir + '/shiptest_out.txt')
os.system('touch shiptest_out.txt')
os.system('uhd_usrp_info  -s > shiptest_out.txt')

#Using terminal grep to set unit data
server_ver = subprocess.getstatusoutput("cat shiptest_out.txt | grep 'Server Version' | cut --complement -d ':' -f1 ")[1]
fpga_ver = subprocess.getstatusoutput("cat shiptest_out.txt | grep 'FPGA' | cut --complement -d ':' -f1")[1]
UHD_ver = subprocess.getstatusoutput("cat shiptest_out.txt | grep 'UHD' | cut --complement -d 'g' -f2")[1]
unit_name = subprocess.getstatusoutput("cat shiptest_out.txt | grep 'Device Type' | cut --complement -d ':' -f1")[1]
unit_time = subprocess.getstatusoutput("cat shiptest_out.txt | grep 'Date' | cut --complement -d ':' -f1")[1]
unit_rtm = subprocess.getstatusoutput("cat shiptest_out.txt | grep 'RTM' | cut --complement -d ':' -f1")[1]

#organizing info in order of time, tx, and rx using gterminal grep
os.system('uhd_usrp_info --all > shiptest_out.txt')
os.system("touch hold.txt")

os.system("grep '0/time/fw_version' shiptest_out.txt -A 15 > hold.txt")

time = []
time.append(subprocess.getstatusoutput("cat hold.txt | grep 'Board Version' | cut --complement -d ':' -f1")[1])
time.append(subprocess.getstatusoutput("cat hold.txt | grep 'Branch' | cut --complement -d ':' -f1")[1])
time.append(subprocess.getstatusoutput("cat hold.txt | grep -m1 'Revision' | cut --complement -d 'g' -f1")[1])
time.append(subprocess.getstatusoutput("cat hold.txt | grep 'Date' | cut --complement -d ':' -f1")[1])
time.append(subprocess.getstatusoutput("cat hold.txt | grep 'MCU Serial' | cut --complement -d ':' -f1")[1])
time.append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse00' | cut --complement -d ':' -f1")[1])
time.append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse02' | cut --complement -d ':' -f1")[1])
time.append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse03' | cut --complement -d ':' -f1")[1])


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


os.system("rm hold.txt")
os.system("rm shiptest_out.txt")

#Globals that will be changed later in the code
center_freq = -1
wave_freq = -1
sample_rate = -1
sample_count = -1
tx_gain = -1
rx_gain = -1
period = -1 #how many samples per one period or one wave
being_cutoff = -1
summary_info = [] #[iteration][[freq][amplitude][snr]]
counter = 0 #Keeps track of run

#page stuff
page_count = 1
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
    list_y = title_y - 20
    logo_x, logo_y = 485, 450
    logo_width, logo_height = 200, 100
    #Setting up title on Title Page
    title = pdf.beginText()
    title.setTextOrigin(title_x, title_y)
    title.setFont(font, title_font_size)
    title.textLine(text=("Ship Test Report: " + unit_name + " - Serial Number: " + serial_num))

    pdf.drawText(title)

    #Printing out Important Details regarding the Machine
    #everything will be attached to unitList text object
    unitList = pdf.beginText(list_x, list_y)

    #Date and TIme Version
    unitList.setFont(bold_font, list_font_size)
    unitList.textOut("Computer Date: ")
    unitList.setFont(font, list_font_size)
    unitList.textLine(formattedDate)

    #UHD Version
    unitList.setFont(bold_font, list_font_size)
    unitList.textOut("UHD Version: ")
    unitList.setFont(font, list_font_size)
    unitList.textLine(UHD_ver)

    #rtm Version
    unitList.setFont(bold_font, list_font_size)
    unitList.textOut("RTM: ")
    unitList.setFont(font, list_font_size)
    unitList.textLine(unit_rtm)

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

    #Unit time
    unitList.setFont(bold_font, list_font_size)
    unitList.textOut("Unit Time: ")
    unitList.setFont(font, list_font_size)
    unitList.textLine(unit_time)
    pdf.drawText(unitList)

    #Adding Logo
    pdf.drawImage(header_img, logo_x, logo_y, logo_width, logo_height)

    #Adding the toime, tx, rx board infocd cddc
    board_width, board_height = 100, 100
    colWidth, rowHeight = (1.5*inch), (0.2*inch)
    board_x, board_y = 3, list_y - rowHeight*17

    board_styles = ([('GRID', (0,0), (num_channels+1, 8), 1, colors.black),
                    ('FONTSIZE', (1,4), (num_channels+1, 5),7.8),
                    ('BACKGROUND', (0, 0), (num_channels+1,0), '#D5D6D5'),
                    ('BACKGROUND', (0, 0), (0,8), '#D5D6D5')])

    #Time Board
    board_info = [["Time Board Information: "], ["Board"], ["Branch"], ["Revision"], ["Date"], ["MCU Serial"], ["Fuse 00"], ["Fuse 02"], ["Fuse 03"]]
    for z in range(len(time)):
        board_info[z+1].append((time[z]))

    board_table = Table(board_info, colWidths=colWidth, rowHeights=rowHeight, style=board_styles)
    board_table.wrapOn(pdf, board_width, board_height)
    board_table.drawOn(pdf, board_x, board_y)
    board_y -= rowHeight*10

    #Tx Board
    board_info = [["TX Board Information: "], ["Board"], ["Branch"], ["Revision"], ["Date"], ["MCU Serial"], ["Fuse 00"], ["Fuse 02"], ["Fuse 03"]]
    for i, name in zip(range(num_channels), channel_names):
        board_info[0].append(chr(65+i))
        for z in range(len(tx_info["TX: " + name])):
            board_info[z+1].append((tx_info["TX: " + name][z]))

    board_table = Table(board_info, rowHeights=rowHeight, style=board_styles)
    board_table.wrapOn(pdf, board_width, board_height)
    board_table.drawOn(pdf, board_x, board_y)
    board_y -= rowHeight*10

    #Rx Board
    board_info = [["RX Board Information: "], ["Board"], ["Branch"], ["Revision"], ["Date"], ["MCU Serial"], ["Fuse 00"], ["Fuse 02"], ["Fuse 03"]]
    for i, name in zip(range(num_channels), channel_names):
        board_info[0].append(chr(65+i))
        for z in range(len(rx_info["RX: " + name])):
            board_info[z+1].append((rx_info["RX: " + name][z]))

    board_table = Table(board_info, colWidths=colWidth, rowHeights=rowHeight, style=board_styles)
    board_table.wrapOn(pdf, board_width, board_height)
    board_table.drawOn(pdf, board_x, board_y)


'''Creates a title for each Run Page
PARAMS: pdf, it name
RETURNS: None
'''
def topOfPage(pdf, it):
    #Positionalgalues
    title_font_size = 26
    title_x, title_y = 80, 575

    #Setting up title on Title Page
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


    #Setting up 2D array holding input data
    data = [["Center Frequency (Hz)", "Wave Frequency (Hz)", "Sample Rate (SPS)", "Sample Count", "TX Gain (dB)", "RX Gain (dB)"],
            [center_freq, wave_freq, sample_rate, sample_count, tx_gain, rx_gain]]

    #Making and styling the table
    inputs = Table(data, style=[('GRID', (0,0), (6,1), 1, colors.black),
                                ('BACKGROUND', (0,0), (6,0), '#D5D6D5')])
    inputs.wrapOn(pdf, table_width, table_height)
    inputs.drawOn(pdf, table_x, table_y)

'''Plots the FFT subplots all in the same format
PARAMS: x, rea;, ax, imag, title
RETURNS: NONE'''
def subPlotFFTs(x, y, ax, title, max_four, nf): #TODO: Add points on top of peaks

    ax.set_title(title)
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Amplitude (dB)")
    fft, = ax.plot(x, y, "-.", color='crimson')
    ax.axhline(nf, markersize=0.5, alpha=0.3, label="Noise Floor")

    for i in range(len(max_four)):
        ax.plot(max_four[i][0], max_four[i][1], "x", label="Peak {}".format(i+1))

    return fft

'''Plots the IQ subplots all in the same format
PARAMS: x, real, ax, imag, best_fit_real, best_fit_imag, title
RETURNS: NONE'''
def subPlotIQs (x, real,imag, best_fit_real, best_fit_imag, offset_real, offset_imag, ax, title):
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

    # plt.show()
    return bf_r

'''
Represents the wave equation
PARAMS: time, ampl, freq, phase
RETUNRS: y'''
def waveEquation(params, time):
    ampl = params['ampl'].value
    freq = params['freq'].value
    phase = params['phase'].value
    dc_offset = params['dc_offset'].value

    model = ampl*np.cos(2*np.pi*freq*time + phase) + dc_offset #model for wave equation
# def waveEquation(time, ampl, freq, phase, dc_offset):
#
#     model = ampl*np.cos(2*np.pi*freq*time + phase) + dc_offset #model for wave equation

    return model

'''Creates the line of best fit for the given x and y
PARAMS: x,y
RETURNS: best_fit (y values of the line of best fit '''
def bestFit(x, y):

    params = create_params(ampl=max(y), freq=wave_freq, phase=0, dc_offset=0)
    result = minimize(waveEquation, params, args=(x,))
    model = y + result.residual

    return model, (result.params['dc_offset'], result.params['ampl'], result.params['freq'], result.params['phase'])

    # model = Model(waveEquation)
    # params = model.make_params(ampl=max(y), freq=wave_freq, phase=0, dc_offset=0)
    # result = model.fit(y, params, time=x, nan_policy='raise')
    #
    #
    # return result.best_fit, (result.params['dc_offset'], result.params['ampl'], result.params['freq'], result.params['phase'])


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

    # #Transform to dB
    # # bools_norms = list(map(isNotZero, norm_y))
    # # np.place(norm_y, bools_norms, 20*np.log10(norm_y)) #does not log values that are 0
    norm_y = 20*np.log10(abs(norm_y))

    #Setting up the X values
    freq = np.fft.fftshift(np.fft.fftfreq(len(x), d=(sample_rate))) #NOTEL makin thing is if this is okay

    return freq, norm_y

'''Turning the plot figure into a rasterized image and saving it to the directory
PARAMS: plot, title, counter, pdf
RETURNS: NONE'''
def plotToPdf(plt, title, counter):

    #Saving plot to proper directory and converting to png
    os.chdir(plots_dir) #ensuring in right directory
    plt.gcf().set_size_inches(8, 5)
    plt.savefig((title + "_" + str(counter)), format='png', dpi=300)

    #Opening file as io bits, then translating them to image reader
    img_data = open(plots_dir + "/" + title + "_" + str(counter), "rb")
    img = ImageReader(img_data)

    # pdf.drawImage(img, plot_img_pos_x, plot_img_pos_y, plot_img_width, plot_img_height)
    return(img)

'''Finding the top four peaks
PARAMS: y
RETURNS: max_four'''
def numPeaks(x, y, ampl, num):

    peaks, properties = find_peaks(y, height=ampl) #NOTE: What should I use as the height...
    x = np.asarray(x)
    y = np.asarray(y)

    maxs = []
    peaks_arrays = [x[peaks], y[peaks]]

    print(peaks_arrays)
    for i in range(num):
        print("Len of Peak Array 0:" + str(len(peaks_arrays[0])))
        print("Len of Peak Array 1:" + str(len(peaks_arrays[1])))
        maxs_indiv = np.argmax(peaks_arrays[1])
        print((peaks_arrays[0][maxs_indiv], peaks_arrays[1][maxs_indiv]))
        maxs.append((peaks_arrays[0][maxs_indiv], peaks_arrays[1][maxs_indiv]))
        peaks_arrays = np.delete(peaks_arrays, maxs_indiv, axis=1)

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
    print("Signal: " + str(signal))
    print("Noise: " + str(noise))
    print("SNR DIFF")
    print(signal - np.max(noise))
    return (signal - np.max(noise))

def partition(array, low, high, other_array):

    # choose the rightmost element as pivot
    pivot = array[high]
    print()
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

            print("Run: " + str(counter))
            print("Swapping " + str(i) + " with " + str(j))
            #NOTE: There is probably a better way to do this, but I am not sure how
            # Swapping element at i with element at j)
            #print("for loops")
            for ar in range(len(other_array)):
                hold = other_array[ar][i]
                other_array[ar][i] = other_array[ar][j]
                other_array[ar][j] = hold

    # Swap the pivot element with the greater element specified by i
    (array[i + 1], array[high]) = (array[high], array[i + 1])

    for ar in range(len(other_array)):
        hold = other_array[ar][i + 1]
        other_array[ar][i + 1] =  other_array[ar][high]
        other_array[ar][high] = hold

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
        print("In low High")
        print(counter)
        pi = partition(array, low, high, other_array)

        # Recursive call on the left of pivot
        quickSort(array, low, pi - 1, other_array)

        # Recursive call on the right of pivot
        quickSort(array, pi + 1, high, other_array)

'''Checks if the given is within the SNR bounds
PARAM: a
RETURN: Boolean'''
def checkSNR(a):
    return (a > SNR_min_check)

'''Checks if the freq is within desired location
PARAM: a
RETURN: Bool'''
def checkFreq(a):
    return (a > (wave_freq - freq_check_offset) and a < wave_freq + (freq_check_offset))

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

    ##MAKING PDF and Title page
    pdf = canvas.Canvas(file_title, pagesize=landscape(letter)) #Setting the page layout and file name
    pdf.setTitle(doc_title)

    #Title page
    titlePage(pdf)

    for it in iterations: #Will iterate per Run
        global counter
        counter += 1

        #Initilize Important Arrays
        reals = []
        imags = []
        x_time = []
        ampl_vec = np.zeros(shape=(4))

        #The reals
        best_fit_reals = []
        freq_reals = np.zeros(shape=(4))
        phase_reals = np.zeros(shape=(4))
        offset_reals = np.zeros(shape=(4))
        ampl_reals = np.zeros(shape=(4))

        best_fit_imags = []
        freq_imags = np.zeros(shape=(4))
        phase_imags = np.zeros(shape=(4))
        offset_imags = np.zeros(shape=(4))
        ampl_imags = np.zeros(shape=(4))

        gen.dump(it) #pulls info form generator

        ##SETING UP TESTS AND GETTING INPUTS
        vsnks = []
        global sample_rate
        sample_rate = int(it["sample_rate"])
        global sample_count
        sample_count = int(it["sample_count"])
        tx_stack = [(10.0 , sample_rate)] #Equivalent to 1 second
        rx_stack = [(10.25, sample_count)] #TODO: Maybe add the burst start times to table - or title page

        vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)

        global period
        period = int(round(1/(it["wave_freq"]/it["sample_rate"])))
        global begin_cutoff
        begin_cutoff = int(period*begin_cutoff_waves)


        #X values
        x = np.arange(begin_cutoff/sample_rate, (sample_count/sample_rate), 1/sample_rate) #0 to max time, taking the 1/sr step


        vsnks.append(vsnk) #This will loop us through the channels an appropriate amount of time
        for vsnk in vsnks:

            for ch, channel in enumerate(vsnk): #Goes through each channel to sve data

                real = [datum.real for datum in channel.data()]
                imag = [datum.imag for datum in channel.data()]

                reals.append(real[begin_cutoff:]) #Formats real data into a 2D array
                imags.append(imag[begin_cutoff:])

                best_fit, param = bestFit(x, real[begin_cutoff:])

                best_fit_reals.append((best_fit))
                offset_reals[ch] = param[0]
                ampl_reals[ch] = param[1]
                freq_reals[ch] = param[2]
                phase_reals[ch] = param[3]

                best_fit, param = bestFit(x, imag[begin_cutoff:])

                best_fit_imags.append((best_fit))
                offset_imags[ch] = param[0]
                ampl_imags[ch] = param[1]
                freq_imags[ch] = param[2]
                phase_imags[ch] = param[3]

                ampl_vec[ch] = np.sqrt(param[1]**2 + ampl_reals[len(ampl_reals)-1]**2)
                #Page One Set up

        #Making them all np.arrays
        #this for efficency, it is easier to initalize as non-numpy bc allows for flexibility in code
        reals = np.asarray(reals)
        imags = np.asarray(imags)

        #Other Variables
        global center_freq
        center_freq = int(it["center_freq"])
        global wave_freq
        wave_freq = int(it["wave_freq"])
        global tx_gain
        tx_gain = int(it["tx_gain"])
        global rx_gain
        rx_gain = int(it["rx_gain"])

        x_time = np.asarray(x*1000000000) # This is for the actual output of IQ plots
        plotted_samples = int(period*num_output_waves) #calculating plot_sample_ratio

        #Plotting IQ Data (not putting on page)
        IQ_plots = []
        #Plotting the imaginary and real values
        fig = plt.GridSpec(1, 56, wspace=0.3, hspace=0.3)

        plt.suptitle("Individual Channels' Amplitude versus Time for Run {}".format(counter))
        plt.xlabel("Time (gS)")
        plt.ylabel("Amplitude(kV)")

        axis = []

        #TODO: Turn this into a for loop
        axis.append(plt.subplot(fig[0:1, 0:10]))
        axis.append(plt.subplot(fig[0:1, 15:25]))
        axis.append(plt.subplot(fig[0:1, 30:40]))
        axis.append(plt.subplot(fig[0:1, 45:55]))
        for i, title, ax in zip(range(num_channels), channel_names, axis):
            IQ_plots.append(subPlotIQs(x_time[0:plotted_samples], reals[i][0:plotted_samples], imags[i][0:plotted_samples], best_fit_reals[i][0:plotted_samples], best_fit_imags[i][0:plotted_samples], offset_reals[i], offset_imags[i], ax, title))
        IQ_plots = np.asarray(IQ_plots)

        #Rasterizes the plot/figures and converts to png
        IQ_plt_img = plotToPdf(plt, ("IQPlots_" + formattedDate), counter)
        plt.clf()

        #Plotting FFT Data (not putting on page)
        #Calculating the x and y fft and finding the 5 maxs
        max_fours = []
        fft_x = []
        fft_y = []
        noise_floor = []
        std = []
        for i in range(num_channels):
            x, y = fftValues(x_time, reals[i], imags[i]) #NOTE: should I use best fit instead?
            fft_x.append((x))
            fft_y.append((y))

            max_fours.append(numPeaks(x, y, ampl_vec[i], 4)) #NOTE: WHY DOESNT THIS GIVE ME THE INFO DB
            #Noise Floor and std- in db
            noise_floor.append(noiseFloor(x, y, ampl_vec[i]))


        max_fours = np.asarray(max_fours)
        fft_x = np.asarray(fft_x)
        fft_y = np.asarray(fft_y)
        noise_floor = np.asarray(noise_floor)
        std = np.asarray(std)

        FFT_plots = []
        #Plotting the individual FFT Plots
        fig = plt.GridSpec(1, 44, wspace=10)
        plt.suptitle("Individual Channels' FFTs for Run {}".format(counter))

        axis = []
        axis.append(plt.subplot(fig[0:1, 0:10]))
        axis.append(plt.subplot(fig[0:1, 11:21]))
        axis.append(plt.subplot(fig[0:1, 22:32]))
        axis.append(plt.subplot(fig[0:1, 33:43]))

        for i, title, ax in zip(range(num_channels), channel_names, axis):
            FFT_plots.append((subPlotFFTs(fft_x[i], fft_y[i], ax, title, max_fours[i], np.mean(noise_floor[1]))))

        FFT_plots = np.asarray(FFT_plots)
        #Rasterizes the plot/figures and converts to png)
        FFT_plt_img = plotToPdf(plt, ("FFTPlots_" + formattedDate), counter)
        plt.clf()

        #MAKING THE ACTUAL PDF THINGS

        #SECTION ONE OF RUNS: Merged Plots
        pdf.showPage()
        global page_count
        page_count += 1
        topOfPage(pdf, str(counter))

        tgth_width, tgth_height = 700, 500
        tgth_x, tgth_y = 2, 3

        #Setting the plot
        fig = plt.GridSpec(17, 45, wspace=10)
        ax1 = plt.subplot(fig[0:17, 0:20])
        ax2 = plt.subplot(fig[0:17, 20:40])

        colours = ['royalblue', 'maroon', 'darkolivegreen', 'mediumvioletred']

        #plotting them all by pulling previous data
        for i, colour in zip(range(num_channels), colours):
            ax1.set_title("All Channels - Real Data")
            ax1.plot(IQ_plots[i].get_xdata(), IQ_plots[i].get_ydata(), '-', color=colour, markersize=0.2, label="Channel {}".format(i))
            ax2.set_title("All Channels - FFT Graphs")
            ax2.plot(FFT_plots[i].get_xdata(), FFT_plots[i].get_ydata(), '-', color=colour, markersize=0.2, label="Channel {}".format(i))

        ax2.legend(loc='upper left', bbox_to_anchor=(1,0.5))

        #Rasterizes the plot/figures and converts to png)
        tgth_plt_img = plotToPdf(plt, ("TogetherPlots_" + formattedDate), counter)
        pdf.drawImage(tgth_plt_img, tgth_x, tgth_y, tgth_width, tgth_height)


        #SECTION TWO OF RUN: Plotting the Amplitude vs Time
        pdf.showPage() #Page break on pdf
        page_count += 1
        topOfPage(pdf, str(counter))

        #TODO: MIGHT BE ABLE TO MAKE THESE MORE EFFICENT FOR FFT, IQ, AND COMBINED
        plot_img_width, plot_img_height = 700, 450
        plot_img_pos_x,  plot_img_pos_y = 2, 60
        IQ_width, IQ_height = 250, 105
        IQ_table_x, IQ_table_y = 5,4
        pdf.drawImage(IQ_plt_img, plot_img_pos_x, plot_img_pos_y, plot_img_width, plot_img_height)

        #Table of IQ info
        IQ_table_info = [["IQ Data: "],["Channel"], ["Mag Freq (Hz)"], ["Mag Ampl (Hz)"]]
        for i in range(num_channels):
            IQ_table_info[1].append((chr(65+i)))
            IQ_table_info[2].append(sig(magnitude(freq_reals[i], freq_imags[i]), sigfigs=sigfigs))
            IQ_table_info[3].append(sig(magnitude(ampl_reals[i], ampl_imags[i]), sigfigs=sigfigs))
        IQ_table = Table(IQ_table_info, style=[('GRID', (0,1), (num_channels+1,3), 1, colors.black),
                                                ('BACKGROUND', (0, 1), (num_channels+1,1), '#D5D6D5')])
        IQ_table.wrapOn(pdf, IQ_width, IQ_height)
        IQ_table.drawOn(pdf, IQ_table_x, IQ_table_y)

        #SECTION THREE OF RUN: Plotting Amplitude vs Frequency
        pdf.showPage()
        page_count += 1
        topOfPage(pdf, str(counter))

        #Positional
        fft_pos_x, fft_pos_y = 2, 100
        fft_width, fft_height = 600, 400
        max_peak_width, max_peak_height = 80, 50
        max_peak_x, max_peak_y = 2, 5
        pdf.drawImage(FFT_plt_img, fft_pos_x, fft_pos_y, fft_width, fft_height)

        #Tables stuff
        max_peak_table_info = [["Top Peaks (Frequencty, Amplitude):"], ["Channel"], ["Highest Peak"], ["Second Highest"], ["Third Highest"], ["Fourth Heighest"]]
        for i in range(num_channels):
            max_peak_table_info[1].append((chr(65+i)))
            print(max_fours[i])
            max_peak_table_info[2].append(str((sig(max_fours[i][0][0], sigfigs=sigfigs), sig(max_fours[i][0][1], sigfigs=sigfigs))))
            max_peak_table_info[3].append(str((sig(max_fours[i][1][0], sigfigs=sigfigs), sig(max_fours[i][1][1], sigfigs=sigfigs))))
            max_peak_table_info[4].append(str((sig(max_fours[i][2][0], sigfigs=sigfigs), sig(max_fours[i][2][1], sigfigs=sigfigs))))
            max_peak_table_info[5].append(str((sig(max_fours[i][3][0], sigfigs=sigfigs), sig(max_fours[i][3][1], sigfigs=sigfigs))))

        peak_table = Table(max_peak_table_info, style=[('GRID', (0,1), (num_channels+1,5), 1, colors.black),
                                ('BACKGROUND', (0,1), (num_channels+1,1), '#D5D6D5')])
        peak_table.wrapOn(pdf, max_peak_width, max_peak_height)
        peak_table.drawOn(pdf, max_peak_x, max_peak_y)

        ##SECTION FOUR OF RUNS: SUMMARY PAGE
        pdf.showPage()
        page_count += 1
        topOfPage(pdf, str(counter))
        stats_summary_x, stats_summary_y = 15, 400
        nf_table_width, nf_table_height = 80, 20
        nf_x, nf_y = stats_summary_x, stats_summary_y - nf_table_height

        #Tables stuff
        nf_table_info = [["All Noise Floor Data :"], ["Channel"],["Maximum"], ["Minimum"], ["Mean"], ["Mean Difference to A"], ["STD"]]
        mean_a = np.mean(noise_floor[0][1])
        for i in range(num_channels):
            max_loc = np.argmax(noise_floor[i][1])
            min_loc = np.argmin(noise_floor[i][1])
            mean = np.mean(noise_floor[i][1])

            nf_table_info[1].append((chr(65+i)))
            nf_table_info[2].append(str((sig(noise_floor[i][0][max_loc], sigfigs=sigfigs), sig(noise_floor[i][1][max_loc], sigfigs=sigfigs))))
            nf_table_info[3].append(str((sig(noise_floor[i][0][min_loc], sigfigs=sigfigs), sig(noise_floor[i][1][min_loc], sigfigs=sigfigs))))
            nf_table_info[4].append(str(mean))
            nf_table_info[5].append(str(mean - mean_a))
            nf_table_info[6].append(str(np.std(noise_floor[i][1])))

        nf_table = Table(nf_table_info, style=[('GRID', (0,1), (num_channels+1,6), 1, colors.black),
                                ('BACKGROUND', (0,1), (num_channels+1,1), '#D5D6D5')])
        nf_table.wrapOn(pdf, nf_table_width, nf_table_height)
        nf_table.drawOn(pdf, nf_x, nf_y)

        #Top 5 Peaks info
        #SNR DATA
        snr_width, snr_height = 100, 50
        snr_x, snr_y = nf_x, nf_y - snr_height
        fft_snr = []
        for i in range(num_channels):
            fft_snr.append(toSNR(noise_floor[i][1], max_fours[i][0][1]))

        fft_snr = np.asarray(fft_snr)

        #At this point, the snr shoud be in order of max peak
        summary_info.append((max_fours[0][0][0], max_fours[0][0][1], fft_snr[0]))

        #Sorting according to SNR
        quickSort(fft_snr, 0, len(fft_snr)-1, max_fours) #X also gets sorted, so that the p/f is easier to check

        #Tables stuff
        snr_table_info = [["Top Peak Information (Based on Highest SNR):"], ["Channel"], ["Location (Hz)"], ["Amplitude (dB)"], ["SNR (dBc)"]]
        snr_style = []

        for i in range(num_channels):
            snr_table_info[1].append((chr(65+i)))
            snr_table_info[2].append(str(sig(max_fours[i][0][0], sigfigs=sigfigs)))
            snr_table_info[3].append(str(sig(max_fours[i][0][1], sigfigs=sigfigs)))
            snr_table_info[4].append(str(sig(fft_snr[i], sigifigs=sigfigs)))

        snr_table = Table(snr_table_info, style=[('GRID', (0,1), (num_channels+1,4), 1, colors.black),
                                ('BACKGROUND', (0,1), (num_channels+1,1), '#D5D6D5')])
        snr_table.wrapOn(pdf, snr_width, snr_height)
        snr_table.drawOn(pdf, snr_x, snr_y)


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


    #Positional values
    title_font_size = 26
    title_x, title_y = 2, 500
    summary_width, summary_height = 250, 100
    summary_x, summary_y = 10, title_y - summary_height
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

    summary_table_info = [["Summary Table: "], ["Run", "SNR Check", "Frequency Check"]]

    for i, snr, freq in zip(range(counter), snr_bools, freq_bools):
        summary_table_info.append([str(i), isPass(snr), isPass(freq)])

    summary = Table(summary_table_info, style=[('GRID', (0,1), (4, counter+1), 1, colors.black),
                                ('BACKGROUND', (0,1), (2,1), '#D5D6D5')])

    summary.wrapOn(pdf, summary_width, summary_height)
    summary.drawOn(pdf, summary_x, summary_y)

    #What the fails are
    if False in snr_bools:
        snr_x += summary_width + 5
        fail_info = [["Fails in SNR: ", ("Must be greater than " + str(SNR_min_check) + "dBc")], ["Run", "SNR Value"]]

        for i, snr in zip(range(counter), summary_nump[:,2]):
            fail_info.append([str(i), str(snr)])

        fail_table = Table(fail_info, style=[('GRID', (0,1), (4, counter+1), 1, colors.black),
                                    ('BACKGROUND', (0,1), (4,1), '#D5D6D5')])
        fail_table.wrapOn(pdf, summary_width, summary_height)
        fail_table.drawOn(pdf, snr_x, summary_y)
            #What the fails are
    if False in freq_bools:
        freq_x = snr_x + summary_width - 2

        fail_info = [["Fails in Frequency: ", ("Must be within " + str(freq_check_offset) + "Hz of " + str(wave_freq) +"Hz")], ["Run", "Frequency"]]

        for i, freq in zip(range(counter), summary_nump[:,0]):
            fail_info.append([str(i), str(freq)])

        fail_table = Table(fail_info, style=[('GRID', (0,1), (4, counter+1), 1, colors.black),
                                    ('BACKGROUND', (0,1), (2,1), '#D5D6D5')])

        fail_table.wrapOn(pdf, summary_width, summary_height)
        fail_table.drawOn(pdf, freq_x, summary_y)

    os.chdir(output_dir) #Ensuring we are saving in the output directory
    pdf.save() #saving the pdf

main(gen.ship_test_tx(4))









