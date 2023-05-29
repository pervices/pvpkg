from common import sigproc
from common import engine
from common import generator as gen
import numpy as np
import matplotlib.pyplot as plt
import sys
from rich.console import Console
from rich.table import Table

#Global Variables, set up to be 2D arrays, so you can append the arrays that result from the inputs

#Defines the wave equation, so it can be used to model input data
def waveEquation(freq, amp, phase, time):
    y = amp**(i*(freq*time + phase)) #model for wave equation
    return y

#Obtains the inputs for channel                              
def getInputs(channel_rx, channel_):
    gen.dump(channel)
    '''sample_count = channel["sample_count"]
    tx_stack = [ (channel["burst_start"], int(channel["sample_count" ])) ]
    rx_stack = [ (10.0, int(channel["sample_count"])) ]
    vsnk = engine.run(channel["channels"], channel["wave_freq"], channel["sample_rate"], channel["center_freq"], channel["tx_gain"], channel["rx_gain"], tx_stack, rx_stack)''' #THis be looking sussy, GOAL: trying to set up the input sequence to be a seperate function, so the main is not as cluttered
    vsnks.append(vsnk)

def main(iterations):
    


