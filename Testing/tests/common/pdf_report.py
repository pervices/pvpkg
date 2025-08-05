# Generate single page PDF reports

import datetime
import os
import subprocess
import re
#PDF IMPORTS
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import Image, Paragraph, Table, Frame, TableStyle

from PIL import Image
from io import BytesIO
from reportlab.lib.utils import ImageReader

class ClassicShipTestReport:
    c = None            # The Canvas
    w, h = letter       # 612, 792
    date = datetime.datetime.now() #current date and time
    iso_time = date.strftime("%Y%m%d%H%M%S.%f")
    formattedDate = iso_time

    file_title = None
    doc_title = None
    output_dir = None
    # The cursor, things get drawn on the top right side of it
    cursor_x = 50
    cursor_y = h-30
    current_page = 1
    # This should not be here for obvious reasons
    num_channels = 4
    channel_names = ["Channel A", "Channel B", "Channel C", "Channel D"]
    # This stores the elements temporarily before calling draw all
    buffer = []

    def __init__(self, doc_title, serial_num = "SERIAL", output_dir = None, docker_sha = None):
        self.serial_num = serial_num
        self.docker_sha = docker_sha
        if output_dir == None:
            output_dir = str(os.getcwd())
        self.output_dir = output_dir
        self.doc_title  = self.formattedDate + "-" + doc_title + "-" + serial_num
        self.file_title = self.doc_title
        #NOTE: We later update the doc_title, file_title, and filename with unit_name 
        #      from the unit
        self.filename = self.output_dir + "/" + self.doc_title + ".pdf"

        self.c = canvas.Canvas(self.file_title, pagesize=letter, lang="en-US")
        self.c.setAuthor("Per Vices Corporation")
        self.c.setTitle(self.doc_title)
        self.c.setSubject("Automatic Ship Test Report")
        self.c.setCreator("Per Vices Corporation CI/CD Tooling")
        self.c.setProducer("Per Vices Corporation - pvpkg")


        self.insert_page_header()
        self.insert_text(self.doc_title)

    def get_canvas(self):
        return self.c

    def get_buffer(self):
        return self.buffer

    def get_filename(self):
        return self.c._filename

    """
        Put elements into the buffer
    """
    def buffer_put(self, element_type, content=None, desc=None):
        self.buffer.append([element_type, content, desc])

    def buffer_insert(self, element_type, content=None, desc=None, idx=0):
        self.buffer.insert(idx, [element_type, content, desc])

    """
        Draw from the buffer
    """
    def draw_from_buffer(self):
        for i in self.buffer:
            if i == None:
                break
            if i[0] == "image":
                self.insert_image(i[1], i[2])
            elif i[0] == "image_double":
                self.insert_image_double(i[1], i[2])
            elif i[0] == "image_quad":
                self.insert_image_quad_grid(i[1], i[2])
            elif i[0] == "image_octo":
                self.insert_image_octo_grid(i[1], i[2])
            elif i[0] == "image_list_dynamic":
                self.insert_image_list_dynamic(i[1], i[2])
            elif i[0] == "text":
                self.insert_text(i[1])
            elif i[0] == "text_large":
                self.insert_text_large(i[1])
            elif i[0] == "table":
                self.insert_table(i[1], 20, i[2])
            elif i[0] == "table_wide":
                self.insert_table(i[1], 0, i[2])
            elif i[0] == "table_large":
                self.insert_table(i[1], -10, i[2], 8)
            elif i[0] == "pagebreak":
                self.new_page()
            else:
                print("Wrong element type in report buffer")

    """
        Insert an image that spans the width of a page
    """
    def insert_image(self, image, desc=None):
        # Check space for both image and text
        if (self.cursor_y < 300):
            self.new_page()

        if (desc != None):
            # self.insert_line_separator()
            self.insert_text(desc)

        # Get enough space
        self.move_cursor(0, 274 + 5)

        self.c.drawImage(image, 122, self.cursor_y, 367, 274)

    """
        Insert two images side by side
    """
    def insert_image_double(self, images, desc=None):
        # Check y space for both image and text
        if (self.cursor_y < (187 + 16)):
            self.new_page()

        if (desc != None):
            # self.insert_line_separator()
            self.insert_text(desc)

        # Get enough space
        self.move_cursor(0, 187 + 3)

        try:
            self.c.drawImage(images[0], 50, self.cursor_y, 250, 187)
        except:
            print("Left image not found")
        try:
            self.c.drawImage(images[1], 312, self.cursor_y, 250, 187)
        except:
            print("Right image not found")

    """
        Insert an array of four images
    """
    def insert_image_quad_grid(self, images, desc=None):
        # Check space
        if (self.cursor_y < (374 + 16)):
            self.new_page()

        if (desc != None):
            self.insert_text(desc)

        # Get enough space
        self.move_cursor(0, 374 + 3)

        # Draw 4 image, each of size 250*187
        self.c.drawImage(images[0], 50, self.cursor_y + 187, 250, 187)
        self.c.drawImage(images[1], 312, self.cursor_y + 187, 250, 187)
        self.c.drawImage(images[2], 50, self.cursor_y, 250, 187)
        self.c.drawImage(images[3], 312, self.cursor_y, 250, 187)

    """
        Insert an array of eight images
    """
    def insert_image_octo_grid(self, images, desc=None):
        # Check space
        if (self.cursor_y < (720 + 13 + 5)):
            self.new_page()

        if (desc != None):
            self.insert_text(desc)

        # Get enough space
        self.move_cursor(0, 719)

        # Draw 8 image, each of size 250*187
        self.c.drawImage(images[0], 50, self.cursor_y + 180*3, 240, 180)
        self.c.drawImage(images[1], 332, self.cursor_y + 180*3, 240, 180)
        self.c.drawImage(images[2], 50, self.cursor_y + 180*2, 240, 180)
        self.c.drawImage(images[3], 332, self.cursor_y + 180*2, 240, 180)
        self.c.drawImage(images[4], 50, self.cursor_y + 180, 240, 180)
        self.c.drawImage(images[5], 332, self.cursor_y + 180, 240, 180)
        self.c.drawImage(images[6], 50, self.cursor_y, 240, 180)
        self.c.drawImage(images[7], 332, self.cursor_y, 240, 180)

    def insert_image_list_dynamic(self, images, desc=None):
        image_height = 187
        image_width = 250
        left_x_coord = 50
        right_x_coord = 312
        # Check space
        if (self.cursor_y < (image_height + 18)):
            self.new_page()

        if (desc != None):
            self.insert_text(desc)

        # # Get enough space
        self.move_cursor(0, image_height + 8)

        y_i = 0
        x_i = 0
        y_coord = 0
        for image in images:
            y_coord = self.cursor_y - (image_height*int(y_i/2))
            x_coord = left_x_coord if x_i % 2 == 0 else right_x_coord

            self.c.drawImage(image, x_coord, y_coord, image_width, image_height)

            y_i+=1
            x_i+=1

            if (y_coord < image_height) and (x_i % 2 == 0):
                self.new_page()
                self.move_cursor(0, image_height + 8)
                y_i = 0
                y_coord = self.cursor_y - (image_height*int(y_i/2))

        self.move_cursor(0, 8)

    """
        Return a BytesIO stream
    """
    def get_image_io_stream(self) -> BytesIO:
        stream = BytesIO()
        return stream

    """
        Read and insert an image from a BytesIO stream
    """
    def insert_image_from_io_stream(self, stream: BytesIO, desc=None):
        stream.seek(0)
        image = ImageReader(stream)
        self.insert_image(image, desc)

    """
        Read and return an image from a BytesIO stream
    """
    @staticmethod
    def get_image_from_io_stream(stream: BytesIO):
        stream.seek(0)
        image = ImageReader(stream)
        return image

    """
        Draw regular text
    """
    def insert_text(self, text):
        # Get enough space
        self.move_cursor(0, 11 + 2)
        # Create text and draw it
        t = self.c.beginText()
        t.setTextOrigin(self.cursor_x, self.cursor_y)
        t.setFont("Helvetica", 11)
        t.textLine(text)
        self.c.drawText(t)

    """
        Draw big text, used for titles
    """
    def insert_text_large(self, text):
        # Get enough space
        self.move_cursor(0, 26 + 2)
        # Create text and draw it
        t = self.c.beginText()
        t.setTextOrigin(self.cursor_x, self.cursor_y)
        t.setFont("Helvetica", 26)
        t.textLine(text)
        self.c.drawText(t)
        # Get some bottom space
        self.move_cursor(0, 3)

    """
        Draw a horizontal line
    """
    def insert_line_separator(self):
        # Get some space
        self.move_cursor(0, 13)
        self.c.line(65, self.cursor_y + 5, self.w - 65, self.cursor_y + 5)

    """
        Set the cursor
    """
    def set_cursor(self, x, y):
        self.cursor_x = x
        self.cursor_y = y

    """
        Move the cursor right/down, start a new page if cursor went outside of vertical border
    """
    def move_cursor(self, x, y):
        # Move cursor by x y amount and insert new page if needed
        self.cursor_x += x
        self.cursor_y -= y
        # insert new page
        if (self.cursor_y < 30):
            self.c.showPage()
            self.cursor_y = self.h - 30 - y     # move down again so nothing get cut off
            self.current_page += 1
            self.insert_page_header()

    """
        Start a new page
    """
    def new_page(self):
        self.c.showPage()
        self.cursor_y = self.h - 30
        self.current_page += 1
        self.insert_page_header()

    """
        Save the file, no more operations can be done after saving
    """
    def save(self):
        self.c.showPage()
        self.c.save()

    """
        Find and put the logo at the top right corner of page
    """
    def insert_logo(self):
        try:
            logo_img_data = open(os.getcwd() + "/pervices-logo.png", "rb")
            logo_img = ImageReader(logo_img_data)
            self.c.drawImage(logo_img, 476, self.h - 23, 43, 15)
        except:
            try:
                tmp_dir = os.getcwd()
                os.chdir("../")
                logo_img_data = open(os.getcwd() + "/pervices-logo.png", "rb")
                logo_img = ImageReader(logo_img_data)
                self.c.drawImage(logo_img, 476, self.h - 23, 43, 15)
                os.chdir(tmp_dir)
            except:
                try:
                    tmp_dir2 = os.getcwd()
                    os.chdir("../")
                    logo_img_data = open(os.getcwd() + "/pervices-logo.png", "rb")
                    logo_img = ImageReader(logo_img_data)
                    self.c.drawImage(logo_img, 476, self.h - 23, 43, 15)
                    os.chdir(tmp_dir2)
                except:
                    t = self.c.beginText()
                    t.setTextOrigin(476, self.h - 23)
                    t.setFont("Helvetica", 12)
                    t.textLine("Per Vices Corp.")
                    self.c.drawText(t)

    """
        Insert a table from an 2D array
        array format example:
        [
            ["Number", "Name", "Description"],
            ["1", "Apple", "some fruit"],
            ["2", "Orange", "some fruit"],
            ["3", "Lemon", "sour fruit"]
        ]
    """
    def __table_helper(self, data, x_offset = 0, title = None, fontsize = 10):
        rows = len(data)
        space_y_needed = rows * 18 + 5
        mStyle=[
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('FONTSIZE', (0,0), (-1,-1), fontsize)
                ]
        if (rows > 1):
            mStyle.append(('BACKGROUND', (0,0), (-1,0), '#D5D6D5'))
        input_table = Table(
            data,
            style=mStyle,
            splitByRow = 1,
            repeatRows = 1,
            repeatCols = 1
            )
        input_table.wrapOn(self.c, 400, 50)
        self.move_cursor(0, space_y_needed)

        if (title != None):
            self.move_cursor(0, 13)
            # Create text and draw it
            t = self.c.beginText()
            t.setTextOrigin(30 + x_offset, self.cursor_y + rows * 18 + 2)
            t.setFont("Helvetica", 11)
            t.textLine(title)
            self.c.drawText(t)

        input_table.drawOn(self.c, 30 + x_offset, self.cursor_y)

    def insert_table(self, data, x_offset = 0, title = None, fontsize = 10):
        for i in range(1, len(data), 35):       # max 35 rows per page, if larger split into multiple tables on separate pages
            if i != 1:
                self.new_page()                 # put each subsection of table on a new page
            table = data[i:i+35]
            table.insert(0, data[0])            # insert header at top of every table
            self.__table_helper(table, x_offset, title, fontsize)

    """
        Make the page header
    """
    def insert_page_header(self):
        # header
        t = self.c.beginText()
        t.setTextOrigin(50, self.h - 19)
        t.setFont("Helvetica", 8)
        t.textLine(self.doc_title)
        self.c.drawText(t)
        # page number
        pg = self.c.beginText()
        pg.setTextOrigin(562, self.h - 19)
        pg.setFont("Helvetica", 8)
        pg.textLine(str(self.current_page))
        self.c.drawText(pg)
        # logo
        self.insert_logo()
        # line
        self.c.line(30, self.h - 28, self.w - 30, self.h - 28)

    """
        Make the title page, including the DUT device specifications
    """
    def insert_title_page(self, title_text="Ship Test Report"):
        self.insert_text_large(title_text)
        self.insert_line_separator()
        self.insert_unit_list()
        self.insert_line_separator()
        self.insert_unit_table()
        self.new_page()

    def insert_unit_list(self):
        # Get the infomation needed
        # This is copied from shiptest.py

        #Using the terminal to pull unit info
        # os.system('rm ' + current_dir + '/shiptest_out.txt')
        os.system('touch shiptest_out.txt')
        os.system('uhd_usrp_info  -s > shiptest_out.txt')

        #Using terminal grep to set unit data
        server_ver = subprocess.getstatusoutput("cat shiptest_out.txt | grep Revision | cut --complement -d ':' -f1 | tr -d [:blank:] ")[1]
        fpga_ver = subprocess.getstatusoutput("cat shiptest_out.txt | grep 'FPGA' | cut --complement -d ':' -f1")[1]
        UHD_ver = subprocess.getstatusoutput("cat shiptest_out.txt | grep 'UHD' | grep -o -P '(?<=-g).*$'")[1]
        unit_name = subprocess.getstatusoutput("cat shiptest_out.txt | grep 'Device Type' | cut --complement -d ':' -f1 | tr -d [:blank:]")[1]
        unit_time = subprocess.getstatusoutput("cat shiptest_out.txt | grep -m1 'Date' | cut --complement -d ':' -f1")[1]
        unit_rtm = subprocess.getstatusoutput("cat shiptest_out.txt | grep 'RTM' | cut --complement -d ':' -f1")[1]
        hostname = subprocess.run(["cat /proc/sys/kernel/hostname | tr -d '\n' "], shell=True, capture_output=True, text=True).stdout
        operating_sys = subprocess.run(["cat /etc/os-release | grep PRETTY_NAME | cut -d '=' -f2 | tr -d '\"' | tr -d '\n' "], shell=True, capture_output=True, text=True).stdout
        pvpkg_commit = subprocess.run(["git describe --abbrev=8 --dirty --always --long | tr -d '\n' "], shell=True, capture_output=True, text=True).stdout
        pvpkg_branch = subprocess.run(["git rev-parse --abbrev-ref HEAD | tr -d '\n' "], shell=True, capture_output=True, text=True).stdout
        fpga_ddr = subprocess.run(["uhd_usrp_info --all | grep DDR | tr -d '\n' "], shell=True, capture_output=True, text=True).stdout
        cmp_time = subprocess.run(["uhd_manual_get --path /mboards/0/cmp_time | grep -Eo [0-9]+-[0-9]+-[0-9]+[[:blank:]][0-9]+:[0-9]+ | tr -d '\n' "], shell=True, capture_output=True, text=True).stdout
        cmp_time_parts = list(map(int, re.split('[-|:| ]', cmp_time)))

        os.system('rm shiptest_out.txt')

        # Update doc_title, file_title, and filename with the unit_name:
        self.doc_title  = self.doc_title + "-" + unit_name
        self.file_title = self.doc_title
        self.filename =  self.output_dir + "/" + self.doc_title + ".pdf"

        # Update actual pdf filename with unit name
        self.c._filename = self.filename

        self.insert_text("Hostname: " + hostname)
        self.insert_text("Operating System: " + operating_sys)
        if self.docker_sha != None:
            self.insert_text("Docker SHA: " + self.docker_sha)
        self.insert_text("Computer Date: " + self.date.isoformat("-", "minutes"))
        self.insert_text("UHD Version : " + UHD_ver)
        self.insert_text("pvpkg Version : " + pvpkg_commit)
        self.insert_text("pvpkg Branch : " + pvpkg_branch)
        self.insert_text("RTM : " + unit_rtm)
        self.insert_text("Server Version: " + server_ver)
        self.insert_text("FPGA Version: " + fpga_ver)
        self.insert_text("FPGA Time: " + datetime.datetime(*cmp_time_parts).isoformat("-", "minutes"))
        if "crimson" not in unit_name:
            self.insert_text(fpga_ddr)
        self.insert_text("Unit Time: " + unit_time)
        self.insert_text("Unit Name: " + unit_name)

    def insert_unit_table(self):
        # This is copied from shiptest.py

        # organizing info in order of time, tx, and rx using gterminal grep
        os.system('uhd_usrp_info --all > shiptest_out.txt')
        os.system("touch hold.txt")
        os.system("grep '0/time/fw_version' shiptest_out.txt -A 15 > hold.txt")

        # Setting up time array to hold board data
        time = []
        time.append(subprocess.getstatusoutput("cat hold.txt | grep 'Board Version' | cut --complement -d ':' -f1")[1])
        time.append(subprocess.getstatusoutput("cat hold.txt | grep 'Branch' | cut --complement -d ':' -f1")[1])
        time.append(" " + subprocess.getstatusoutput("cat hold.txt | grep -m1 'Revision' | cut --complement -d 'g' -f1")[1])
        time.append(subprocess.getstatusoutput("cat hold.txt | grep 'Date' | cut --complement -d ':' -f1")[1])
        time.append(subprocess.getstatusoutput("cat hold.txt | grep 'MCU Serial' | cut --complement -d ':' -f1")[1])
        time.append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse00' | cut --complement -d ':' -f1")[1])
        time.append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse02' | cut --complement -d ':' -f1")[1])
        time.append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse03' | cut --complement -d ':' -f1")[1])
        time.append(subprocess.getstatusoutput("cat hold.txt | grep 'GCC' | cut --complement -d ':' -f1")[1])

        num_channels = self.num_channels
        channel_names = self.channel_names

        # Setting up rx dictionary to hold board data
        rx_info = {}
        for i, name in zip(range(num_channels), channel_names): #NOTE: This might be more efficent with numpy arrays
            os.system("grep 'rx/{}/fw_version' shiptest_out.txt -A 15 > hold.txt".format(i))

            rx_info["RX: " + name] = []
            rx_info["RX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Board Version' | cut --complement -d ':' -f1")[1])
            rx_info["RX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Branch' | cut --complement -d ':' -f1")[1])
            rx_info["RX: " + name].append(" " + subprocess.getstatusoutput("cat hold.txt | grep -m1 'Revision' | cut --complement -d 'g' -f1")[1])
            rx_info["RX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Date' | cut --complement -d ':' -f1")[1])
            rx_info["RX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'MCU Serial' | cut --complement -d ':' -f1")[1])
            rx_info["RX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse00' | cut --complement -d ':' -f1")[1])
            rx_info["RX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse02' | cut --complement -d ':' -f1")[1])
            rx_info["RX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse03' | cut --complement -d ':' -f1")[1])
            rx_info["RX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'GCC' | cut --complement -d ':' -f1")[1])


        # Setting up tx dictionary to hold board data
        tx_info = {}
        for i, name in zip(range(num_channels), channel_names):
            os.system("grep 'tx/{}/fw_version' shiptest_out.txt -A 15 > hold.txt".format(i))
            tx_info["TX: " + name] = []
            tx_info["TX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Board Version' | cut --complement -d ':' -f1")[1])
            tx_info["TX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Branch' | cut --complement -d ':' -f1")[1])
            tx_info["TX: " + name].append(" " + subprocess.getstatusoutput("cat hold.txt | grep -m1 'Revision' | cut --complement -d 'g' -f1")[1])
            tx_info["TX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Date' | cut --complement -d ':' -f1")[1])
            tx_info["TX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'MCU Serial' | cut --complement -d ':' -f1")[1])
            tx_info["TX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse00' | cut --complement -d ':' -f1")[1])
            tx_info["TX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse02' | cut --complement -d ':' -f1")[1])
            tx_info["TX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'Fuse03' | cut --complement -d ':' -f1")[1])
            tx_info["TX: " + name].append(subprocess.getstatusoutput("cat hold.txt | grep 'GCC' | cut --complement -d ':' -f1")[1])

        # Removing the temp files from the systems
        os.system("rm hold.txt")
        os.system("rm shiptest_out.txt")

        #Adding the time, tx, rx board info in a table
        board_styles = ([
                        ('GRID', (0,0), (self.num_channels+1, 9), 1, colors.black),
                        ('FONTSIZE', (1,4), (self.num_channels+1, 5),7.8),
                        ('BACKGROUND', (0, 0), (self.num_channels+1,0), '#D5D6D5'),
                        ('BACKGROUND', (0, 0), (0,9), '#D5D6D5'),
                        ('VALIGN', (0,0), (-1, -1), 'MIDDLE')
                    ])


        #Positional Values
        title_font_size = 26
        title_x = 100
        title_y = 700
        list_font_size = 14
        list_x = title_x - 5
        list_y = title_y - 100
        logo_x, logo_y = 550, 450
        logo_width, logo_height = 200, 100
        board_width, board_height = 100, 100
        colWidth, rowHeight = (1.5*inch), (0.2*inch)
        board_x, board_y = 20, list_y - rowHeight*16.25

        #Time Board table
        board_info = [["Time Board Information: "], ["Board"], ["Branch"], ["Revision"], ["Date"], ["MCU Serial"], ["Fuse 00"], ["Fuse 02"], ["Fuse 03"], ["GCC"]]
        for z in range(len(time)):
            board_info[z+1].append((time[z]))

        board_table = Table(board_info, colWidths=colWidth, rowHeights=rowHeight, style=board_styles)
        board_table.wrapOn(self.c, board_width, board_height)
        board_table.drawOn(self.c, board_x, board_y)
        board_y -= rowHeight*11

        # graph_max = int(np.ceil(self.num_channels/4))
        graph_max = 1

        for z in range(graph_max): #This ensures theres columns per page

            start, end = z*4, (z*4)+4 #only have to be calculated once

            #Adding Tx Board Table
            board_info = [["TX Board Information: "], ["Board"], ["Branch"], ["Revision"], ["Date"], ["MCU Serial"], ["Fuse 00"], ["Fuse 02"], ["Fuse 03"], ["GCC"]]
            for i, name in zip(range(start, end), channel_names[start:end]):
                board_info[0].append(chr(65+i))
                for z in range(len(tx_info["TX: " + name])):
                    board_info[z+1].append((tx_info["TX: " + name][z]))

            board_table = Table(board_info, colWidths=colWidth, rowHeights=rowHeight, style=board_styles)
            board_table.wrapOn(self.c, board_width, board_height)
            board_table.drawOn(self.c, board_x, board_y)
            board_y -= rowHeight*11

            #Adding Rx Board Table
            board_info = [["RX Board Information: "], ["Board"], ["Branch"], ["Revision"], ["Date"], ["MCU Serial"], ["Fuse 00"], ["Fuse 02"], ["Fuse 03"], ["GCC"]]

            for q, rxname in zip(range(start, end), channel_names[start:end]):
                board_info[0].append(chr(65+q))
                for z in range(len(rx_info["RX: " + rxname])):
                    board_info[z+1].append((rx_info["RX: " + rxname][z]))

            board_table = Table(board_info, colWidths=colWidth, rowHeights=rowHeight, style=board_styles)
            board_table.wrapOn(self.c, board_width, board_height)
            board_table.drawOn(self.c, board_x, board_y)


if __name__ == "__main__":
    # Test Function

    report = ClassicShipTestReport("test_report")
    report.insert_title_page()

    for i in range(2):
        report.insert_text_large("Lorem Ipsum.")
        report.insert_text(" ")
        report.insert_text("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor")
        report.insert_text("incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis")
        report.insert_text("nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.")
        report.insert_text("Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore")
        report.insert_text("eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt")
        report.insert_text("in culpa qui officia deserunt mollit anim id est laborum.")
        report.insert_text(" ")

    try:
        test_pic_data = open(os.getcwd() + "/test-picture.png", "rb")
        test_pic = ImageReader(test_pic_data)
    except:
        print("cannot find " + os.getcwd() + "/test-picture.png")
        pass

    try:
        two_pictures = [test_pic, test_pic]
        report.buffer_put("image_double", two_pictures, desc="Double Picture grid")
    except:
        print("Cant draw double pictues")

    try:
        four_pictures = [test_pic, test_pic, test_pic, test_pic]
        report.buffer_put("image_quad", four_pictures, desc="Quadruple Picture grid")
    except:
        print("Cant draw quadruple pictues")

    try:
        eight_pictures = [test_pic, test_pic, test_pic, test_pic, test_pic, test_pic, test_pic, test_pic]
        report.buffer_put("image_octo", eight_pictures, desc="Octuple Picture grid")
    except:
        print("Cant draw Octuple pictues")

    try:
        eight_pictures = [test_pic, test_pic, test_pic, test_pic, test_pic, test_pic, test_pic, test_pic]
        report.buffer_put("image_list_dynamic", eight_pics, desc="Dynamic image list - 8")
    except:
        print("Cant draw dynamic image list pictues")

    test_long_table = [
        ["Run", "Baseline A", "Diff AB", "Diff AC", "Diff AD"],
        ["Mean", 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999, 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999],
        ["Mean", 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999, 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999],
        ["Mean", 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999, 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999],
        ["Mean", 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999, 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999],
        ["Mean", 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999, 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999],
        ["Mean", 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999, 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999],
        ["Mean", 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999, 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999],
        ["Mean", 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999, 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999],
        ["Mean", 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999, 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999],
        ["Mean", 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999, 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999],
        ["Mean", 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999, 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999],
        ["Mean", 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999, 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999],
        ["Mean", 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999, 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999],
        ["Mean", 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999, 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999],
        ["Mean", 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999, 9.9999999999999999, -9.9999999999999999, 0.9999999999999999, -9.9999999999999999]
    ]
    report.buffer_put("table_large", test_long_table, "A Long Table")

    report.draw_from_buffer()

    report.save()
