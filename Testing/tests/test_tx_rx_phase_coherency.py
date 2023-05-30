from common import sigproc
from common import engine
from common import generator as gen
import numpy as np
import matplotlib.pyplot as plt
import sys
from rich.console import Console
from rich.table import Table

#Global Variables
num_channel = 4 #we know this will always be 4 because, rx or tx there is always 4

#Defines the wave equation, so it can be used to model input data
#PARAMS: frequency, amplitude, phase, time (which is the x data)
#RETURNS: Y 
def waveEquation(time, freq, amp, phase):
    
    y = amp**(i*(freq*time + phase)) #model for wave equation
    
    return y

##Merges the complex data by multiplying I and Q, then adding it to I
##PARAMS: real and imag
##RETURNS: data
def interpretComplex(real, imag):

    data = (real*imag)+imag
    
    return data


##Obtains the inputs for channel and formats them in manner we can work with
##PARAMS: channel
##RETURNS: vsnk, an array holding the details of the channel set up
def getInputs(channel):
    
    gen.dump(channel) #pulling info from generator

    #the actual collecting
    sample_count = channel["sample_count"]
    tx_stack = [ (10.0 , int(channel_tx["sample_count" ])) ]
    rx_stack = [ (10.25,  int(channel_rx["sample_count"])) ]
    vsnk = engine.run(channel["channels"], channel["wave_freq"], channel["sample_rate"], channel["center_freq"], channel["tx_gain"], channel["rx_gain"], tx_stack, rx_stack)
    
    ampl = channel["ampl"] #CHECK HOW TO ACTUALLY RUN THE MACHINE AT THIS AMP - if I can it will clean up more code in the main function
    
    #Turning the complex to an easy to work with array (multiply complex by real and adding it to real)
    data_points  = []
    for ch, channel in enumerate(vsnk):
        
        real = [datum.real for datum in channel.data()]
        imag = [datum.imag for datum in channel.data()]
        
        data_points.append(interpretComplex(real, imag)) #viktor said to interperet the complex data like this

    return data_points, ampl 


##Sets up an array of time that correlates to the discrete points of the given sample rate
##PARAMS: sample rate, sample count
##RETURNS: time array
def timeGet(samp_rate, sample_count):
    
    time = range(0, sample_count, (1/samp_rate) #setting up array represeting discrete points **MIGHT HAVE TO ADD 1 TO SAMP_COUNT**
                                                #the time step is one over the sample rate
    return time


def main(iterations):
    
    #get inputs and set them to respective arrays
    a, a_amp, a_sample_count = getInputs(0)
    b, b_amp, b_sample_count = getInputs(1)
    c, c_amp, c_sample_count = getInputs(2)
    d, d_amp, d_sample_count = getInputs(3)

    #X-Y plot of the data, with time as the X-axis, and amplitude as the Y-axis
    plt.subplot(2,2) #Setting up a base for the plots
    
    #getting the x axes
    a_time = timeGet(a[2], a_sample_count)
    b_time = timeGet(b[2], b_sample_count)
    c_time = timeGet(c[2], c_sample_count)
    d_time = timeGet(d[2], d_sample_count)
    
    #set up sub plots -- NOTE: would love to find out how to make this a callable function, but for now  this will do
    

                  

