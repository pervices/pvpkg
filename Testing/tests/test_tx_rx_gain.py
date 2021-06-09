from common import sigproc
from common import engine
from common import generator as gen
import sys

import numpy as np

from dataclasses import dataclass

failed_tx_low_it = []
failed_rx_low_it = []
failed_tx_high_it = []
failed_rx_high_it = []

@dataclass
class TestResult:
    config: dict
    areas: list
    passed: bool

#@dataclass
#class TestBatch:
    #passed: list
    #failed: list

def main(iterations, result):

    for it in iterations:
        result.config = it #The config for each iteration is the same. Currently config is just used to be ale to view the stuff that prints when calling gen.dump(it). THis may need to be modified in the future
        print("Now running: ")
        gen.dump(it) #Prints the paramters ro the test currently being run
        tx_stack = [ (10.0, it["sample_rate" ]) ] # One seconds worth.
        rx_stack = [ (10.5, it["sample_count"]) ]
        vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack) #runs the test
        area = [sigproc.absolute_area(channel.data()) for channel in vsnk] #checks the area under the channel, these should be increasing every time if the system is working
        result.areas.append(area)

    result.areas = np.array(result.areas).T.tolist() # Transpose areas, now the number should be increasing, if theyare not the test has failed

    result.passed = True
    for area in result.areas:
        if(area != sorted(area)): result.passed = False #marks the test as failed if the area for any channel is not increasing

number_of_channels = 4 #selects how many channels are being tested

tx_low = TestResult(dict(), list(), False)
rx_low = TestResult(dict(), list(), False)
tx_high = TestResult(dict(), list(), False)
rx_high = TestResult(dict(), list(), False)

#runs the test using a variety of setting
main(gen.lo_band_gain_tx(number_of_channels), tx_low)
main(gen.lo_band_gain_rx(number_of_channels), rx_low)
main(gen.hi_band_gain_tx(number_of_channels), tx_high)
main(gen.hi_band_gain_rx(number_of_channels), rx_high)

any_failed = False

def print_result(type_test, test_result):
    print(type_test)
    if(test_result.passed): print("Test passed at: ")
    else:
        print("Test failed at: ")
        any_failed = True
    gen.dump(test_result.config)
    print(test_result.areas)

print_result("Tx low", tx_low)
print_result("Rx_low", rx_low)
print_result("Tx_high", tx_high)
print_result("Rx_high", rx_high)

print(any_failed)

if(any_failed):#This part doesn't work properly
    print("A test failed")
    sys.exit(1) #exits with 3 to indicate that one of the tests failed
else:
    print("All tests passed")
    sys.exit(0)
