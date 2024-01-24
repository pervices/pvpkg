# Generate single page PDF reports

import datetime
import os
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
    date = datetime.datetime.now()
    formattedDate = date.isoformat("-", "minutes")
    formattedDate = formattedDate.replace(':', '-')     # cant have ':' in file path
    file_title = None
    doc_title = None
    cursor_x = 50
    cursor_y = h-30
    current_page = 1
    num_channels = 4    # This should not be here for obvious reasons 
    
    def __init__(self, doc_title, serial_num = "SERIAL"):
        self.serial_num = serial_num
        self.file_title = "ship_report_" + doc_title + "_" + serial_num + "_" + self.formattedDate + ".pdf"
        self.doc_title = "ship_report_" + doc_title + "_" + serial_num + "_" + self.formattedDate

        self.c = canvas.Canvas(self.file_title, pagesize=letter)
        self.insert_page_header()
        self.insert_text(self.doc_title)

    def get_canvas(self):
        return self.c

    def insert_image(self, image, desc=None):
        # Get enough space
        self.move_cursor(122, 274)

        if (desc != None):
            self.insert_text(desc)

        self.c.drawImage(image, self.cursor_x, self.cursor_y, 367, 274)
        
    def get_image_io_stream(self) -> BytesIO:
        stream = BytesIO()
        return stream

    def insert_image_from_io_stream(self, stream: BytesIO, desc=None):
        stream.seek(0)
        image = ImageReader(stream)
        self.insert_image(image, desc)

    def insert_text(self, text):
        # Get enough space
        self.move_cursor(0, 11 + 2)
        # Create text and draw it
        t = self.c.beginText()
        t.setTextOrigin(self.cursor_x, self.cursor_y)
        t.setFont("Helvetica", 11)
        t.textLine(text)
        self.c.drawText(t)

    def insert_text_large(self, text):
        # Get enough space
        self.move_cursor(0, 26 + 2)
        # Create text and draw it
        t = self.c.beginText()
        t.setTextOrigin(self.cursor_x, self.cursor_y)
        t.setFont("Helvetica", 26)
        t.textLine(text)
        self.c.drawText(t)

    def insert_line_separator(self):
        # Get some space
        self.move_cursor(0, 13)
        self.c.line(50, self.cursor_y + 5, self.w - 50, self.cursor_y + 5)

    def move_cursor(self, x, y):
        # Move cursor by x y amount and insert new page if needed
        self.cursor_x += x
        self.cursor_y -= y
        # insert new page
        if (self.cursor_y < 30):
            self.c.showPage()
            self.cursor_y = self.h - 30
            self.current_page += 1
            self.insert_page_header()
    
    def new_page(self):
        self.c.showPage()
        self.cursor_y = self.h - 30
        self.current_page += 1
        self.insert_page_header()

    def save(self):
        self.c.showPage()
        self.c.save()

    def insert_logo(self):
        logo_img_data = open(os.getcwd() + "/pervices-logo.png", "rb")
        logo_img = ImageReader(logo_img_data)
        self.c.drawImage(logo_img, 476, self.h - 21, 43 ,15)

    def insert_table(self, table):
        pass

    def insert_page_header(self):
        # header
        t = self.c.beginText()
        t.setTextOrigin(50, self.h - 15)
        t.setFont("Helvetica", 8)
        t.textLine(self.doc_title)
        self.c.drawText(t)
        # page number
        pg = self.c.beginText()
        pg.setTextOrigin(562, self.h - 15)
        pg.setFont("Helvetica", 8)
        pg.textLine(str(self.current_page))
        self.c.drawText(pg)
        # logo
        self.insert_logo()
    
    def insert_title_page(self, title_text="Ship Test Report"):
        self.insert_text_large(title_text)
        self.insert_line_separator()
        self.insert_unit_list()
        self.insert_line_separator()
        self.insert_unit_table()
        self.new_page()

    def insert_unit_list(self):
        # Get the infomation needed
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

        os.system('rm shiptest_out.txt')

        self.insert_text("Computer Date: " + self.date.isoformat("-", "minutes"))
        self.insert_text("UHD Version : " + UHD_ver)
        self.insert_text("RTM : " + unit_rtm)
        self.insert_text("Server Version: " + server_ver)
        self.insert_text("FPGA Version: " + fpga_ver)
        self.insert_text("Unit Time: " + unit_time)
        self.insert_text("Unit Name: " + unit_name)

    def insert_unit_table(self):
        # organizing info in order of time, tx, and rx using gterminal grep
        os.system('uhd_usrp_info --all > shiptest_out.txt')
        os.system("touch hold.txt")
        os.system("grep '0/time/fw_version' shiptest_out.txt -A 15 > hold.txt")

        # Setting up time array to hold board data
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

        # Setting up rx dictionary to hold board data
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


        # Setting up tx dictionary to hold board data
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

        # Removing the temp files from the systems
        os.system("rm hold.txt")
        os.system("rm shiptest_out.txt")

        #Adding the time, tx, rx board info in a table
        board_styles = ([('GRID', (0,0), (self.num_channels+1, 9), 1, colors.black),
                        ('FONTSIZE', (1,4), (self.num_channels+1, 5),7.8),
                        ('BACKGROUND', (0, 0), (self.num_channels+1,0), '#D5D6D5'),
                        ('BACKGROUND', (0, 0), (0,9), '#D5D6D5')])
        
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

        #Time Board table
        board_info = [["Time Board Information: "], ["Board"], ["Branch"], ["Revision"], ["Date"], ["MCU Serial"], ["Fuse 00"], ["Fuse 02"], ["Fuse 03"], ["GCC"]]
        for z in range(len(time)):
            board_info[z+1].append((time[z]))

        board_table = Table(board_info, colWidths=colWidth, rowHeights=rowHeight, style=board_styles)
        board_table.wrapOn(pdf, board_width, board_height)
        board_table.drawOn(pdf, board_x, board_y)
        board_y -= rowHeight*11

        graph_max = int(np.ceil(self.num_channels/4))

        for z in range(graph_max): #This ensures theres columns per page

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
        
        self.new_page()
        

if __name__ == "__main__":
    report = ClassicShipTestReport("test_report")
    report.insert_title_page()

    for i in range(10):
        report.insert_text_large("Lorem Ipsum.")
        report.insert_text(" ")
        report.insert_text("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor")
        report.insert_text("incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis")
        report.insert_text("nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.")
        report.insert_text("Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore")
        report.insert_text("eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt")
        report.insert_text("in culpa qui officia deserunt mollit anim id est laborum.")
        report.insert_text(" ")

    # report.insert_table()

    report.save()