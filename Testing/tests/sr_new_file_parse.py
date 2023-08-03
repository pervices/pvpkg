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
from lmfit import Model, minimize, Parameters #apparently better for discrete things
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
decimal_round = 7
SNR_min_check = 40 #dB
#SNR_max_check = 50 #dB
freq_check_offset = 1 #Hz


#Unit Info
#Asking the user to type serial number into the terminal
serial_num = "" #NOTE: Doug will add to script later
num_channels = 3
channel_names = ["Channel A", "Channel B", "Channel C"] #TODO: SWAP THIS BASED ON UNIT USED

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
print("ser ver: " + server_ver)

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
    print(rx_info["RX: " + name])



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
    logo_x, logo_y = 450, 450
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
    board_info = [["TX Board Information: "], ["Board"], ["Branch"], ["Revision"], ["Date"], ["MCU Serial"], ["Fuse 00"], ["Fuse 02"], ["Fuse 03"]]
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
    table_height = 75
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
def subPlotFFTs(x, y, ax, title, max_five, nf): #TODO: Add points on top of peaks

    ax.set_title(title)
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Amplitude (dB)")
    fft, = ax.plot(x, y, color='crimson')
    ax.plot(x, nf, markersize=0.5, alpha=0.3, label="Noise Floor")

    for i in range(len(max_five)):
        ax.plot(max_five[i][0], max_five[i][1], "x")

    return fft

'''Plots the IQ subplots all in the same format
PARAMS: x, real, ax, imag, best_fit_real, best_fit_imag, title
RETURNS: NONE'''
def subPlotIQs (x, real,imag, best_fit_real, best_fit_imag, offset_real, offset_imag, ax, title):
    ax.set_title(title)
    ax.set_xlabel("Time")
    ax.set_ylabel("Amplitude (kV)") #NOTE: I HOPE THIS IS RIGHT
    bf_r, = ax.plot(x, best_fit_real, '-', markersize=0.1, color='indianred', label="Real Best Fit")
    ax.plot(x, real, '.', markersize=3, color='crimson', label="Real")
    ax.axhline(y = offset_real, markersize=0.025, color='red', alpha=0.4, label='Real Offset')
    ax.plot(x, best_fit_imag, '-', markersize=0.1, color='darkmagenta', label="Imaginary Best Fit")
    ax.plot(x, imag, '.', markersize=3, color='purple', label="Imaginary")
    ax.axhline(y = offset_imag, markersize=0.025, color='indigo', alpha=0.4, label='Imaginary Offset')

    real_peaks = find_peaks(real, distance=period)
    imag_peaks = find_peaks(imag, distance=period)

    for r, i in zip(real_peaks[0], imag_peaks[0]):
        ax.axvline(x = x[r], linestyle='--', alpha=0.5, color='rosybrown', markersize=0.05)
        ax.text(x[r], max(best_fit_real) + (0.05*max(best_fit_real)), "\u2190" + str(round(x[r], 3)), fontsize=7, verticalalignment='top', )
        ax.axvline(x = x[i],  linestyle='--', alpha=0.5, color='darkslateblue',markersize=0.05)
        ax.text(x[i], min(best_fit_imag) - (min(best_fit_imag)*0.05), "\u2190" + str(round(x[i], 3)), fontsize=7, verticalalignment='top')

    plt.show()
    return bf_r

'''
Represents the wave equation
PARAMS: time, ampl, freq, phase
RETUNRS: y'''
def waveEquation(time, ampl, freq, phase, dc_offset):
    # ampl = guess['ampl'].value
    # freq = guess['freq'].value
    # phase = guess['phase'].value
    # dc_offset = guess['dc_offset'].value
    model = ampl*np.cos(2*np.pi*freq*time + phase) + dc_offset #model for wave equation

    return model

'''Creates the line of best fit for the given x and y
PARAMS: x,y
RETURNS: best_fit (y values of the line of best fit '''
def bestFit(x, y):

    model = Model(waveEquation)
    params = model.make_params(ampl=max(y), freq=wave_freq, phase=0, dc_offset=0)
    result = model.fit(y, params, time=x)

    return result.best_fit, (result.params['dc_offset'], result.params['ampl'], result.params['freq'], result.params['phase'])



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
    # bools_norms = list(map(isNotZero, norm_y))
    # np.place(norm_y, bools_norms, 20*np.log10(norm_y)) #does not log values that are 0
    norm_y = 20*np.log10(abs(norm_y))

    #Setting up the X values
    freq = np.fft.fftshift(np.fft.fftfreq(len(x), d=(sample_rate))) #NOTEL makin thing is if this is okay

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

    return max_five

'''Intakes data to find the noise floor
PARAM: Data
RETURNS: noise_floor_y'''
def noiseFloor(data_given):
    return (((data_given - np.mean(data_given))/sample_count))

'''Squares the given values
PARMS: V
RETURNS: v**2'''
def square(v):
    return v**2

'''Turning the amplitudes of noise and signal and making the snr
PARAMS:y_vals
RETURNS: SNR in dB'''
def toSNR(noise, signal):
    noise_std  = np.std(noise)
    return 20*np.log10(signal/noise_std) #Signal is not in decibls, but noise is. This is from wikipedia

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


            # Swapping element at i with element at git ])
            for ar in range(len(other_arrays)):
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

        #Page One Set up
        pdf.showPage() #Page break on pdf
        global page_count
        page_count += 1
        topOfPage(pdf, str(counter))


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
        tx_stack = [ (10.0 , sample_rate)] #Equivalent to 1 second
        rx_stack = [ (10.25, sample_count)] #TODO: Maybe add the burst start times to table - or title page

        vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)

        #Other Variablesc
        global center_freq
        center_freq = int(it["center_freq"])
        global wave_freq
        wave_freq = int(it["wave_freq"])
        global tx_gain
        tx_gain = int(it["tx_gain"])
        global rx_gain
        rx_gain = int(it["rx_gain"])
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


        #Making them all np.arrays
        #this for efficency, it is easier to initalize as non-numpy bc allows for flexibility in code
        reals = np.asarray(reals)
        imags = np.asarray(imags)

        #VISUALS on PDF
        #IMAG AND REAL
        '''Following the steps of: Setting up variables, making the individiual plots on the figure,
        rasterizing onto the PDF, adding note to ensure readers know there are less than tested samples visible'''
        #variables for placement of plot
        plot_img_width, plot_img_height = 700, 450
        plot_img_pos_x,  plot_img_pos_y = 2, 20
        IQ_width, IQ_height = 250, 105
        IQ_table_x, IQ_table_y = 565,200

        #calculating plot_sample_ratio
        plotted_samples = int(period*num_output_waves)

        IQ_plots = []
        #Plotting the imaginary and real values
        fig = plt.GridSpec(1, 28, wspace=6, hspace=0.3)

        plt.suptitle("Individual Channels' Amplitude versus Time for Run {}".format(counter))
        axis = []
        axis.append(plt.subplot(fig[0:1, 0:5]))
        axis.append(plt.subplot(fig[0:1, 6:11]))
        axis.append(plt.subplot(fig[0:1, 12:17]))
        #axis.append(plt.subplot(fig[0:1, 18:23]))

        for i, title, ax in zip(range(num_channels), channel_names, axis):
            IQ_plots.append(subPlotIQs(x_time[0:plotted_samples], reals[i][0:plotted_samples], imags[i][0:plotted_samples], best_fit_reals[i][0:plotted_samples], best_fit_imags[i][0:plotted_samples], offset_reals[i], offset_imags[i], ax, title))

        IQ_plots = np.asarray(IQ_plots)
        # plt.show()
        #Rasterizes the plot/figures and converts to png)
        plotToPdf(plt, ("IQPlots_" + formattedDate), counter, pdf, plot_img_width, plot_img_height, plot_img_pos_x, plot_img_pos_y)
        plt.clf()

        #Table of IQ info
        IQ_table_info = [["IQ Data: "],["Channel"], ["Mag Freq (Hz)"], ["Mag Ampl (Hz)"]]
        for i in range(num_channels):
            IQ_table_info[1].append((chr(65+i)))
            IQ_table_info[2].append(magnitude(freq_reals[i], freq_imags[i]))
            IQ_table_info[3].append(magnitude(ampl_reals[i], ampl_imags[i]))

        IQ_table = Table(IQ_table_info, style=[('GRID', (0,1), (2,5), 1, colors.black),
                                                ('BACKGROUND', (0, 1), (2,1), '#D5D6D5')])


        IQ_table.wrapOn(pdf, IQ_width, IQ_height)
        IQ_table.drawOn(pdf, IQ_table_x, IQ_table_y)


        ##FFT PLOT AND TABLE
        pdf.showPage()
        page_count += 1
        topOfPage(pdf, str(counter))
        #Positional
        fft_pos_x, fft_pos_y = 10, 125
        fft_width, fft_height = 650, 450
        max_peak_width, max_peak_height = 80, 100
        max_peak_x, max_peak_y = fft_pos_x, fft_pos_y - max_peak_height

        #Calculating the x and y fft and finding the 5 maxs
        max_fives = []
        max_fives = []
        fft_x = []
        fft_y = []
        noise_floor = []
        for i in range(num_channels):
            x, y = fftValues(x_time, reals[i], imags[i]) #NOTE: should I use best fit instead?
            fft_x.append(x)
            fft_y.append(y)
            normal = fivePeaks(fft_x[i], fft_y[i], ampl_vec[i])
            max_fives.append(normal) #NOTE: WHY DOESNT THIS GIVE ME THE INFO DB
                    #Noise Floor - in db
            noise_floor.append(noiseFloor(y))

        max_fives = np.asarray(max_fives)
        fft_x = np.asarray(fft_x)
        fft_y = np.asarray(fft_y)
        noise_floor = np.asarray(noise_floor)

        FFT_plots = []
        #Plotting the individual FFT Plots
        fig = plt.GridSpec(1, 44, wspace=10)
        plt.suptitle("Individual Channels' FFTs for Run {}".format(counter))


        axis = []
        axis.append(plt.subplot(fig[0:1, 0:10]))
        axis.append(plt.subplot(fig[0:1, 11:21]))
        axis.append(plt.subplot(fig[0:1, 22:32]))
        axis.append(plt.subplot(fig[0:1, 33:43]))

        fft_x = np.asarray(fft_x)
        fft_y = np.asarray(fft_y)

        for i, title, ax in zip(range(num_channels), channel_names, axis):
            FFT_plots.append((subPlotFFTs(fft_x[i], fft_y[i], ax, title, max_fives[0], noise_floor[0])))

        FFT_plots = np.asarray(FFT_plots)
        #Rasterizes the plot/figures and converts to png)
        plotToPdf(plt, ("FFTPlots_" + formattedDate), counter, pdf, fft_width, fft_height, fft_pos_x, fft_pos_y)
        plt.clf()

        #Tables stuff
        max_peak_table_info = [["Top Five Peaks:"],
                                ["Channel A", "Channel B", "Channel C", "Channel D"]]
        for i in range(num_channels):
            max_peak_table_info.append((str(np.round(max_fives[i][0], decimal_round)), str(np.round(max_fives[i][1], decimal_round)), str(np.round(max_fives[i][2], decimal_round)), str(np.round(max_fives[i][3], decimal_round))))

        peak_table = Table(max_peak_table_info, style=[('GRID', (0,1), (4,8), 1, colors.black),
                                ('BACKGROUND', (0,1), (6,1), '#D5D6D5')])
        peak_table.wrapOn(pdf, max_peak_width, max_peak_height)
        peak_table.drawOn(pdf, max_peak_x  + 40, max_peak_y)

        header(pdf) #Putting here so on top of the image


        ##All merged plots
        pdf.showPage()
        page_count += 1
        topOfPage(pdf, str(counter))

        tgth_width, tgth_height = 800, 600
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

        # plt.show()
        #Rasterizes the plot/figures and converts to png)
        plotToPdf(plt, ("TogetherPlots_" + formattedDate), counter, pdf, tgth_width, tgth_height, tgth_x, tgth_y)
        plt.clf()

        ##SUMMARY PAGE
        pdf.showPage()
        page_count += 1
        topOfPage(pdf, str(counter))
        stats_summary_x, stats_summary_y = 15, 565
        nf_table_width, nf_table_height = 80, 20
        nf_x, nf_y = stats_summary_x, stats_summary_y - 175

        #Tables stuff
        nf_table_info = [["All Noise Floor Data :"], ["Maximum", "Minimum", "Mean", "Mean Difference to A"]]

        for i in range(num_channels):
            nf_table_info.append((str(np.max(noise_floor[i])), str(np.min(noise_floor[i])), str(np.mean(noise_floor[i])), str(np.mean(noise_floor[i]) - np.mean(noise_floor[0]))))

        nf_table = Table(nf_table_info, style=[('GRID', (0,1), (4,8), 1, colors.black),
                                ('BACKGROUND', (0,1), (6,1), '#D5D6D5')])

        nf_table.wrapOn(pdf, nf_table_width, nf_table_height)
        nf_table.drawOn(pdf, nf_x, nf_y)

        #Top 5 Peaks info
        #SNR DATA
        snr_width, snr_height = 100, 250
        snr_x, snr_y = nf_x, nf_y - snr_height
        fft_snr = []
        for i in range(num_channels):
            fft_snr.append(toSNR(noise_floor[i], ampl_vec[i]))

        fft_snr = np.asarray(fft_snr)

        #At this point, the snr shoud be in order of max peak
        summary_info.append((max_fives[0][0][0], max_fives[0][0][1], fft_snr[0]))

        #Sorting according to SNR
        quickSort(fft_snr, 0, len(fft_snr)-1, max_fives) #X also gets sorted, so that the p/f is easier to check


        #Tables stuff
        snr_table_info = [["More Top Peak Information:"]]
        snr_style = []

        for i, name in zip(range(num_channels), channel_names):
            snr_table_info.append((str(name), "", ""))
            snr_table_info.append(("Location (Hz)", str(max_fives[i][0][0]), str(max_fives[i][1][0]), str(max_fives[i][2][0]), str(max_fives[i][3][0])))
            snr_table_info.append(("Amplitude (dB)", str(max_fives[i][0][1]), str(max_fives[i][1][1]), str(max_fives[i][2][1]), str(max_fives[i][3][1])))
            snr_table_info.append(("SNR (dBc)", str(fft_snr[i])))
            snr_style.append(['GRID', (0, (2 + (4*i))), (5, (4 + (4*i))), 1, colors.black])
            snr_style.append(['BACKGROUND', (0, (1 + (4*i))), (6, (1 + (4*i))), '#D5D6D5'])




        snr_table = Table(snr_table_info, style=snr_style)
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
    title_x, title_y = 10, 600
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

        fail_info = [["Fails in Frequency: ", ("Must be within " + str(freq_check_offset) + "Hz of " + str(wave_freq))], ["Run", "Frequency"]]

        for i, freq in zip(range(counter), summary_nump[:,0]):
            fail_info.append([str(i), str(freq)])

        fail_table = Table(fail_info, style=[('GRID', (0,1), (4, counter+1), 1, colors.black),
                                    ('BACKGROUND', (0,1), (2,1), '#D5D6D5')])

        fail_table.wrapOn(pdf, summary_width, summary_height)
        fail_table.drawOn(pdf, freq_x, summary_y)

    os.chdir(output_dir) #Ensuring we are saving in the output directory
    pdf.save() #saving the pdf

main(gen.ship_test_tx(4))









