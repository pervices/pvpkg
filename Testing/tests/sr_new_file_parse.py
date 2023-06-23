#IMPORTING LIBRARIES AND MODULES
#TODO: go through these imports and libraries to see if we really need EVERY one -- add them in order of use
#Per Vices Imports
from common import sigproc
from common import engine
from common import generator as gen

#Basic imports
import time, datetime
import os
import numpy as np

#PDF IMPORTS
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import Image, Paragraph, Table, Frame

#Plot imports
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO


from reportlab.lib.utils import ImageReader
import glob
#import test_ship_collection as tsc
import re
from scipy.signal import find_peaks
import scipy.fftpack
from matplotlib import rcParams
import math
from scipy.fft import fft, fftfreq, fftshift
from scipy.signal import blackman

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
begin_cutoff_waves = 1 #how many waves to cut off before tracking data
num_output_waves = 4 #number of waves shown on the final plots (IQ)

#Globals that will be changed later
center_freq = -1

#Other Variables
unit_name = "Crimson"
python_to_inch = 72
num_channels = 4
font = "Times-Roman"
bold_font = "Times-Bold"
unit_max_rate = "325 MSPS" #Pulled from website
#TODO: WAIT FOR DOUG TO SET UP API CODE TO PULL OTHER REVISION NUMBERS EASILY FROM TERMINAL


''' DEBUGGER: Prints out the x and y placements of the pixels, to allow for nice layout
PARAMS: c (name of pdf)
RETURNS: none'''
def drawMyRuler(c):
    c.drawString(100,10, 'x100')
    c.drawString(200,10, 'x200')
    c.drawString(300,10, 'x300')
    c.drawString(400,10, 'x400')
    c.drawString(500,10, 'x500')

    c.drawString(10,100, 'y100')
    c.drawString(10,200, 'y200')
    c.drawString(10,300, 'y300')
    c.drawString(10,400, 'y400')
    c.drawString(10,500, 'y500')
    c.drawString(10,600, 'y600')
    c.drawString(10,700, 'y700')
    c.drawString(10,800, 'y800')

'''Creates Title Page
PARAMS: pdf
RETURNS: NONE'''
def titlePage(pdf):
    #Positional Values
    title_font_size = 26
    title_x = 125
    title_y = 755
    list_font_size = 14
    list_x = title_x - 50
    list_y = title_y - 75

    #Setting up title on Title Page
    title = pdf.beginText()
    title.setTextOrigin(title_x, title_y)
    title.setFont(font, title_font_size)
    title.textLine(text=(unit_name + " Unit Report using Ship Test"))
    title.setFont(font, title_font_size/2)
    title.textLine("Date and Time: " + formattedDate)
    pdf.drawText(title)

    #Printing out Important Details regarding the Machine
    #everything will be attached to unitList text object
    unitList = pdf.beginText(list_x, list_y)

    #Max Rate
    unitList.setFont(bold_font, list_font_size)
    unitList.textOut("Max Rate: ")
    unitList.setFont(font, list_font_size)
    unitList.textLine(unit_max_rate)

    #TEST: position holder for future version values.
    unitList.setFont(bold_font, list_font_size)
    unitList.textOut("Max Rate: ")
    unitList.setFont(font, list_font_size)
    unitList.textLine(unit_max_rate)

    #TODO: SET UP THE REST OF THE VERSION VALUES ONCE THEY ARE PROPERLY DECLARED AT THE BEGINNING OF THE CODE

    pdf.drawText(unitList)

'''Creates a title for each Run Page
PARAMS: pdf, it name
RETURNS: None
'''
def runTitle(pdf, it, name):
    #Positional Values
    title_font_size = 26
    title_x = 100
    title_y = 755

    #Setting up title on Title Page
    title = pdf.beginText()
    title.setTextOrigin(title_x, title_y)
    title.setFont(font, title_font_size)
    title.textLine(text=("Run Number " + it + " - " + name + " On " + unit_name))
    pdf.drawText(title)

'''Creates a table that shows the input values of each Run
PARAMS: pdf, center_freq, wave_freq, sample_rate, sample_count, tx_gain, rx_gain
RETURNS: None'''
def inputTable(pdf, center_freq, wave_freq, sample_rate, sample_count, tx_gain, rx_gain):
    #positional values
    label_x = 45
    label_y = 725
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
    data = [["Center Frequency (Hz)", "Wave Frequency (Hz)", "Sample Rate (SPS)", "Sample Count", "TX Gain (dB)", "RX Gain (dB)"], #TODO: ENSURE CORRECT UNITS
            [center_freq, wave_freq, sample_rate, sample_count, tx_gain, rx_gain]]
    #Making and styling the table
    inputs = Table(data, style=[('GRID', (0,0), (6,1), 1, colors.black),
                                ('BACKGROUND', (0,0), (6,0), '#D5D6D5')])

    inputs.wrapOn(pdf, table_width, table_height)
    inputs.drawOn(pdf, table_x, table_y)


'''Plots the subplots all in the same format
PARAMS: x, rea;, ax, imag, title
RETURNS: NONE'''
def subPlot(x, y, ax, title, y_name, x_name, y2=(-1,-1), labels=("","")):

    ax.set_title(title)
    ax.set_xlabel(x_name)
    ax.set_ylabel(y_name) #NOTE: I HOPE THIS IS RIGHT
    ax.plot(x, y, '-', color='crimson', label=labels[0])
    if (y2[0] != -1): #if it has two variables, it will plot the second
        ax.plot(x, y2, '-', color='darkviolet', label=labels[1])
        ax.legend()

'''Gets the magnitude of a 2D vector
PARAMS: a,b
RETURNS: ans'''
def magnitude(a, b):
    ans = np.sqrt( a**2 + b**2)
    return ans

def normalize(vector):
    peak = max(vector)
    return(vector/peak)

'''Turns the values recieved into values for the FFT plots
PARAMS: sample_count, reals, imags
RETURNS: freq, normalized_ys'''
def fftValues(x, reals, imags): #TODO: Not sure if it's more efficent to pass in sample count, make a sample count, or just use len'

    comp = np.vectorize(magnitude)
    mag_y = comp(reals, imags)#Make complex
    temp = []

    #normalizing
    for i in range(num_channels-1):
        temp.append(normalize(mag_y))

    fft_y = abs(np.fft.fftshift(np.fft.fft(temp)*np.blackman(len(x))))

    #Setting up the X values
    freq = np.fft.fftshift(x/center_freq)*10000000 #ensures plot window is looking @ right area (also in MHz)

    return freq, fft_y

'''Turning the plot figure into a rasterized image, saving it to the directory, and putting the plot onto the pdf
PARAMS: plot, title, counter, pdf
RETURNS: NONE'''
def plotToPdf(plt, title, counter, pdf, plot_img_width, plot_img_height, plot_img_pos_x, plot_img_pos_y):

    #Saving plot to proper directory and converting to png
    os.chdir(plots_dir) #ensuring in right directory
    plt.savefig((title + "_" + str(counter)), format='png', dpi=300)

    #Opening file as io bits, then translating them to image reader
    img_data = open(plots_dir + "/" + title + "_" + str(counter), "rb")
    img = ImageReader(img_data)

    pdf.drawImage(img, plot_img_pos_x, plot_img_pos_y, plot_img_width, plot_img_height)



'''Runs the tests and data collection, then calls other functions to tests and format the code outputs
PARAMS: iterations
RETURNS: NONE, it is the main function'''
def main(iterations):

    ##MAKING PDF and Title page
    pdf = canvas.Canvas(file_title, pagesize=letter) #Setting the page layout and file name
    pdf.setTitle(doc_title)

    drawMyRuler(pdf) #Allows for design to be easier
    titlePage(pdf)

    counter = 0 #Keeps track of run
    for it in iterations: #Will iterate per Run
        counter += 1

        #Important Arrays
        reals = []
        imags = []
        x_time = []

        #DEALING WITH PDF SET UP - INPUTS AND TITLE
        pdf.showPage() #Page break on pdf
        drawMyRuler(pdf)

        gen.dump(it) #pulls info form generator

        #Adds title to pdf, dependent on run
        runTitle(pdf, str(counter), it["name"])

        #Prints table showing inputs used on unit
        inputTable(pdf, it["center_freq"], it["wave_freq"], it["sample_rate"], it["sample_count"], it["tx_gain"], it["rx_gain"])

        ##SETING UP TESTS AND GETTING INPUTS
        vsnks = []
        sample_rate = int(it["sample_rate"])
        tx_stack = [ (10.0 , sample_rate)] #Equivalent to 1 second
        rx_stack = [ (10.0, int(it["sample_count"]))] #TODO: Maybe add the burst start times to table

        #Other Variables
        global center_freq
        center_freq = int(it["center_freq"])
        begin_cutoff = plotted_samples = int(round(1/(int(wave_freq)/sample_rate))*begin_cutoff_waves)

        #X values, for when plotting is required
        x = np.arange(begin_cutoff/it["sample_rate"],it["sample_count"]/it["sample_rate"], 1/it["sample_rate"]) #0 to max time, taking the 1/sr step
        x_time = np.asarray(x*1000000)

        vsnks.append(vsnk) #This will loop us through the channels an appropriate amount of time
        for vsnk in vsnks:
            for ch, channel in enumerate(vsnk): #Goes through each channel to sve data

                real = [datum.real for datum in channel.data()]
                imag = [datum.imag for datum in channel.data()]

                reals.append(real[begin_cutoff:]) #Formats real data into a 2D array
                imags.append(imag[begin_cutoff:])


        #PLOTTING
        #IMAG AND REAL
        '''Following the steps of: Setting up variables, making the individiual plots on the figure,
        rasterizing onto the PDF, adding note to ensure readers know there are less than tested samples visible'''
        #variables for placement of plot
        plot_img_width = 400
        plot_img_height = 375
        plot_img_pos_x = 150
        plot_img_pos_y = 50

        #calculating plot_sample_ratio
        plotted_samples = int(round(1/(int(it["wave_freq"])/sample_rate))num_output_waves)
        print(plotted_samples) #TODO: CALCULATE  THIS DIFFERENTLY FOR THE FFTs

        #Plotting the imaginary and real values
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2)
        plt.suptitle("Individual Channels' Amplitude versus Time for Run {}".format(counter))

        subPlot(x_time[0:plotted_samples], reals[0][0:plotted_samples], ax1, "Channel A", "Amplitude (volts)", "Time (\u03BCs)", y2=imags[0][0:plotted_samples], labels=("Real", "Imaginary"))
        subPlot(x_time[0:plotted_samples], reals[1][0:plotted_samples], ax2, "Channel B", "Amplitude (volts)", "Time (\u03BCs)", y2=imags[1][0:plotted_samples], labels=("Real", "Imaginary"))
        subPlot(x_time[0:plotted_samples], reals[2][0:plotted_samples], ax3, "Channel C", "Amplitude (volts)", "Time (\u03BCs)", y2=imags[2][0:plotted_samples], labels=("Real", "Imaginary"))
        subPlot(x_time[0:plotted_samples], reals[3][0:plotted_samples], ax4, "Channel D", "Amplitude (volts)", "Time (\u03BCs)", y2=imags[3][0:plotted_samples], labels=("Real", "Imaginary"))

        plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0) #Formatting the plots nicely

        #Rasterizes the plot/figures and converts to png)
        plotToPdf(plt, ("IQPlots_" + formattedDate), counter, pdf, plot_img_width, plot_img_height, plot_img_pos_x, plot_img_pos_y)

        #noting the number of samples
        note_x = plot_img_pos_x
        note_y = plot_img_pos_y + plot_img_height + 4
        note_font_size = 10

        #Number of samples note
        note = pdf.beginText(note_x, note_y)
        note.setFont(font, note_font_size)
        note.textOut("Note that the following plot only shows ")
        note.setFont(bold_font, note_font_size)
        note.textOut(str(plotted_samples) + "th")
        note.setFont(font, note_font_size)
        note.textOut("of the samples retrived. This was done for readability")
        pdf.drawText(note)


        #FFTS - STARTING NEW PAGE
        '''Following the steps of: Page Break on PDF, Set up variables (INCLUDING SETTING UP THE X AND Y TO BE FFT QUALIFIED), setting up the x axis view limit, plotting'''
        pdf.showPage()

        #Mathing the FFTs
        freq, fft_y = fftValues(x, reals, imags)

        #Plotting the individual FFT Plots
        fig2, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2)
        plt.suptitle("Individual Channels' FFTs for Run {}".format(counter))

        subPlot(freq, fft_y[0], ax1, "Channel A", "Power (dBm)", "Frequency (MHz)")
        subPlot(freq, fft_y[1], ax2, "Channel B", "Power (dBm)", "Frequency (MHz)")
        subPlot(freq, fft_y[2], ax3, "Channel C", "Power (dBm)", "Frequency (MHz)")
        subPlot(freq, fft_y[3], ax4, "Channel D", "Power (dBm)", "Frequency (MHz)")

        plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0) #Formatting the plots nicely

        #Rasterizes the plot/figures and converts to png)
        plotToPdf(plt, ("FFTPlots_" + formattedDate), counter, pdf, plot_img_width, plot_img_height, plot_img_pos_x, plot_img_pos_y)


    os.chdir(output_dir) #Ensuring we are saving in the output directory
    pdf.save() #saving the pdf
main(gen.ship_test_tx(4))









