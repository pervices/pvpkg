#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 15:39:24 2022

@author: bmcq55
"""
import os
from common import sigproc
from common import engine
from common import generator as gen
from retrying import retry
import numpy as np
import matplotlib.pyplot as plt
import sys

from gnuradio import blocks
from gnuradio import uhd
from gnuradio import gr
from common import sigproc
from common import engine
from common import generator as gen
#from common import crimson
from retrying import retry
import numpy as np
import matplotlib.pyplot as plt
import time


#UHD and SDR information
print('the UHD output is', gen.uhd_output)
print('the crimson output is', gen.crimson_output)

def test(Shiptest_Crimson1):
    #gen.dump(it)
    # Collect.
    #tx_stack = [ (10.0, it["sample_count" ]) ] # One seconds worth.
    #rx_stack = [ (10.0, it["sample_count"]) ]
    for center_freq in gen.Shiptest_Crimson1.center_freq_list:
        
        tx_stack = [ (10.0, gen.Shiptest_Crimson1.sample_count) ] # One seconds worth.
        rx_stack = [ (10.0, int(gen.Shiptest_Crimson1.sample_count) ) ]
        vsnk = engine.run(gen.Shiptest_Crimson1.channels, gen.Shiptest_Crimson1.wave_freq, gen.Shiptest_Crimson1.sample_rate, center_freq, gen.Shiptest_Crimson1.tx_gain, gen.Shiptest_Crimson1.rx_gain, tx_stack, rx_stack)
        # def run(channels, wave_freq, sample_rate, center_freq, tx_gain, rx_gain, tx_stack, rx_stack):

        error_detected = 0
        # Process.
        reals = []
        imags = []
        #i=0
        for ch, channel in enumerate(vsnk):
        
            real = [datum.real for datum in channel.data()]
            imag = [datum.imag for datum in channel.data()]
            #print('the value of the real array is', real)
            #print('the value of the imag array is', imag)
    
            reals.append(real)
            imags.append(imag)
            #print('the value of reals[0] is', reals[0])
            #print('the value of imags[0] is', imags[0])
            
    
            sigproc.dump_file_shiptest(vsnk, gen.Shiptest_Crimson1.wave_freq, center_freq, gen.Shiptest_Crimson1.sample_rate, gen.Shiptest_Crimson1.tx_gain, gen.Shiptest_Crimson1.sample_count)
            
    

def main(iterations):

    #for it in iterations:
        test(gen.Shiptest_Crimson1)

#main(gen.ship_test())
main(gen.Shiptest_Crimson1)
# main(gen.ship_test_low())
# main(gen.ship_test_high())
main(gen.hi_band_wave_easy())
