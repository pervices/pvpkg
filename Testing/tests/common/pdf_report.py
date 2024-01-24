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
        self.c.line(50, self.cursor_y + 6, self.w - 50, self.cursor_y + 6)

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
    
    def insert_title_page(self):
        self.insert_text_large("Title Text")
        self.insert_line_separator()
        self.insert_unit_list()
        self.insert_line_separator()
        self.insert_unit_table()
        self.new_page()

    def insert_unit_list(self):
        self.insert_text("Computer Date: ")
        self.insert_text("UHD Version : ")
        self.insert_text("RTM : ")
        self.insert_text("Server Version: ")
        self.insert_text("FPGA Version: ")
        self.insert_text("Unit Time: ")
    
    def insert_unit_table(self):
        self.insert_text("Time Board Information: ")
        pass

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