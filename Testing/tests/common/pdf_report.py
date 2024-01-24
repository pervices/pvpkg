# Generate single page PDF reports

import datetime
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
    c = None    # The Canvas
    w, h = letter
    date = datetime.datetime.now()
    formattedDate = date.isoformat("-", "minutes")
    formattedDate = formattedDate.replace(':', '-')     # cant have ':' in file path
    file_title = None
    doc_title = None
    cursor_x = 50
    cursor_y = h-50
    
    def __init__(self, doc_title, serial_num = "SERIAL"):
        self.serial_num = serial_num
        self.file_title = "ship_report_" + doc_title + "_" + serial_num + "_" + self.formattedDate + ".pdf"
        self.doc_title = "ship_report_" + doc_title + "_" + serial_num + "_" + self.formattedDate

        self.c = canvas.Canvas(self.file_title, pagesize=letter)
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

    def move_cursor(self, x, y):
        # Move cursor by x y amount and insert new page if needed
        self.cursor_x += x
        self.cursor_y -= y
        # insert new page
        if (self.cursor_y < 50):
            self.c.showPage()
            self.cursor_x = 50
            self.cursor_y = self.h - 50
    
    def new_page(self):
        self.c.showPage()
        self.cursor_x = 50
        self.cursor_y = self.h - 50

    def save(self):
        self.c.showPage()
        self.c.save()

    def insert_table(self, table):
        pass

    def insert_page_header(self):
        pass
    
    def insert_title_page(self):
        pass

if __name__ == "__main__":
    report = ClassicShipTestReport("test_report")

    for i in range(10):
        report.insert_text_large("A quick brown fox jumps over a lazy dog.")

    report.save()