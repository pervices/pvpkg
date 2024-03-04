from gnuradio import blocks
from gnuradio import uhd
from gnuradio import gr
from common import crimson
from common import pdf_report
import time, sys, os

#                                                 x x x x x x - - - x - - - - - x x x x x x x x x x x x x x x x x x x x x x x x x
# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
# 3 2 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0
#       6                   5                   4                   3                   2                   1

def gpio_write(csrc, pins, mask, time):

    csrc.set_command_time(uhd.time_spec(time))
    csrc.set_user_register(0, (pins >>  0) & 0xFFFFFFFF) # 32bit.
    csrc.set_user_register(1, (pins >> 32) & 0xFFFFFFFF)
    csrc.set_user_register(2, (mask >>  0) & 0xFFFFFFFF)
    csrc.set_user_register(3, (mask >> 32) & 0xFFFFFFFF) # Queue.


def main():

    global report
    duration_s = 128

    report = pdf_report.ClassicShipTestReport("gpio")
    report.insert_title_page("Crimson Stacked GPIO Commands Test")

    csrc = crimson.get_src_c(list(range(4)), 20e6, 15e6, 0.0) # Does not matter if sink or source is used here.
    pins = 0x0
    all = 0xFFFFFFFFFFFFFFFF; # 64bit.

    test_failed = False
    
    report.insert_text_large("Test Results")

    for second in range(1, duration_s, 1):
        pins ^= all
        try:
            gpio_write(csrc, pins, all, second);
        except:
            print("GPIO write failed at " + str(second) + " second")
            test_failed = True
        
    if (not test_failed):
        report.insert_text("Test ran for " + str(duration_s) + " seconds")
        report.insert_text("Test successfully completed")
    else: 
        report.insert_text("Test failed")
    
    report.save()
    print("PDF report saved at " + str(os.getcwd()) + "/" + report.get_filename())

if __name__ == '__main__':
    main()

