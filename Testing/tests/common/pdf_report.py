# Generate single page PDF reports

#PDF IMPORTS
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import Image, Paragraph, Table, Frame, TableStyle

class ClassicShipTestReport:
    c = None    # The Canvas
    w, h = landscape(letter)
    date = datetime.datetime.now()
    formattedDate = date.isoformat("-", "minutes")
    file_title = None
    doc_title = None
    cursor_x = 30
    cursor_y = h-50
    
    def __init__(self, doc_title, serial_num = "SERIAL_UNDEF"):
        self.serial_num = serial_num
        self.file_title = "ship_report_" + doc_title + _ + serial_num + "_" + formattedDate + ".pdf"
        self.doc_title = "ship_report_" + doc_title + _ + serial_num + "_" + formattedDate

        self.c = canvas.Canvas(file_title, pagesize=landscape(letter))
        self.c.drawString(self.cursor_x, self.cursor_y, "Report")
        self.cursor_y += 30 

    def get_canvas(self):
        return self.c

    def insert_image(self, image):
        self.c.drawImage(image, cursor_x, cursor_y, 600, 400)

    def save(self):
        c.showPage()
        c.save()