from gnuradio import blocks
from gnuradio import uhd
from gnuradio import gr
from common import crimson
from common import pdf_report
from common import test_args
from common import log
import time, sys, os

# Note that Tate has 80 GPIO pins
# The following is the mapping of the GPIO pins to the registers
#
#    pwr_en        : Power on the HDR board
#    hi_pwr_en     : Enable the high power branch
#    atten64..1    : Amount of attenuation (all will be summed together).
#                      9          8          7          6          5          4          3          2          1          0
#                +----------+----------+----------+----------+----------+----------+----------+----------+----------+----------+
# CHANNEL A:   9 | Reserved |   pwr_en | hi_pwr_en| atten64  | atten32  | atten16  | atten8   | atten4   | atten2   | atten1   |   0
#                +----------+----------+----------+----------+----------+----------+----------+----------+----------+----------+
# CHANNEL B:  19 | Reserved |   pwr_en | hi_pwr_en| atten64  | atten32  | atten16  | atten8   | atten4   | atten2   | atten1   |  10
#                +----------+----------+----------+----------+----------+----------+----------+----------+----------+----------+
# CHANNEL C:  29 | Reserved |   pwr_en | hi_pwr_en| atten64  | atten32  | atten16  | atten8   | atten4   | atten2   | atten1   |  20
#                +----------+----------+----------+----------+----------+----------+----------+----------+----------+----------+
# CHANNEL D:  39 | Reserved |   pwr_en | hi_pwr_en| atten64  | atten32  | atten16  | atten8   | atten4   | atten2   | atten1   |  30
#                +----------+----------+----------+----------+----------+----------+----------+----------+----------+----------+
# CHANNEL E:  49 | Reserved |   pwr_en | hi_pwr_en| atten64  | atten32  | atten16  | atten8   | atten4   | atten2   | atten1   |  40
#                +----------+----------+----------+----------+----------+----------+----------+----------+----------+----------+
# CHANNEL F:  59 | Reserved |   pwr_en | hi_pwr_en| atten64  | atten32  | atten16  | atten8   | atten4   | atten2   | atten1   |  50
#                +----------+----------+----------+----------+----------+----------+----------+----------+----------+----------+
# CHANNEL G:  69 | Reserved |   pwr_en | hi_pwr_en| atten64  | atten32  | atten16  | atten8   | atten4   | atten2   | atten1   |  60
#                +----------+----------+----------+----------+----------+----------+----------+----------+----------+----------+
# CHANNEL H:  79 | Reserved |   pwr_en | hi_pwr_en| atten64  | atten32  | atten16  | atten8   | atten4   | atten2   | atten1   |  70
#                +----------+----------+----------+----------+----------+----------+----------+----------+----------+----------+

def gpio_write(csrc, pins, mask, time):

    csrc.set_command_time(uhd.time_spec(time))
    csrc.set_user_register(0, (pins >>  0) & 0xFFFFFFFF) # 32bit.
    csrc.set_user_register(1, (pins >> 32) & 0xFFFFFFFF)
    csrc.set_user_register(2, (mask >>  0) & 0xFFFFFFFF)
    csrc.set_user_register(3, (mask >> 32) & 0xFFFFFFFF) # Queue.

def main():
    targs = test_args.TestArgs(testDesc="Stacked GPIO Commands Test")

    global report
    duration_s = 10
    test_failed = False
    report = pdf_report.ClassicShipTestReport("gpio", targs.serial, targs.report_dir, targs.docker_sha)

    if(targs.product == 'Tate'):
        report.insert_title_page("Cyan Stacked GPIO Commands Test")
        csrc = crimson.get_src_c(list(range(4)), 20e6, 15e6, 0.0) # Does not matter if sink or source is used here.
        pins = [0x0601806018060180, 0x6018]
        mask = [0xFFFFFFFFFFFFFFFF, 0xFFFF]

        report.insert_text_large("Test Results")

        for second in range(1, duration_s, 1):
            pins[0] ^= mask[0]
            pins[1] ^= mask[1]
            try:
                gpio_write(csrc, pins, mask, second);
            except:
                log.pvpkg_log_error("GPIO_STACK", "GPIO write failed at " + str(second) + " second")
                test_failed = True

        if (not test_failed):
            report.insert_text("Test ran for " + str(duration_s) + " seconds")
            report.insert_text("Test successfully completed")
        else:
            report.insert_text("Test failed")

    elif(targs.product == 'Lily'):
        report.insert_title_page("Chestnut Stacked GPIO Commands Test")
        csrc = crimson.get_src_c(list(range(4)), 20e6, 15e6, 0.0) # Does not matter if sink or source is used here.
        pins = [0x0601806018060180, 0x6018]
        mask = [0xFFFFFFFFFFFFFFFF, 0xFFFF]

        report.insert_text_large("Test Results")

        for second in range(1, duration_s, 1):
            pins[0] ^= mask[0]
            pins[1] ^= mask[1]
            try:
                gpio_write(csrc, pins, mask, second);
            except:
                log.pvpkg_log_error("GPIO_STACK", "GPIO write failed at " + str(second) + " second")
                test_failed = True

        if (not test_failed):
            report.insert_text("Test ran for " + str(duration_s) + " seconds")
            report.insert_text("Test successfully completed")
        else:
            report.insert_text("Test failed")

    elif(targs.product == "Vaunt"):
        report.insert_title_page("Crimson Stacked GPIO Commands Test")
        csrc = crimson.get_src_c(list(range(4)), 20312500, 15e6, 0.0) # Does not matter if sink or source is used here.
        pins = 0x0
        all = 0xFFFFFFFFFFFFFFFF; # 64bit.

        for second in range(1, duration_s, 1):
            pins ^= all
        try:
            gpio_write(csrc, pins, all, second);
        except:
            log.pvpkg_log_error("GPIO_STACK", "GPIO write failed at " + str(second) + " second")
            test_failed = True

        if (not test_failed):
            report.insert_text("Test ran for " + str(duration_s) + " seconds")
            report.insert_text("Test successfully completed")
        else:
            report.insert_text("Test failed")


    report.save()
    log.pvpkg_log_info("GPIO_STACK", "PDF report saved at " + report.get_filename())

    if (test_failed):
        sys.exit(1)

if __name__ == '__main__':
    main()

