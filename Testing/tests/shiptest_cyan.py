# This file is used for generating a PDF report for cyan
# It should act like shiptest.py and generate a report that look the same as it

# IMPORTING LIBRARIES AND MODULES ---------------------------------------------
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

# -----------------------------------------------------------------------------

begin_cutoff_waves = 20 # how many waves to cut off before tracking data

# Global variables
center_freq = -1
sample_rate = -1
sample_count = -1
tx_gain = -1
rx_gain = -1
being_cutoff = -1
summary_info = []

# USER SET VARIABLES
channel_names = []

# Setup argument parsing
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
parser.add_argument('-b', '--strict', default = False, type=bool,  help="Exit the test as soon as any test fails")

args = parser.parse_args()
# Parse the input arguments
num_output_waves = args.displayed_waves
sigfigs = args.sigfigs
snr_min_check = args.snr
serial_num = args.serial
strict_mode = args.strict
freq_check_threshold = args.freq_threshold  # Frequency offset threshold
spur_check_threshold = args.spur_threshold
gain_check_threshold = args.gain_threshold
product = args.product
num_channels = args.num_channels

# Check the input arguments

# Validates num_output_waves
try:
    assert 1 <= num_output_waves <= 4
except AssertionError:
    print("ERROR: Can only display 1 to 4 waves per graph. Try again: ")
    num_output_waves = int(input("How many waves do you want shown on IQ graphs? "))
except ValueError:
    print("ERROR: Please only input integers. Try again: ")
    num_output_waves = int(input("How many waves do you want shown on IQ graphs? "))

# Validate number of sigfigs
try:
    assert 1 <= sigfigs <= 5
except ValueError:
    sys.exit("ERROR: Please only input integers. Try again: ")
except AssertionError:
    sys.exit("ERROR: For formatting, please input a value within 1 to 5. Try again:")

# Validate product and number of channels
try:
    if (product != 't' and product != 'v'):
        raise(ValueError)
except:
    sys.exit("Invalid product. Only v (Vaunt) and t (Crimson) supported")

channel_names = [
    "Channel A",
    "Channel B", 
    "Channel C", 
    "Channel D", 
    "Channel E", 
    "Channel F", 
    "Channel G", 
    "Channel H"
    ]

if(product == 'v'):
    max_channels = 4
if(product == 't'):
    max_channels = 8

try:
    assert 1 <= num_channels <= max_channels
except AssertionError:
    sys.exit("Invalid number of channels selected")

channel_names = channel_names[0:num_channels]

# Create the generator 
if(product == 'v'):
    generate = gen.ship_test_crimson(num_channels)
elif(product == 't'):
    generate = gen.ship_test_cyan(num_channels)

# SETTING UP PATH DIRECTORIES
current_dir = os.getcwd()
output_dir = current_dir + "/ship_reports"
plots_dir = output_dir + "/plots_" + formattedDate
os.makedirs(output_dir, exist_ok=True)
os.makedirs(plots_dir, exist_ok=True)

# Pull product unit info
os.system('touch shiptest_out.txt')
os.system('uhd_usrp_info  -s > shiptest_out.txt')

# Read unit info
server_ver = subprocess.getstatusoutput("cat shiptest_out.txt | grep 'Server Version' | cut --complement -d ':' -f1 ")[1]
fpga_ver = subprocess.getstatusoutput("cat shiptest_out.txt | grep 'FPGA' | cut --complement -d ':' -f1")[1]
UHD_ver = subprocess.getstatusoutput("cat shiptest_out.txt | grep 'UHD' | cut --complement -d 'g' -f1")[1]
unit_name = subprocess.getstatusoutput("cat shiptest_out.txt | grep 'Device Type' | cut --complement -d ':' -f1")[1]
unit_time = subprocess.getstatusoutput("cat shiptest_out.txt | grep -m1 'Date' | cut --complement -d ':' -f1")[1]
unit_rtm = subprocess.getstatusoutput("cat shiptest_out.txt | grep 'RTM' | cut --complement -d ':' -f1")[1]

# organizing info in order of time, tx, and rx using gterminal grep
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

class ShipTestReport:
    c = None
    w, h = landscape(letter)
    date = datetime.datetime.now()
    formattedDate = date.isoformat("-", "minutes")
    serial_num = None
    file_title = None
    doc_title = None
    page_count = 1
    graph_max = int(np.ceil(num_channels/4))
    multi = (graph_max > 1)
    page_total = ((2*graph_max)+2)*(8*(product == 'V' or product == 'v') + 6*(product == 'T' or product == 't')) + graph_max
    #Formatting Variables - just so they're easily accessible
    python_to_inch = 72
    font = "Times-Roman"
    gen_font_size = 12
    bold_font = "Times-Bold"
    rcParams['agg.path.chunksize'] = 115

    def __init__(self, serial_num = "SERIAL_UNDEF"):
        self.serial_num = serial_num
        self.file_title = "ship_report_" + serial_num + "_" + formattedDate + ".pdf"
        self.doc_title = "ship_report_" + serial_num + "_" + formattedDate

        self.c = canvas.Canvas(file_title, pagesize=landscape(letter))
        self.c.drawString(30, h - 50, "Line")
        h_img_data = open(current_dir + "/pervices-logo.png", "rb")
        header_img = ImageReader(h_img_data)

    def get_canvas(self):
        return self.c

    def save(self):
        c.showPage()
        c.save()

# Create title page with board info, title and unit info
def title_page(c):

    # Positional Values
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
    title = c.beginText()
    title.setTextOrigin(title_x, title_y)
    title.setFont(font, title_font_size)
    title.textLine(text=("Ship Test Report: " + unit_name + " - Serial Number: " + serial_num))
    c.drawText(title)

    #Printing out Important Details regarding the Machine
    #everything will be attached to unitList text object
    unitList = c.beginText(list_x, list_y)

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
    unitList.setFont(bold_font, list_font_size)
    unitList.textOut("Unit Time: ")
    unitList.setFont(font, list_font_size)
    unitList.textLine(unit_time)
    c.drawText(unitList)

    #Drawing Logo
    c.drawImage(header_img, logo_x, logo_y, logo_width, logo_height)

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
    board_table.wrapOn(c, board_width, board_height)
    board_table.drawOn(c, board_x, board_y)
    board_y -= rowHeight*11

    for z in range(graph_max): #This ensures theres columns per page

        if (z != 0): #If there are more than 4 channels, make another page for the board info
            board_x, board_y = 3, list_y - rowHeight*10
            global page_total
            page_total +=1
            global page_count
            page_count += 1
            c.showPage() #Page break on pdf
            c.drawText(title)
            c.drawImage(header_img, logo_x, logo_y, logo_width, logo_height)
            pg_x, pg_y = 650,10
            pg_num = c.beginText()
            pg_num.setTextOrigin(pg_x, pg_y)
            pg_num.setFont(font, 10)
            pg_num.textLine(text=("Page " + str(page_count) + " of " + str(page_total)))
            c.drawText(pg_num)

        start, end = z*4, (z*4)+4 #only have to be calculated once

        #Adding Tx Board Table
        board_info = [["TX Board Information: "], ["Board"], ["Branch"], ["Revision"], ["Date"], ["MCU Serial"], ["Fuse 00"], ["Fuse 02"], ["Fuse 03"], ["GCC"]]
        for i, name in zip(range(start, end), channel_names[start:end]):
            board_info[0].append(chr(65+i))
            for z in range(len(tx_info["TX: " + name])):
                board_info[z+1].append((tx_info["TX: " + name][z]))

        board_table = Table(board_info, rowHeights=rowHeight, style=board_styles)
        board_table.wrapOn(c, board_width, board_height)
        board_table.drawOn(c, board_x, board_y)
        board_y -= rowHeight*11

        #Adding Rx Board Table
        board_info = [["RX Board Information: "], ["Board"], ["Branch"], ["Revision"], ["Date"], ["MCU Serial"], ["Fuse 00"], ["Fuse 02"], ["Fuse 03"], ["GCC"]]

        for q, rxname in zip(range(start, end), channel_names[start:end]):
            board_info[0].append(chr(65+q))
            for z in range(len(rx_info["RX: " + rxname])):
                board_info[z+1].append((rx_info["RX: " + rxname][z]))

        board_table = Table(board_info, colWidths=colWidth, rowHeights=rowHeight, style=board_styles)
        board_table.wrapOn(c, board_width, board_height)
        board_table.drawOn(c, board_x, board_y)




def main():
    matplotlib.use('PDF')
    report = ShipTestReport(serial_num)
    title_page(report.get_canvas())
    report.save()

if __name__ == "__main__":
    main()









