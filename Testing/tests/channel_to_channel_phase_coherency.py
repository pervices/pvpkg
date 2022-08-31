#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 18:59:34 2022

@author: bmch
"""

from common import sigproc
from common import engine
from common import generator as gen
from retrying import retry
import numpy as np
import matplotlib.pyplot as plt
import sys


@retry(stop_max_attempt_number = 3)
def test(it):

    gen.dump(it)

    # Collect.
    tx_stack = [ (10.0, it["sample_count" ]) ] # One seconds worth.
    rx_stack = [ (10.0, it["sample_count"]) ]
    vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
    error_detected = 0
    # Process.
    reals = []
    imags = []
    for ch, channel in enumerate(vsnk):

        real = [datum.real for datum in channel.data()]
        imag = [datum.imag for datum in channel.data()]
        #print('the value of the real array is', real)
        #print('the value of the imag array is', imag)

        reals.append(real)
        imags.append(imag)
        #print('the value of reals[0] is', reals[0])
        #print('the value of imags[0] is', imags[0])

        real_coherency = sigproc.lag(real, reals[0], it["sample_rate"], it["wave_freq"])
        imag_coherency = sigproc.lag(imag, imags[0], it["sample_rate"], it["wave_freq"])

        print("channel %2d: real coherency %f" % (ch, real_coherency))
        print("channel %2d: imag coherency %f" % (ch, imag_coherency))
        
def main(iterations):

    for it in iterations:
        test(it)

main(gen.lo_band_wave_sweep())
#main(gen.hi_band_wave_sweep())