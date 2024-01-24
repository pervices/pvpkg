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
    cursor_y = h-30
    
    def __init__(self, doc_title, serial_num = "SERIAL"):
        self.serial_num = serial_num
        self.file_title = "ship_report_" + doc_title + "_" + serial_num + "_" + self.formattedDate + ".pdf"
        self.doc_title = "ship_report_" + doc_title + "_" + serial_num + "_" + self.formattedDate

        self.c = canvas.Canvas(self.file_title, pagesize=letter)
        self.insert_text(self.doc_title)

    def get_canvas(self):
        return self.c

    def insert_image(self, image):
        if (self.cursor_y < 320):
            self.new_page()

        self.c.drawImage(image, self.cursor_x, self.cursor_y - 320, height=320)
        self.move_cursor(0, 330)    # Move by extra 10

    def get_image_io_stream(self) -> BytesIO:
        stream = BytesIO()
        return stream

    def insert_image_from_io_stream(self, stream: BytesIO):
        stream.seek(0)
        image = ImageReader(stream)
        self.insert_image(image)

    def insert_text(self, text):
        self.c.drawString(self.cursor_x, self.cursor_y, text)
        self.move_cursor(0, 18)

    def move_cursor(self, x, y):
        # Move cursor by x y amount and insert new page if needed
        self.cursor_x += x
        self.cursor_y -= y
        # insert new page
        if (self.cursor_y < 20):
            self.c.showPage()
            self.cursor_x = 50
            self.cursor_y = self.h - 30
    
    def new_page(self):
        self.c.showPage()
        self.cursor_x = 50
        self.cursor_y = self.h - 30

    def save(self):
        self.c.showPage()
        self.c.save()

if __name__ == "__main__":
    report = ClassicShipTestReport("test_report")
    report.insert_text("A quick brown fox jumps over a lazy dog.")
    report.save()