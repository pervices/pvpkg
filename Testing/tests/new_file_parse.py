#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 19:24:42 2022

@author: bmch
"""
#Libraries and modules
from gnuradio import blocks
from gnuradio import uhd
from gnuradio import gr
from common import sigproc
from common import engine
from common import generator as gen
from common import crimson
from retrying import retry
import numpy as np
import matplotlib.pyplot as plt
import time
import os
import glob
#import test_ship_collection as tsc
import re
from scipy.signal import find_peaks
import scipy.fftpack
import glob   
import os
import calendar
from datetime import date
from matplotlib import rcParams
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox
import math

####-------------------------------INPUT DATA--------------------------------------------------------------------------------####

CF_table=["CF_50000000_", "CF_300000000_", "CF_600000000_", "CF_1200000000_", "CF_2400000000_", "CF_4000000000_", "CF_5000000000_", "CF_5500000000_"] #from generator program TODO: have this automatically taken from gen file
#CF_table=str(gen.Shiptest_Crimson1.center_freq_list) ###TODO: get this automatically. NEED THE 'CF'??
print('the CF table is', CF_table)
wave_freq_array=[]
center_freq_array=[]
IQ_array_2=[] #array of IQ grouped in 4 Channels of same center frequency
I_array=[]
Q_array=[]
channels_array=[]
IQ_array=[]

#Directory where shiptest_collection data is
#ath='/home/jade/Desktop/dump_20220805153333.187244'
current_dir=os.getcwd()
path= current_dir + '/shiptest_dump'

numbers= re.compile(r'(\d+)')
def  numerical_sort(value):
    parts= numbers.split(value)
    parts[1::2]=map(int, parts[1::2])
    return parts

# for infile in sorted(glob.glob('*.dat'), key=numerical_sort):
#     print("the infile being processed is:", infile)
    
os.chdir(path)
files = filter(os.path.isfile, os.listdir(path))
files = [os.path.join(path, f) for f in files] # add path to each file

#print(sorted(files))
chan=gen.Shiptest_Crimson1.channels 
for i in range(len(CF_table)):
    for file in sorted(files):
        if file.endswith(".dat") and CF_table[i] in file:
            #if file_num_table in file:
            #print("the file being procesed is:",file)
            I,Q=np.loadtxt(file, unpack=True)
            I_array.append(I)
            Q_array.append(Q)
   
            #generator parameters parsed from file name
            wave_freq=re.findall("_WF_(\d+)_",file)
            center_freq=re.findall("_CF_(\d+)_",file)
            sample_rate=re.findall("_SR_(\d+)_",file)
            gain=re.findall("_gain_(\d+)_",file)
            sample_count=re.findall("_SC_(\d+)",file)
            #channel=re.findall("CH_(\d+)", filename)
            sample_rate=int(sample_rate[0])
            wave_freq=int(wave_freq[0])
            wave_freq_array.append(wave_freq)
            center_freq=int(center_freq[0])
            center_freq_array.append(center_freq)
            gain=int(gain[0])
            sample_count=int(len(sample_count[0]))
            
            channel=re.findall("CH_(\d+)", file)
            
            channel=int(channel[0])
            channels_array.append(channel)
            sample_count=np.linspace(0,2560,2560)
            
            
            I_arr=np.asarray(I_array)  #converted lists to numpy array
            Q_arr=np.asarray(Q_array)
            #IQ_array=[]
            IQ= I_arr + 1j*Q_arr
            IQ_array.append(IQ)
        
            
        I_array_2=[] #8 arrays of I grouped in 4 Channels of same center frequency
        Q_array_2=[] #8 arrays of Q grouped in 4 Channels of same center frequency
        IQ_array_2=[]
        channels_array_2=[]
        center_freq_array_2=[]
        x=0
        for w in range(0,len(I_array),4): #creates array of I samples for channel 0,1,2,3 for each CF
            new_I_array=I_array[len(chan)*x:len(chan)*x+len(chan)]
            #print(new_I_array)
            x+=1
            I_array_2.append(new_I_array)
            

        x=0   
        for v in range(0,len(Q_array),4): #creates array Q samples for channel 0,1,2,3 for each CF
            new_Q_array=Q_array[len(chan)*x:len(chan)*x+len(chan)]
            x+=1
            Q_array_2.append(new_Q_array)
            
        x=0    
        for q in range(0,len(IQ_array), 4): #creates array of IQ complex samples for channel 0,1,2,3 for each CF
            new_IQ_array=IQ_array[len(chan)*x:len(chan)*x+len(chan)]
            x+=1
            IQ_array_2.append(new_IQ_array)
            
        x=0
        for c in range(0, len(channels_array),4): #creates array of channels for each CF
            new_chan=channels_array[len(chan)*x:len(chan)*x+len(chan)]
            #print(new_chan)
            x+=1
            channels_array_2.append(new_chan)
            
        x=0
        for f in range(0, len(center_freq_array),4): 
            new_cf=center_freq_array[len(chan)*x:len(chan)*x+len(chan)]
            x+=1
            center_freq_array_2.append(new_cf)
            

# #####----------------------------TIME, SAMPLE AND FFT PLOTS--------------------------------------------------------------------####       

output_path1=path +'/samp_vs_time'
os.makedirs(output_path1, exist_ok=True)
#output_path1="/home/jade/Desktop/dump_20220805153333.187244/samp_vs_time" ###TODO: Make this directory inside of where the data files are
os.chdir(output_path1)
#time series plots
x=0
#for c,f in zip(center_freq_array_2,channels_array_2):
for I, Q in zip(I_array_2, Q_array_2):
    print(x)
    print(center_freq_array_2[x][0],center_freq_array_2[x][1])
    print(channels_array_2[x][0],channels_array_2[x][1])
    #print(c,f)
    
    plt.figure(1)
    fig1, axis= plt.subplots(2,2, figsize=(6,6))
    #plt.title("Amp vs. Sample Plot of center freq of {}".format(center_freq), loc='center')
    plt.figtext(0.1 ,0,("wave_Freq=",wave_freq, "center_freq=", center_freq_array_2[x][1], "sample rate=", sample_rate,"gain=",gain))
    
    axis[0,0].plot(sample_count[0:100], I[0][0:100], label='in-phase')
    axis[0,0].plot(sample_count[0:100],Q[0][0:100], label='quadrature')
    axis[0,1].plot(sample_count[0:100], I[1][0:100], label='in-phase')
    axis[0,1].plot(sample_count[0:100],Q[1][0:100], label='quadrature')
    axis[1,0].plot(sample_count[0:100], I[2][0:100], label='in-phase')
    axis[1,0].plot(sample_count[0:100],Q[2][0:100], label='quadrature')
    axis[1,1].plot(sample_count[0:100], I[3][0:100], label='in-phase')
    axis[1,1].plot(sample_count[0:100],Q[3][0:100], label='quadrature')

    axis[0,0].set_title("Channel {}".format(channels_array_2[x][0], loc='center'))
    axis[0,1].set_title("Channel {}".format(channels_array_2[x][1], loc='center'))
    axis[1,0].set_title("Channel {}".format(channels_array_2[x][2], loc='center'))
    axis[1,1].set_title("Channel {}".format(channels_array_2[x][3], loc='center'))
    x+=1
    plt.savefig("samp_vs_time_{}.png".format(x))
    plt.show()
    


#FFTs of 4 CH in each center freq
from scipy.fft import fft, fftfreq, fftshift
from scipy.signal import blackman

ywf_array=[]
xf_array=[]
for vec in IQ_array_2:
    for IQ in vec[1]:
        #print(IQ)
        n=len(IQ) # number of samples
        d=1/sample_rate # sample spacing
        bin_size=sample_rate/n
        w=blackman(n)
    
        
        ywf=fft(IQ*w)
        ywf_array.append(ywf)
        xf=fftfreq(n,d)
        xf_array.append(xf)

# create array of 4 CH of each center_freq
ywf_array_2=[]
xf_array_2=[]
x=0
for x in range(0,len(CF_table),1):
    new_ywf=ywf_array[len(chan)*x:len(chan)*x+len(chan)]
    new_xf=xf_array[len(chan)*x:len(chan)*x+len(chan)]
    # print(len(new_ywf))
    # print(len(new_xf))
    x+=1
    ywf_array_2.append(new_ywf)
    xf_array_2.append(new_xf)


#plotting non-normalized FFTs
x=0
for Fx, Fy in zip(xf_array_2, ywf_array_2):
    plt.figure(2)
    fig2, axis= plt.subplots(2,2, figsize=(6,6))
    # plt.title("Amp vs. Sample Plot of center freq of {}".format(center_freq), loc='center')
    plt.figtext(0.1 ,0,("wave_Freq=",wave_freq, "center_freq=", center_freq_array[x], "sample rate=", sample_rate,"gain=",gain))
    
    axis[0,0].plot(scipy.fftpack.fftshift(Fx[0]), scipy.fftpack.fftshift(np.abs(Fy[0])))
    axis[0,1].plot(scipy.fftpack.fftshift(Fx[1]), scipy.fftpack.fftshift(np.abs(Fy[1])))
    axis[1,0].plot(scipy.fftpack.fftshift(Fx[2]), scipy.fftpack.fftshift(np.abs(Fy[2])))
    axis[1,1].plot(scipy.fftpack.fftshift(Fx[3]), scipy.fftpack.fftshift(np.abs(Fy[3])))

    axis[0,0].set_title("Channel {} with Center Freq {} Hz".format(channels_array_2[x][0], center_freq_array_2[x][0]), loc='center')
    axis[0,1].set_title("Channel {} with Center Freq {} Hz".format(channels_array_2[x][1], center_freq_array_2[x][1]), loc='center')
    axis[1,0].set_title("Channel {} with Center Freq {} Hz".format(channels_array_2[x][2], center_freq_array_2[x][2]), loc='center')
    axis[1,1].set_title("Channel {} with Center Freq {} Hz".format(channels_array_2[x][3], center_freq_array_2[x][3]), loc='center')
    x+=1
    plt.show()

#converting to dB 
ywf_array_normalized=[]
for Fy in ywf_array_2:
    max_amp_new=20*np.log(2**16)
    amp_dB_new=20*np.log(Fy)
    amp_dB_fs_new=amp_dB_new - max_amp_new
    ywf_array_normalized.append(amp_dB_fs_new)

    
#peak finding using scipy
#determining the height - 50dB will be the threshold for peak finding
max_peaks=[]
for h in ywf_array_normalized:
    for h_2 in h:
        height_max=max(h_2) 
        max_peaks.append(height_max)

height= np.array(max_peaks) - 50

height_array=[]
for x in range(0,len(CF_table),1):
    new_height_array=height[len(chan)*x:len(chan)*x + len(chan)]
    height_array.append(new_height_array)


#peaks_fx=[] 
peaks_fy=[] #xy-coordinate of peaks of the normalized FFT in grouped 4 channels/center freq
peaks_fx=[] 
max_fy=[]
for ywf in ywf_array_normalized:
    for y in ywf:
        peaks_y=find_peaks(np.real(y), height=[-500, 100], width=5)
        peaks_x,_=find_peaks(np.real(y), height=[-500, 100], width=5)
        peak_max_fy=max(y)
        peaks_y = peaks_y[1]["peak_heights"]
        peaks_fy.append(peaks_y)
        peaks_fx.append(peaks_x)
        max_fy.append(peak_max_fy)

peaks_fx_array=[]
x=0
for x in range(0,len(CF_table),1):
    new_fx=peaks_fx[len(chan)*x:len(chan)*x+len(chan)]
    peaks_fx_array.append(new_fx) 
    x+=1


peaks_fy_array=[]
for x in range(0,len(CF_table),1):
    new_fy=peaks_fy[len(chan)*x:len(chan)*x+len(chan)]
    peaks_fy_array.append(new_fy)
    x+=1
        
max_fy_array=np.array(max_fy)
max_fy_peaks=[]
for y in range(0, len(CF_table),1):
    #print("the value of y is:", y)
    new_max=max_fy_array[len(chan)*y:len(chan)*y+len(chan)]
    #print(new_max)
    max_fy_peaks.append(new_max)


#average noise floor
average_NF=[]
for yf in ywf_array_normalized:
    for ywf in yf:
        sum_fft_bins=np.sum(ywf)
        avg=np.real(sum_fft_bins/len(ywf))
        avg_array=np.full([len(ywf)], avg)
        average_NF.append(avg_array)       


#putting average noise floor array 
avg_noise_floor_array=[]
x=0
for NF in range(0,len(CF_table),1):
    new_NF=average_NF[len(chan)*x:len(chan)*x+len(chan)]
    x+=1
    avg_noise_floor_array.append(new_NF)

#finding max values of the FFT
ywf_max_array=[]
for v in ywf_array_normalized:
    for y in v:
        max_value=max(y)
        ywf_max_array.append(max_value)

ywf_max_array_2=[]
x=0
for m in range(0, len(CF_table),1):
    new_max=ywf_max_array[len(chan)*x:len(chan)*x+len(chan)]
    x+=1
    ywf_max_array_2.append(new_max)


xf_array_2_np=np.asarray(xf_array_2)
peaks_fx_array_np=np.asarray(peaks_fx_array)

#x-y coordinates of peaks
peak_x=[]
peak_y=[] 
for i, j in zip(peaks_fx_array, peaks_fy_array):
    #print('value issss', i, j)
    for a, b in zip(i,j):
        maxim=np.real(max(b))
        index, =np.where(b==maxim)
        print('the value 0 is', str(a[index]),maxim)
        peak_x.append(np.ndarray.item((a[index])))
        peak_y.append(maxim)
        
        
peak_x_array_2=[]
x=0
for c in range(0, len(CF_table),1):
    new_peak=peak_x[len(chan)*x:len(chan)*x+len(chan)]
    x+=1
    peak_x_array_2.append(new_peak)

peak_y_array_2=[]
x=0
for d in range(0, len(CF_table),1):
    new_peak=peak_y[len(chan)*x:len(chan)*x+len(chan)]
    x+=1
    peak_y_array_2.append(new_peak)
    
#sorting top 5 peaks highest to lowest
x=0
top_5_peaks=[]
for peak in range(0,len(CF_table),1):
    sort=peaks_fy_array[len(chan)*x:len(chan)*x+len(chan)]
    #print("the sorted number is",sort)
    for array in sort:
        #print("the value of i is",i)
        rank0=sorted(array[0], reverse=True)
        rank1=sorted(array[1], reverse=True)
        rank2=sorted(array[2], reverse=True)
        rank3=sorted(array[3], reverse=True)
        ranked0=rank0[0:5]
        ranked1=rank1[0:5]
        ranked2=rank2[0:5]
        ranked3=rank3[0:5]
        top_5_peaks.append(ranked0)
        top_5_peaks.append(ranked1)
        top_5_peaks.append(ranked2)
        top_5_peaks.append(ranked3)
    x+=1
    
top_5_peaks_by_CF=[]
x=0
for i in range(0, len(CF_table),1):
    new_peak=top_5_peaks[len(chan)*x:len(chan)*x+len(chan)]
    x+=1
    top_5_peaks_by_CF.append(new_peak)
    
#Dynamic Range of top 5 peaks
dynamic_range_array=[]
for p,NF in zip(top_5_peaks_by_CF, avg_noise_floor_array):
    for i,j in zip(p, NF):
        #print("the value of dynamic range is", p, NF[0:5])
        dynamic_range=abs(np.subtract(i,j[0:5]))
        dynamic_range_array.append(dynamic_range)
        
dynamic_range_by_CF=[]
x=0
for i in range(0, len(CF_table),1):
    new_dr=dynamic_range_array[len(chan)*x:len(chan)*x+len(chan)]
    x+=1
    dynamic_range_by_CF.append(new_dr)

output_path2=path +'/FFT_plots'
os.makedirs(output_path2, exist_ok=True)
os.chdir(output_path2)
x=0
for Fx, Fy, NF, xf,yf  in zip(xf_array_2, ywf_array_normalized, avg_noise_floor_array,peak_x_array_2, peak_y_array_2):
    #print("the value of xf,yf is:", xf[0],yf[0])
    #print("the value of xf,yf is:", xf[1],yf[1])

    plt.figure(3)
    fig3, axis= plt.subplots(2,2, figsize=(6,6))    
    #plt.figtext(0.1 ,0,("wave_Freq=",wave_freq, "center_freq=",center_freq_array[x], "sample rate=", sample_rate,"gain=",gain))        
    #fig4, axis= plt.subplots(2,2, figsize=(20,15)) 
    axis[0,0].plot(scipy.fftpack.fftshift(Fx[0]), scipy.fftpack.fftshift(Fy[0]))
    axis[0,1].plot(scipy.fftpack.fftshift(Fx[1]), scipy.fftpack.fftshift(Fy[1]))
    axis[1,0].plot(scipy.fftpack.fftshift(Fx[2]), scipy.fftpack.fftshift(Fy[2]))
    axis[1,1].plot(scipy.fftpack.fftshift(Fx[3]), scipy.fftpack.fftshift(Fy[3]))
        
    axis[0,0].set_title("Channel {}".format(channels_array_2[x][0], loc='center'))
    axis[0,1].set_title("Channel {}".format(channels_array_2[x][1], loc='center'))
    axis[1,0].set_title("Channel {}".format(channels_array_2[x][2], loc='center'))
    axis[1,1].set_title("Channel {}".format(channels_array_2[x][3], loc='center'))
        
    axis[0,0].plot(scipy.fftpack.fftshift(Fx[0]), NF[0], label='NF= {} dB'.format(round(NF[0][0])))
    axis[0,1].plot(scipy.fftpack.fftshift(Fx[1]), NF[1], label='NF= {} dB'.format(round(NF[1][0])))
    axis[1,0].plot(scipy.fftpack.fftshift(Fx[2]), NF[2],label='NF= {} dB'.format(round(NF[2][0])))
    axis[1,1].plot(scipy.fftpack.fftshift(Fx[3]), NF[3],label='NF= {} dB'.format(round(NF[3][0])))
    # axis[0,0].plot(scipy.fftpack.fftshift(Fx[0]), NF[0])
    # axis[0,1].plot(scipy.fftpack.fftshift(Fx[1]), NF[1])
    # axis[1,0].plot(scipy.fftpack.fftshift(Fx[2]), NF[2])
    # axis[1,1].plot(scipy.fftpack.fftshift(Fx[3]), NF[3])
    axis[0,0].legend(loc='lower center')
    axis[0,1].legend(loc='lower center')
    axis[1,0].legend(loc='lower center')
    axis[1,1].legend(loc='lower center')
    axis[0,0].annotate(text=str(round(yf[0])),xy=(xf[0],yf[0]), xytext=(xf[0],yf[0]), arrowprops=dict(facecolor='black', shrink=0.000005, width=0)) ###TODO: fix the arrow to the right x-y coord.
    axis[0,1].annotate(text=str(round(yf[1])),xy=(xf[1],yf[1]),xytext=(xf[1],yf[1]), arrowprops=dict(facecolor='black', shrink=0.000005, width=0))
    axis[1,0].annotate(text=str(round(yf[2])),xy=(xf[2],yf[2]),xytext=(xf[2],yf[2]), arrowprops=dict(facecolor='black', shrink=0.000005, width=0))
    axis[1,1].annotate(text=str(round(yf[3])),xy=(xf[3],yf[3]),xytext=(xf[3],yf[3]), arrowprops=dict(facecolor='black', shrink=0.000005, width=0))
    #plt.show(fig3)
    plt.savefig("FFT_plot{}.png".format(x))
    x+=1

#####----------------------------Table of Peaks, Dynamic range, SDR Info, and Testing PASS/FAIL--------------------------------------------------------------------####  

#Tables of 5 peaks, dynamic range
output_path3=path +'/peaks_table'
os.makedirs(output_path3, exist_ok=True)
os.chdir(output_path3)
for i in range(0,len(CF_table),1):
    fig, ax=plt.subplots(figsize=(6,6))
    rows=4
    cols=8
    ax.set_ylim(-1, rows + 1)
    ax.set_xlim(0, cols + .5)
    
    data=[{'freq': None,                                'channel': chan[0], 'Highest Peak': round(top_5_peaks_by_CF[i][0][0]), 'Dynamic Range':round(dynamic_range_by_CF[i][0][0]),  '2nd Highest Peak': round(top_5_peaks_by_CF[i][0][1]), '3rd Highest Peak': round(top_5_peaks_by_CF[i][0][2]), '4th Highest Peak':round(top_5_peaks_by_CF[i][0][3]),'5th Highest Peak': round(top_5_peaks_by_CF[i][0][4])},
          {'freq': None,                                'channel': chan[1], 'Highest Peak': round(top_5_peaks_by_CF[i][1][0]), 'Dynamic Range':round(dynamic_range_by_CF[i][1][0]),'2nd Highest Peak': round(top_5_peaks_by_CF[i][1][1]), '3rd Highest Peak': round(top_5_peaks_by_CF[i][1][2]), '4th Highest Peak': round(top_5_peaks_by_CF[i][1][3]),'5th Highest Peak': round(top_5_peaks_by_CF[i][1][4])},
          {'freq': None,                                'channel': chan[2], 'Highest Peak': round(top_5_peaks_by_CF[i][2][0]), 'Dynamic Range':round(dynamic_range_by_CF[i][2][0]),'2nd Highest Peak': round(top_5_peaks_by_CF[i][2][1]), '3rd Highest Peak': round(top_5_peaks_by_CF[i][2][2]), '4th Highest Peak': round(top_5_peaks_by_CF[i][2][3]),'5th Highest Peak': round(top_5_peaks_by_CF[i][2][4])},
          {'freq': round(center_freq_array_2[i][0]/1e6),'channel': chan[3], 'Highest Peak': round(top_5_peaks_by_CF[i][3][0]), 'Dynamic Range':round(dynamic_range_by_CF[i][3][0]),'2nd Highest Peak': round(top_5_peaks_by_CF[i][3][1]), '3rd Highest Peak': round(top_5_peaks_by_CF[i][3][2]), '4th Highest Peak': round(top_5_peaks_by_CF[i][3][3]),'5th Highest Peak': round(top_5_peaks_by_CF[i][3][4])}
          ]

    for row in range(rows):
        d=data[row]
        #freq column
        ax.text(x=.5, y=row, s=d['freq'], va='center', ha='left')
        #channel column
        ax.text(x=2, y=row, s=d['channel'], va='center', ha='center')
        #highest peaks columns
        ax.text(x=3, y=row, s=d['Highest Peak'], va='center', ha='right')
        ax.text(x=4, y=row, s=d['Dynamic Range'], va='center', ha='right')
        ax.text(x=5, y=row, s=d['2nd Highest Peak'], va='center', ha='right')
        ax.text(x=6, y=row, s=d['3rd Highest Peak'], va='center', ha='right')
        ax.text(x=7, y=row, s=d['4th Highest Peak'], va='center', ha='right')
        ax.text(x=8, y=row, s=d['5th Highest Peak'], va='center', ha='right')

        ax.text(.2, 3.5, 'Freq(MHz)', weight='bold', ha='left')
        ax.text(2, 3.5, 'Channel', weight='bold', ha='right')
        ax.text(3, 3.5, '1st Peak\n(dB)', weight='bold', ha='right')
        ax.text(4, 3.5, 'Dyn. Rng.\n(dB)', weight='bold', ha='right')
        ax.text(5, 3.5, '2nd Peak\n(dB)', weight='bold', ha='right')
        ax.text(6, 3.5, '3rd Peak\n(dB)', weight='bold', ha='right')
        ax.text(7, 3.5, '4th Peak\n(dB)', weight='bold', ha='right')
        ax.text(8, 3.5, '5th Peak\n(dB)', weight='bold', ha='right', va='bottom')
        ax.axis('off')
        for row in range(rows):
            ax.plot(
        	[0, cols + 1],
        	[row -.5, row - .5],
        	ls=':',
        	lw='.5',
        	c='grey'
        )

        ax.plot([0, cols + 1], [9.5, 9.5], lw='.5', c='black')
        ax.set_title("Top 5 Peaks and Dynamic Range at Center Frequency = {} MHz".format((center_freq_array_2[i][0])/1e6))
        plt.savefig("Top_5_peaks_table{}.png".format(i))
        #plt.show()

#image of uhd_usrp_info -v command 
output_path4=path +'/version_info'
os.makedirs(output_path4, exist_ok=True)
os.chdir(output_path4)
#Version info
fig, ax=plt.subplots(figsize=(14,10))
plt.axis('off')
output= str(gen.crimson_output)
plt.text(0,1, output)
plt.savefig('crimson_versions.png')
plt.show()

        
#Test that all channels at the frequency have equivalent gain (within 5dB of eachother)
test_info=[]
for i in max_fy_peaks:
    max_fy=np.real(max(i))
    min_fy=np.real(min(i))
    
    #test_info=[]
    if np.logical_and(i <= min_fy + 5, i >= max_fy - 5).all():
        test_out_pass=("Center Peaks= {}. \n FFT peak of all channels are within 5dB of one another, PASS".format(np.real(i)))
        test_info.append(test_out_pass)
        print(str(test_out_pass))

    else:
        test_out_fail=("Center Peaks= {}.FFT peak of all channels are NOT within 5dB of one another, FAIL".format(np.real(i)))
        test_info.append(test_out_fail)
        print(str(test_out_fail))
            
output_path5=path +'/version_info'
os.makedirs(output_path5, exist_ok=True)
os.chdir(output_path5)            
#testing info
fig, ax=plt.subplots(figsize=(14,10))
output= str(test_info)
plt.text(0.2,1, output)
plt.axis('off')
plt.savefig('testing.png')
plt.show()        
            
#####----------------------------Report Generation--------------------------------------------------------------------####  
from PIL import Image

#report directory
output_path6=path +'/report'
os.makedirs(output_path6, exist_ok=True)
os.chdir(output_path6)   

# set font
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'STIXGeneral'# set A4 paper

# Title Page
fig, ax = plt.subplots(figsize=(8.5, 11))  # Decorative Lines
ax.axvline(x=.01, ymin=0, ymax=1, color='grey', alpha=0.3, linewidth=120)
plt.axvline(x=.99, color='grey', alpha=0.3, linewidth=120)
logo = mpimg.imread('/home/jade/Desktop/dump_20220805153333.187244/pv-logo.png')
imagebox1 = OffsetImage(logo, zoom=1)
a = AnnotationBbox(imagebox1, (0.5, 0.6),frameon=False)
ax.add_artist(a)
ax.set_facecolor('white')
plt.axis('off')   
Header = 'CRIMSON TNG:\n SHIPTEST REPORT'
Contact = 'Date: {}'.format(date.today())
page = 'Page 1'
plt.annotate(Header, (.2,.7), weight='bold', fontsize=30, alpha=.6 )
plt.annotate(Contact, (.6,.1), weight='bold', fontsize=14,alpha=.6)
plt.annotate(page, (.48,.02), weight='medium', fontsize=10)
#plt.show()
plt.savefig('Title_page_1', dpi=300, bbox_inches='tight')

#page 2: Version info
fig, ax = plt.subplots(figsize=(8.5, 11))
plt.axis('off')
logo= Image.open('/home/jade/Desktop/dump_20220805153333.187244/pv-logo.png')
rsize_logo=logo.resize((np.array(logo.size)/2).astype(int))
#logo = mpimg.imread('/home/jade/Desktop/dump_20220805153333.187244/pv-logo.png')
imagebox = OffsetImage(rsize_logo, zoom=1)
a_logo = AnnotationBbox(imagebox, (0.48, 0.95),frameon=False)
ax.add_artist(a_logo)
#crimson_info= Image.open('/home/jade/Desktop/dump_20220805153333.187244/version_info/crimson_versions.png')
#rsize_info=crimson_info.resize((np.array(crimson_info.size)/2).astype(int))

crimson_info = mpimg.imread('/home/jade/Desktop/dump_20220805153333.187244/version_info/crimson_versions.png')
imagebox1 = OffsetImage(crimson_info, zoom=.3)
a1 = AnnotationBbox(imagebox1,(0.48, 0.5))
ax.add_artist(a1)
Header = 'UHD and Crimson Information' ###TODO: add the value automatically
page2= 'Page 2'
# add text
plt.annotate(Header, (.2,.85), weight='regular', fontsize=20, alpha=1)
plt.annotate(page2, (.48,.02), weight='medium', fontsize=10)
#plt.show()
plt.savefig('page_2', dpi=300, bbox_inches='tight')

#page 3: pass/fail
fig, ax = plt.subplots(figsize=(8.5, 11))
plt.axis('off')
logo= Image.open('/home/jade/Desktop/dump_20220805153333.187244/pv-logo.png')
rsize_logo=logo.resize((np.array(logo.size)/2).astype(int))
imagebox = OffsetImage(rsize_logo, zoom=1)
a_logo = AnnotationBbox(imagebox, (0.48, 0.95),frameon=False)
ax.add_artist(a_logo)
test_info = mpimg.imread("/home/jade/Desktop/dump_20220805153333.187244/test_info/testing.png" )
imagebox1 = OffsetImage(test_info, zoom=0.3)
a1 = AnnotationBbox(imagebox1, (0.48, 0.1),xybox=(0.48, 0.1),frameon=False)
ax.add_artist(a1)
Header = 'Testing Output' ###TODO: add the value automatically
page3= 'Page 3'
# add text
plt.annotate(Header, (.2,.85), weight='regular', fontsize=20, alpha=1)
plt.annotate(page3, (.48,.02), weight='medium', fontsize=10)
#plt.show()
plt.savefig('page_3', dpi=300, bbox_inches='tight')


#time plots report pages
time_plots_path= '/home/jade/Desktop/dump_20220805153333.187244/samp_vs_time/' ##TODO: MAKE PATH RELATIVE TO WHERE COLLECTION DUMP IS STORED
os.chdir(time_plots_path)
files = filter(os.path.isfile, os.listdir(time_plots_path))
files = [os.path.join(time_plots_path, f) for f in files] # add path to each file

i=0
for file in sorted(files):
    print("the file being procesed is:",file)
    fig, ax = plt.subplots(figsize=(8.5, 11))
    plt.axis('off')
    logo= Image.open('/home/jade/Desktop/dump_20220805153333.187244/pv-logo.png')
    rsize_logo=logo.resize((np.array(logo.size)/2).astype(int))
    imagebox = OffsetImage(rsize_logo, zoom=1)
    a_logo = AnnotationBbox(imagebox, (0.48, 0.95),frameon=False)
    ax.add_artist(a_logo)
    samp_time_plot_1 = mpimg.imread(file)
    imagebox1 = OffsetImage(samp_time_plot_1, zoom=1)
    a1 = AnnotationBbox(imagebox1, (0.48, 0.5),frameon=False)
    ax.add_artist(a1)
    Header = 'Time Plot for Center Frequency {} MHz'.format(gen.Shiptest_Crimson1.center_freq_list[i]/1e6) 
    page= 'Page {}'.format(4 + i)
    # add text
    plt.annotate(Header, (.1,.85), weight='regular', fontsize=20, alpha=1)
    plt.annotate(page, (.48,.02), weight='medium', fontsize=10)
    #plt.show()
    plt.savefig('/home/jade/Desktop/dump_20220805153333.187244/report/page_{}'.format(4+i), dpi=300, bbox_inches='tight')
    i+=1

# FFT plots report pages
FFT_plots_path= '/home/jade/Desktop/dump_20220805153333.187244/FFT_plots/' ##TODO: MAKE PATH RELATIVE TO WHERE COLLECTION DUMP IS STORED
os.chdir(FFT_plots_path)
files = filter(os.path.isfile, os.listdir(FFT_plots_path))
files = [os.path.join(FFT_plots_path, f) for f in files] # add path to each file

i=0
for file in sorted(files):
    print("the file being procesed is:",file)
    fig, ax = plt.subplots(figsize=(8.5, 11))
    plt.axis('off')
    logo= Image.open('/home/jade/Desktop/dump_20220805153333.187244/pv-logo.png')
    rsize_logo=logo.resize((np.array(logo.size)/2).astype(int))
    imagebox = OffsetImage(rsize_logo, zoom=1)
    a_logo = AnnotationBbox(imagebox, (0.48, 0.95),frameon=False)
    ax.add_artist(a_logo)
    FFT_plot_1 = mpimg.imread(file)
    imagebox2 = OffsetImage(FFT_plot_1, zoom=1)
    a2 = AnnotationBbox(imagebox2, (0.48, 0.5),frameon=False)
    ax.add_artist(a2)
    Header = 'FFT for Center Frequency {} MHz'.format((gen.Shiptest_Crimson1.center_freq_list[i]/1e6)) 
    page= 'Page {}'.format(11+i)
    # add text
    plt.annotate(Header, (.1,.85), weight='regular', fontsize=20, alpha=1 )
    plt.annotate(page3, (.48,.02), weight='medium', fontsize=10)
    plt.savefig('/home/jade/Desktop/dump_20220805153333.187244/report/page_{}'.format(12+i),dpi=300, bbox_inches='tight')
    i+=1

#Peaks table report pages
peaks_table_path= '/home/jade/Desktop/dump_20220805153333.187244/peaks_table/' ##TODO: MAKE PATH RELATIVE TO WHERE COLLECTION DUMP IS STORED
os.chdir(peaks_table_path)
files = filter(os.path.isfile, os.listdir(peaks_table_path))
files = [os.path.join(peaks_table_path, f) for f in files] # add path to each file

i=0
for file in sorted(files):
    print("the file being procesed is:",file)
    fig, ax = plt.subplots(figsize=(8.5, 11))
    plt.axis('off')
    logo= Image.open('/home/jade/Desktop/dump_20220805153333.187244/pv-logo.png')
    rsize_logo=logo.resize((np.array(logo.size)/2).astype(int))
    imagebox = OffsetImage(rsize_logo, zoom=1)
    a_logo = AnnotationBbox(imagebox, (0.48, 0.95),frameon=False)
    ax.add_artist(a_logo)
    Table_1 = mpimg.imread(file)
    imagebox2 = OffsetImage(Table_1, zoom=1)
    a3 = AnnotationBbox(imagebox2, (0.48, 0.5),frameon=False)
    ax.add_artist(a3)
    #Header = 'FFT Top 5 Peaks of Center Frequency' ###TODO: add the value automatically
    page4= 'Page {}'.format(20 + i)
    # add text
    #plt.annotate(Header, (.2,.9), weight='regular', fontsize=20, alpha=1 )
    plt.annotate(page4, (.48,.02), weight='medium', fontsize=10)
    plt.savefig('/home/jade/Desktop/dump_20220805153333.187244/report/page_{}'.format(20+i), dpi=300, bbox_inches='tight')
    i+=1

            
            
            
            
 