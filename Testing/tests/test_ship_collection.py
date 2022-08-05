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


# def SDR_info():
#     MCU=
#     FPGA=
#     UHD=
#     server=


def test(it):
    gen.dump(it)
    # Collect.
    #tx_stack = [ (10.0, it["sample_count" ]) ] # One seconds worth.
    #rx_stack = [ (10.0, it["sample_count"]) ]
    tx_stack = [ (10.0, it["sample_count"]) ] # One seconds worth.
    rx_stack = [ (10.0, int(it["sample_count"]) ) ]
    vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
    
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
        

        sigproc.dump_file_shiptest(vsnk, it["wave_freq"], it["center_freq"], it["sample_rate"], it["tx_gain"], it["sample_count"])
        #sigproc.dump_file_shiptest_bin(vsnk, it["wave_freq"], it["center_freq"], it["sample_rate"], it["tx_gain"], it["sample_count"])
        #i=i+1
        
        


def main(iterations):

    for it in iterations:
        test(it)

main(gen.ship_test())
# main(gen.ship_test_low())
# main(gen.ship_test_high())
#main(gen.hi_band_wave_easy())
