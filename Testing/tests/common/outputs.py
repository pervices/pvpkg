import numpy as np

'''
table -- class that formats output data into a table
Author: Stella Rovazzi
'''
class Table:

    def __init__(self, title):
        self.title = title
        self.columns = []
        self.rows = []

    def addColumn(self, column):
        self.columns.append(column)

    def addRow(self, *row):
        self.rows.append(row)

    def printData(self):

        column_len = len(self.columns)

        #Setting Table Width
        lenSum = np.vectorize(len)
        width = sum(lenSum(self.columns))
        print(width)

        print("\n")
        print("{:^{}}".format(self.title, width) + "\n")

        #Making Format References
        row_format ="|{:<{display_width}}" * column_len
        header_format ="|{:^{display_width}}" * column_len

        #Printing the Table
        print(header_format.format(*self.columns, display_width=width) + "|")
        #print("\u2500" * full_width)
        for i in range(len(self.rows)):
            try:
                print(row_format.format(*self.rows[i], display_width=width) + "|")
                #print("\u2500" * full_width)
            except:
                print("ERROR: Number of columns is longer than length of rows")
                break;

