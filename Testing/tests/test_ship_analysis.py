#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 16:22:51 2022

@author: bmcq55
"""

from gnuradio import blocks
from gnuradio import uhd
from gnuradio import gr
from common import sigproc
from common import engine
from common import generator as gen
from common import crimson
from common import log
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


####-------------------------------INPUT DATA--------------------------------------------------------------------------------####
#path="/home/jade/bmch/Testing/tests/dump_20220621204459.728612" ## TODO: how to update this regardless of dump_file and ensure that it's sorted by time modified/created?? theres some os function that does this
#path="/home/jade/bmch/Testing/tests/dump_20220624191343.443462" ## TODO: how to update this regardless of dump_file and ensure that it's sorted by time modified/created?? theres some os function that does this
path="/home/bmch/Desktop/dump_20220801183448.236882"


file_list=os.listdir(path)        
directory = os.fsencode(path)

#CF_table = np.asarray(gen.center_freq_list)
# print(CF_table)
#CF_table_2=''.join('"' + item + '"' for item in CF_table)
#print(CF_table_2)
CF_table=["CF_50000000_", "CF_300000000_", "CF_600000000_", "CF_1200000000_", "CF_2400000000_", "CF_4000000000_", "CF_5000000000_", "CF_5500000000_"] #from generator program TODO: have this automatically taken from gen file
log.pvpkg_log_info("SHIP_ANALYSIS", len(CF_table))
#WF_table=["WF_-30000000_", "WF_160000000_", "WF_-162000000_", "WF_162000000_"]
center_freq_array=[]
wave_freq_array=[]
I_array_2=[] #array of I grouped in 4 Channels of same center frequency
Q_array_2=[] #array of Q grouped in 4 Channels of same center frequency
IQ_array_2=[] #array of IQ grouped in 4 Channels of same center frequency
for i in range(len(CF_table)):
    I_array=[]
    Q_array=[]
    IQ_array=[]
    channels_array=[]
    for file in os.listdir(directory):
        log.pvpkg_log_info("SHIP_ANALYSIS", 'the file name is', file)
        filename = os.fsdecode(file)
        #channels_array=[]
        if filename.endswith(".dat") and CF_table[i] in filename:
            
            with open(os.path.join(directory, file)) as f:
                
                content= f.read()
                data= np.fromstring(content, dtype='short') # converts to a numpy array
              
                #generator parameters parsed from file name
                wave_freq=re.findall("_WF_(\d+)_",filename)
                center_freq=re.findall("_CF_(\d+)_",filename)
                sample_rate=re.findall("_SR_(\d+)_",filename)
                gain=re.findall("_gain_(\d+)_",filename)
                sample_count=re.findall("_SC_(\d+)",filename)
                #channel=re.findall("CH_(\d+)", filename)
                sample_rate=int(sample_rate[0])
                wave_freq=int(wave_freq[0])
                wave_freq_array.append(wave_freq)
                center_freq=int(center_freq[0])
                center_freq_array.append(center_freq)
                gain=int(gain[0])
                sample_count=int(len(sample_count[0]))
                
                channel=re.findall("CH_(\d+)", filename)
                
                channel=int(channel[0])
                channels_array.append(channel)
                sample_count=np.linspace(0,2560,2560)
    

            # print('the file name is', filename)
            # print('channel and center_Freq is', channel, center_freq)
            
           
        
            #parses IQ samples from 4 channels at specific CF and assigns to array       
            I=[]
            for k in range(0,len(sample_count),1):
                sub_data=data[(2*k)]
                I.append(sub_data)
            I_array.append(I)
            
            Q=[]
            for n in range(0,len(sample_count),1):
                sub_data2=data[(2*n-1)]
                Q.append(sub_data2)
            Q_array.append(Q) 
            
            #IQ_array=[]
            I_arr=np.asarray(I)  #converted lists to numpy array
            Q_arr=np.asarray(Q)
            IQ= I_arr + 1j*Q_arr
            IQ_array.append(IQ)
            
    for w in range(0,1,1): #creates array of I samples for channel 0,1,2,3 for each CF
        #print ("rdb : " + str(len(I_array)))
        I_array_2.append(I_array)
       
    for v in range(0,1,1): #creates array Q samples for channel 0,1,2,3 for each CF
        Q_array_2.append(Q_array)
        
    for q in range(0,1, 1): #creates array of IQ complex samples for channel 0,1,2,3 for each CF
        IQ_array_2.append(IQ_array)
            

#####----------------------------TIME, SAMPLE AND FFT PLOTS--------------------------------------------------------------------####       



x=0      
for I, Q in zip(I_array_2, Q_array_2):
    log.pvpkg_log(x)
    
    
    plt.figure(1)
    fig1, axis= plt.subplots(2,2, figsize=(20,15))
    # plt.title("Amp vs. Sample Plot of center freq of {}".format(center_freq), loc='center')
    plt.figtext(0.1 ,0,("wave_Freq=",wave_freq, "center_freq=", center_freq_array[x], "sample rate=", sample_rate,"gain=",gain))
    
    axis[0,0].plot(sample_count[0:100], I[0][0:100], label='in-phase')
    axis[0,0].plot(sample_count[0:100],Q[0][0:100], label='quadrature')
    axis[0,1].plot(sample_count[0:100], I[1][0:100], label='in-phase')
    axis[0,1].plot(sample_count[0:100],Q[1][0:100], label='quadrature')
    axis[1,0].plot(sample_count[0:100], I[2][0:100], label='in-phase')
    axis[1,0].plot(sample_count[0:100],Q[2][0:100], label='quadrature')
    axis[1,1].plot(sample_count[0:100], I[3][0:100], label='in-phase')
    axis[1,1].plot(sample_count[0:100],Q[3][0:100], label='quadrature')

    axis[0,0].set_title("Amp vs. Sample Plot of channel {} with Center Freq {} Hz".format(channels_array[0], center_freq_array[x]), loc='center')
    axis[0,1].set_title("Amp vs. Sample Plot of channel {} with Center Freq {} Hz".format(channels_array[1], center_freq_array[x]), loc='center')
    axis[1,0].set_title("Amp vs. Sample Plot of channel {} with Center Freq {} Hz".format(channels_array[2], center_freq_array[x]), loc='center')
    axis[1,1].set_title("Amp vs. Sample Plot of channel {} with Center Freq {} Hz".format(channels_array[3], center_freq_array[x]), loc='center')
    x+=len(channels_array)
    plt.show()


#FFTs of 4 CH in each center freq
from scipy.fft import fft, fftfreq, fftshift
from scipy.signal import blackman

ywf_array=[]
xf_array=[]
for vec in IQ_array_2:
    for IQ in vec:
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
    new_ywf=ywf_array[len(channels_array)*x:len(channels_array)*x+len(channels_array)]
    new_xf=xf_array[len(channels_array)*x:len(channels_array)*x+len(channels_array)]
    # print(len(new_ywf))
    # print(len(new_xf))
    x+=1
    ywf_array_2.append(new_ywf)
    xf_array_2.append(new_xf)


#plotting non-normalized FFTs
x=0
for Fx, Fy in zip(xf_array_2, ywf_array_2):
    plt.figure(2)
    fig2, axis= plt.subplots(2,2, figsize=(20,15))
    # plt.title("Amp vs. Sample Plot of center freq of {}".format(center_freq), loc='center')
    plt.figtext(0.1 ,0,("wave_Freq=",wave_freq, "center_freq=", center_freq_array[x], "sample rate=", sample_rate,"gain=",gain))
    
    axis[0,0].plot(scipy.fftpack.fftshift(Fx[0]), scipy.fftpack.fftshift(np.abs(Fy[0])))
    axis[0,1].plot(scipy.fftpack.fftshift(Fx[1]), scipy.fftpack.fftshift(np.abs(Fy[1])))
    axis[1,0].plot(scipy.fftpack.fftshift(Fx[2]), scipy.fftpack.fftshift(np.abs(Fy[2])))
    axis[1,1].plot(scipy.fftpack.fftshift(Fx[3]), scipy.fftpack.fftshift(np.abs(Fy[3])))

    axis[0,0].set_title("Non-Normalized FFT of channel {} with Center Freq {} Hz".format(channels_array[0], center_freq_array[x]), loc='center')
    axis[0,1].set_title("Non-Normalized FFT of channel {} with Center Freq {} Hz".format(channels_array[1], center_freq_array[x]), loc='center')
    axis[1,0].set_title("Non-Normalized FFT of channel {} with Center Freq {} Hz".format(channels_array[2], center_freq_array[x]), loc='center')
    axis[1,1].set_title("Non-Normalized FFT of channel {} with Center Freq {} Hz".format(channels_array[3], center_freq_array[x]), loc='center')
    x+=len(channels_array)
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
    new_height_array=height[len(channels_array)*x:len(channels_array)*x + len(channels_array)]
    height_array.append(new_height_array)


#peaks_fx=[]
peaks_fy=[]
peaks_fx=[]
max_fy=[]
for ywf in ywf_array_normalized:
    for y in ywf:
        peaks_y=find_peaks(np.real(y), height=50)
        peaks_x,_=find_peaks(np.real(y), height=50)
        peak_max_fy=max(y)
        peaks_y = peaks_y[1]["peak_heights"]
        peaks_fy.append(peaks_y)
        peaks_fx.append(peaks_x)
        max_fy.append(peak_max_fy)

peaks_fy_array=[]
peaks_fx_array=[]
x=0
for x2,y2 in zip(peaks_fx, peaks_fy):
    new_fy=peaks_fy[len(channels_array)*x:len(channels_array)*x+len(channels_array)]
    new_fx=peaks_fx[len(channels_array)*x:len(channels_array)*x+len(channels_array)]
    x+=1
    peaks_fy_array.append(new_fy)
    peaks_fx_array.append(new_fx)

#average noise floor
average_NF=[]
for yf in ywf_array_normalized:
    for ywf in yf:
        sum_fft_bins=np.sum(ywf)
        avg=np.real(sum_fft_bins/len(ywf))
        avg_array=np.full([len(ywf)], avg)
        average_NF.append(avg_array)

#new_average_NF=np.asarray(average_NF, dtype=np.float32)
#putting average noise floor array 
avg_noise_floor_array=[]
x=0
for NF in range(0,len(CF_table),1):
    new_NF=average_NF[len(channels_array)*x:len(channels_array)*x+len(channels_array)]
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
    new_max=ywf_max_array[len(channels_array)*x:len(channels_array)*x+len(channels_array)]
    x+=1
    ywf_max_array_2.append(new_max)


xf_array_2_np=np.asarray(xf_array_2)
peaks_fx_array_np=np.asarray(peaks_fx_array)

# print(peaks_fx)
# #plotting normalized FFT

x=0
for Fx, Fy in zip(xf_array_2, ywf_array_normalized):
    x+=len(channels_array)
    log.pvpkg_log_info("SHIP_ANALYSIS", "the value of x 1 is",x)
    for f,NF in zip(xf_array_2, avg_noise_floor_array):
       
        log.pvpkg_log_info("SHIP_ANALYSIS", "the value of x 2 is",x)
        plt.figure(3)
        fig3, axis= plt.subplots(2,2, figsize=(20,15))    
        plt.figtext(0.1 ,0,("wave_Freq=",wave_freq, "center_freq=", center_freq_array[x], "sample rate=", sample_rate,"gain=",gain))
        
        #fig4, axis= plt.subplots(2,2, figsize=(20,15)) 

        axis[0,0].plot(scipy.fftpack.fftshift(Fx[0]), scipy.fftpack.fftshift(Fy[0]))
        axis[0,1].plot(scipy.fftpack.fftshift(Fx[1]), scipy.fftpack.fftshift(Fy[1]))
        axis[1,0].plot(scipy.fftpack.fftshift(Fx[2]), scipy.fftpack.fftshift(Fy[2]))
        axis[1,1].plot(scipy.fftpack.fftshift(Fx[3]), scipy.fftpack.fftshift(Fy[3]))
        
        axis[0,0].set_title("Normalized FFT of channel {} with Center Freq {} Hz".format(channels_array[0], center_freq_array[x]), loc='center')
        axis[0,1].set_title("Normalized FFT of channel {} with Center Freq {} Hz".format(channels_array[1], center_freq_array[x]), loc='center')
        axis[1,0].set_title("Normalized FFT of channel {} with Center Freq {} Hz".format(channels_array[2], center_freq_array[x]), loc='center')
        axis[1,1].set_title("Normalized FFT of channel {} with Center Freq {} Hz".format(channels_array[3], center_freq_array[x]), loc='center')
        axis[0,0].plot(scipy.fftpack.fftshift(f[0]), NF[0], label='NF= {} dB'.format(average_NF[x+0][0]))
        axis[0,1].plot(scipy.fftpack.fftshift(f[1]), NF[1], label='NF= {} dB'.format(average_NF[x+1][0]))
        axis[1,0].plot(scipy.fftpack.fftshift(f[2]), NF[2],label='NF= {} dB'.format(average_NF[x+2][0]))
        axis[1,1].plot(scipy.fftpack.fftshift(f[3]), NF[3],label='NF= {} dB'.format(average_NF[x+3][0]))
        axis[0,0].legend()
        axis[0,1].legend()
        axis[1,0].legend()
        axis[1,1].legend()
        
        
        
        for j in ywf_max_array_2:
            log.pvpkg_log_info("SHIP_ANALYSIS", 'the value is',j)
            i_new=0
            j_new1=j[0]
            j_new2=j[1]
            j_new3=j[2]
            j_new4=j[3]
            #print(i_new,j_new)
            #text=(int(j_new))
            #print('the text is',text)
            #plt.plot(peaks_y)
            axis[0,0].annotate(text=j_new1,xy=(i_new,j_new1), arrowprops=dict(facecolor='black', shrink=0.00005, width=0))
            axis[0,1].annotate(text=j_new2,xy=(i_new,j_new2), arrowprops=dict(facecolor='black', shrink=0.00005, width=0))
            axis[1,0].annotate(text=j_new3,xy=(i_new,j_new3), arrowprops=dict(facecolor='black', shrink=0.00005, width=0))
            axis[1,1].annotate(text=j_new4,xy=(i_new,j_new4), arrowprops=dict(facecolor='black', shrink=0.00005, width=0))
            
            plt.show(fig3)
            
        

# x=0
# for Fx,NF in zip(xf_array_2, avg_noise_floor_array):
    
#         fig4, axis= plt.subplots(2,2, figsize=(20,15)) 
#         axis[0,0].plot(scipy.fftpack.fftshift(Fx[0]), NF[0])
#         axis[0,1].plot(scipy.fftpack.fftshift(Fx[1]), NF[1])
#         axis[1,0].plot(scipy.fftpack.fftshift(Fx[2]), NF[2])
#         axis[1,1].plot(scipy.fftpack.fftshift(Fx[3]), NF[3])
        
#         plt.show(fig4)
        
#         x+=len(channels_array)
        
        # axis[0,0].plot(NF[0])
        # axis[0,1].plot(NF[1])
        # axis[1,0].plot(NF[2])
        # axis[1,1].plot(NF[3])
        
        
        
# for x_peak, y_peak in zip(peaks_fx_array, peaks_fy_array):
#         print(x_peak, y_peak)
        # text=(str(x_peak),str(y_peak))
        # #plt.plot(peaks_y)
        # plt.annotate(text,xy=(str(x_peak),str(y_peak)), arrowprops=dict(facecolor='black', shrink=0.00005, width=0))
        
        
        
        
        x+=len(channels_array)
        plt.show()
        plt.show(fig3)



#####----------------------------Testing PASS/FAIL--------------------------------------------------------------------####  






     

    # #plotting normalized FFT
    # plt.figure(7)
    # plt.title('normalized FFT with windowing')
    # plt.plot(scipy.fftpack.fftshift(xf), scipy.fftpack.fftshift(amp_dB_fs_new))
    # plt.xlabel('Frequency (Hz)')
    # plt.ylabel('Power(dB rel. to 1V rms)')
    
    
    
    
    # plt.figure(6)
    # plt.title('FFT with windowing')
    # plt.plot(xf[1:n//2], np.abs(ywf[1:n//2]), 'r')
    # plt.show()
    

        
                                
                    
                
                
                    # ##converts sample axis to time axis
                    # time=np.arange(0,len(Q)/sample_rate, 1/sample_rate)
                
                    # #plotting amplitude vs. time
                    # plt.figure()
                    # plt.title("Amp vs. Time Plot of {}")
                    # plt.xlabel("Time(seconds)")
                    # plt.ylabel("Amplitude")
                    # plt.plot(time[0:len(sample_count)], I,label='in-phase')
                    # plt.plot(time[0:len(sample_count)], Q,label='quadrature')
                    # plt.legend()
                    # plt.show()
                    
                    # n=len(IQ) # number of samples
                    # d=1/sample_rate # sample spacing
                    # bin_size=sample_rate/n
                    # #I_f=np.fft.fft(I_arr,norm='ortho')
                    # I_f=np.fft.fft(IQ)/bin_size
                    # #frequency-axis
                    # x_f=np.fft.fftfreq(n, d)
                    
                    # plt.figure()
                    # plt.title("NEW FFT")
                    # plt.plot(x_f,I_f)
                    # plt.show()
                    
                    # fig2=plt.figure(2)
                    # fig2, axs=plt.subplots(2,1)
                    # axs[0].plot(scipy.fftpack.fftshift(x_f),scipy.fftpack.fftshift(I_f))
                    # axs[0].set_xlabel('Frequency (Hz)')
                    # axs[0].set_ylabel('Power (ADC Resolution)')
                    # axs[0].set_title('Non-normalized and Normalized to dB FFT')
                    # #plt.figtext(0 ,1,("sample count=", len(sample_count), "sample rate=", sample_rate, 'amplitude=', amplitude))

                    # #converting to dB
                    # max_amp=20*np.log10(2**16)
                    # #amp_dB=20*np.log10((I_f)) * (1/bin_size)
                    # amp_dB=20*np.log10((I_f)) 
                    # amp_dB_fs=amp_dB - max_amp
                    # #amp_dB_fs=amp_dB

                    # #plotting normalized FFT
                    # axs[1].plot(scipy.fftpack.fftshift(x_f), scipy.fftpack.fftshift(amp_dB_fs))
                    # axs[1].set_xlabel('Frequency (Hz)')
                    # axs[1].set_ylabel('Power(dB)')
                    # plt.show()


                        # print('the length of IQ is', len(IQ))
                        # plt.figure(21)
                        # plt.title("I_F vs time")
                        # plt.plot(time[0:100], IQ[0:100])
                        # plt.show()
                        
                    # #IQ data in complex array and FFT parameters
                    # N= len(sample_count) #number of samples
                    # T= 1/sample_rate
                    # x=np.linspace(0,N*T,N) #discrete array of time samples
                    # #print("the length of x is",len(x))
                    # signal_freq=14850000
                    # I_arr=np.asarray(I)  #converted lists to numpy array
                    # Q_arr=np.asarray(Q)
                    # #IQ=((I_arr*np.cos(2*np.pi*signal_freq))**2 + (Q_arr*np.sin(2*np.pi*signal_freq))**2j) #function
                   
                    # IQ=10*np.log10(I_arr**2 + Q_arr**2j) #power in dB
                    # complex_array=np.sqrt(IQ) #amplitude complex valued array
                    # #print(complex_array)
                                 
                   
                    # #FFT of data
                    # signal_spectrum=np.fft.fftshift(np.fft.fft(complex_array))
                    # freqs = np.fft.fftshift(np.fft.fftfreq(len(complex_array), d=T))
                   
                    # #peak finding using scipy
                    # peaks_y=find_peaks(np.abs(signal_spectrum), height=1000)
                    # peaks,_=find_peaks(np.abs(signal_spectrum), height=1000)
                   
                   
                    # peaks_y = peaks_y[1]["peak_heights"]
                   
                    # #print("the peaks are:", peaks_y)
                    # #print("the first peak is", peaks_y[0])
                    # #print("the peaks array is:", peaks)
                   
                    # #plotting FFT 
                    # plt.figure()
                    # plt.plot(np.abs((signal_spectrum)))
                    # plt.plot(peaks,np.abs(signal_spectrum[peaks]),"o")
                    # #FFT peak markers
                    # for i,j in zip(peaks,peaks_y):
                    #     print(i,j)
                    #     text=(i,int(j))
                    #     plt.annotate(text,xy=(i,j), arrowprops=dict(facecolor='black', shrink=0.00005, width=0))
                    # plt.show()
                    
               
                 
                             
                 
                 
                 
                 # I_arr=np.array(I)  #converted lists to numpy array
                 # Q_arr=np.array(Q)
                 # complex_array=np.sqrt((I_arr)**2 + (Q_arr)**2j) #complex valued magnitude array
                 # print(complex_array)
                 
                 # N= 2560 #number of samples
                 # T= 1/sample_rate
                 # x=np.linspace(0,N*T,N)
                 
                 # #FFT of data
                 # signal_spectrum = np.fft.fftshift(np.fft.fft(complex_array))
                 # #freqs = np.fft.fftshift(np.fft.fftfreq(N, d=T))
                 
                 # #plotting FFT
                 # plt.figure()
                 # plt.plot(np.abs(signal_spectrum))
                 # plt.show()
                 
                 
















#       #     # print(os.path.join(directory, filename))
#       #     continue
#       # else:
#       #     continue
     
    





# #converts sample axis to time axis
# time=np.arange(0,len(Q)/sample_rate, 1/sample_rate)

# #plotting amplitude vs. time
# plt.figure()
# plt.title("Amp vs. Time Plot of {}".format(filename))
# plt.xlabel("Time(seconds)")
# plt.ylabel("Amplitude")
# plt.plot(time[0:500], I,label='in-phase')
# plt.plot(time[0:500], Q,label='quadrature')
# plt.legend()
# plt.show()
