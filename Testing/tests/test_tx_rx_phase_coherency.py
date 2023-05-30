from common import sigproc
from common import engine
from common import generator as gen
import numpy as np
import matplotlib.pyplot as plt
import sys
#from rich.console import Console
#from rich.table import Table

#Global Variables
num_channel = 4 #we know this will always be 4 because, rx or tx there is always 4
default_ampl = 9830.1 #30% of max sc val, based of of GNU's default amp

'''
#Defines the wave equation, so it can be used to model input data
#PARAMS: frequency, amplitude, phase, time (which is the x data)
#RETURNS: Y
'''
def waveEquation(time, ampl, freq,  phase):
    
    y = ampl**(i*(freq*time + phase)) #model for wave equation
    
    return y


'''
##Merges the complex data by multiplying I and Q, then adding it to I
##PARAMS: real and imag
##RETURNS: data
'''
def interpretComplex(real, imag):

    data = (real*imag)+imag

    return data


'''
##sets units up to run with frequency parameters we want
##PARAMS: channel
##RETURNS: vsnk, sample_count
'''
def setInputs(channel):
    
    gen.dump(channel) #pulling info from generator

    #the actual collecting
    sample_count = channel["sample_count"]
    tx_stack = [ (10.0 , int(channel_tx["sample_count" ])) ] #ARE THESE THE BURST TIME
    rx_stack = [ (10.25,  int(channel_rx["sample_count"])) ]
    vsnk = engine.run(channel["channels"], channel["wave_freq"], channel["sample_rate"], channel["center_freq"], channel["tx_gain"], channel["rx_gain"], tx_stack, rx_stack, channel["ampl"])
    
    return vsnk, sample_count

'''
##Obtains the information from unit and formats them into formats we can work with
##PARAMS: channel, vsnk, sample_count
##RETURNS: data_points, x_time
'''
def getInputs(channel, vsnk, sample_count):
    
    data_points = []
    for ch, channel in enumerate(vsnk):

        #reworking the complex
        real = [datum.real for datum in channel.data()] ##MIGHT NOT BE ABLE TO PULL DATA LIKE THIS
        imag = [datum.imag for datum in channel.data()]
        
        data_points.append(interpretComplex(real, imag))
    
    #setting up the x values
    x_time = []
    x_time = timeGet(vsnk[2], sample_count) 
    
    return data_points, x_time, vsnk #these are  hopefully arrays


'''
##Sets up an array of time that correlates to the discrete points of the given sample rate
##PARAMS: sample rate, sample count
##RETURNS: time array
'''
def timeGet(samp_rate, sample_count):
    
    time = range(0, sample_count, (1/samp_rate)) #setting up array represeting discrete points **MIGHT HAVE TO ADD 1 TO SAMP_COUNT**
                                                #the time step is one over the sample rate
    return time

'''
##Makes plot with line of best fit for the wave eqn
##PARAMS: data, x_val, ax, snk_data
##RETURNS: plot, which can be assigned as a subplot
'''
def subPlot(data, x_val, ax, snk_data, name):
    #General formatting
    ax.set_title(name)
    ax.xlabel("Time (defined by Sample Rate)")
    ax.ylabel("Amplitude")
  
    #calculating line of best fit             
    param, covariance  = curve_fit(waveEquation, x_val, data) #using curve fit to have line of best ift
    best_fit = waveEquation(x_val, snk_data[8], snk_data[1], 0) #making the line of best fiit
                                                            #SETTING PHASE TO 0 FOR BEGINNING RIGHT NOW, WILL CLARIFY LATER
    #plotting data
    ax.plot(x_val, data, 'o', label="Discrete Points") #plotting normal points
    ax.plot(x_val, best_fit, '-', label="Best Fit") 
    
    return ax.plot()

'''
##plots input info, merged info, and prints table of other info
##PARAMS: iterations
##Returns: N/A
'''
def main(iterations):                                                 
    
    #setting up channels and retriving x and y information ~Must be better way to get snk values but im not sure how~
    a, a_x, a_vsnk  = getInputs(0, setInputs(0)) 
    b, b_x, b_vsnk  = getInputs(1, setInputs(1))  
    c, c_x, c_vsnk  = getInputs(2, setInputs(2))  
    d, d_x, d_vsnk  = getInputs(3, setInputs(3))  

    #X-Y plot of the data, with time as the X-axis, and amplitude as the Y-axis
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplot(2,2) #Setting up a base for the plots
    #set up sub plots -- NOTE: would love to find out how to make this a callable function, but for now  this will do
    fig.suptitle("Amplitude versus Time for Recieve Channels")
    subPlot(a, a_x, ax1, a_vsnk, "Channel A")
    subPlot(b, b_x, ax2, b_vsnk, "Channel B")
    subPlot(c, c_x, ax3, c_vsnk, "Channel C")
    subPlot(d, d_x, ax4, d_vsnk, "Channel D")

main(gen.lo_band_phaseCoherency_rx(4))                  
main(gen.lo_band_phaseCoherency_tx(4))                  

