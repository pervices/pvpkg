import scipy.fftpack
import numpy as np
import sys
import os

from scipy import signal
from datetime import datetime

#Standardize dump file naming schemes and directories

#Use ISO time for filename creation
now = datetime.now() #current date and time
iso_time = now.strftime("%Y%m%d%H%M%S.%f")


parent_dir = "./"
leaf_dir = "dump/"
lead_dir_rawdat= iso_time + "-rawdat"
leaf_dir_shiptest = iso_time + "-shiptest"

dump_dir = parent_dir + leaf_dir
dump_path = os.path.join("./", dump_dir)
os.makedirs(dump_path,exist_ok=True)

rawdat_dir = parent_dir + leaf_dir + lead_dir_rawdat
rawdat_path = os.path.join("./", rawdat_dir)
#os.makedirs(rawdat_path,exist_ok=True)

shiptest_dump_dir = parent_dir + leaf_dir + leaf_dir_shiptest
shiptest_path=os.path.join("./", shiptest_dump_dir)
#os.makedirs(shiptest_path,exist_ok=True)

def dump(vsnk):
    sample_count = range(len(vsnk[0].data()))
    channels = range(len(vsnk))
    for sample in sample_count:
        for channel in channels:
            datum = vsnk[channel].data()[sample]
            sys.stdout.write("%10.5f %10.5f\t" % (datum.real, datum.imag))
        sys.stdout.write("\n")
    sys.stdout.write("\n")
    return None

def dump_file(vsnk, wave_freq):
    os.makedirs(rawdat_path,exist_ok=True)
    sample_count = range(len(vsnk[0].data()))
    channels = range(len(vsnk))
    for sample in sample_count:
        for channel in channels:
            datum = (vsnk[channel].data()[sample])
            #Writing to a file
            f = open(rawdat_path+"/CH_" + str(channel) + "_WF_" + str(wave_freq) + ".dat", "a")
            f.write("%10.5f %10.5f\t" % (datum.real, datum.imag) + "\n")
    return None

def dump_file_shiptest(vsnk, wave_freq, center_freq, sample_rate, tx_gain, sample_count):
    os.makedirs(shiptest_path,exist_ok=True)
    sample_count = range(len(vsnk[0].data()))
    channels = range(len(vsnk))
    for sample in sample_count:
        i=0
        for channel in channels:
            datum = (vsnk[channel].data()[sample])
            #Writing to a file
            f = open(shiptest_path + "/file_num_" + str(i) + "_CH_" + str(channel) + "_WF_" + str(wave_freq) + "_CF_" + str(center_freq) + "_SR_" + str(sample_rate) + "_gain_" + str(tx_gain) + "_SC_" + str(len(sample_count)) + ".dat", "a")
            f.write("%10.5f %10.5f\t" % (datum.real, datum.imag) + "\n")
            i+=1
    return None

def dump_file_shiptest_bin(vsnk, wave_freq, center_freq, sample_rate, tx_gain, sample_count):
    os.makedirs(rawdat_path,exist_ok=True)
    sample_count = range(len(vsnk[0].data()))
    channels = range(len(vsnk))
    for sample in sample_count:
        for channel in channels:
            datum = (vsnk[channel].data()[sample])
            #Writing to a file
            f = open(rawdat_path + "/CH_" + str(channel) + "_WF_" + str(wave_freq) + "_CF_" + str(center_freq) + "_SR_" + str(sample_rate) + "_gain_" + str(tx_gain) + "_SC_" + str(len(sample_count)) + ".dat", "a")
            byte_array=("%10.5f %10.5f\t" % (datum.real, datum.imag) + "\n")
            binary_format=bytearray(byte_array, encoding="ascii")
            #f.write( (datum.real, datum.imag) )
            #Or, try this - this should just store the array.
            f.write(binary_format)
    return None
    

def fundamental(real_wave, sample_rate):

    N = len(real_wave)
    T = 1.0 / sample_rate
    x  = np.linspace(int(0.0), int(N * T), int(N))
    xf = np.linspace(int(0.0), int(1.0 / (2.0 * T)), int(N / 2.0))
    yf = 2.0 / N * np.abs(scipy.fftpack.fft(real_wave)[:N // 2])
    indices = np.argwhere(yf > np.max(yf) / 2)

    return np.mean(xf[indices])

def fft_peaks(wave, sample_rate):

    N = len(wave)
    T = 1.0 / sample_rate
    yf = np.abs(scipy.fftpack.fft(wave))
    xf = scipy.fftpack.fftfreq(N, T)

    # Need to reorder frequency array such that the array goes from negative bound to positive bound (default is 0->pos, then jumps to neg->0).
    # If we don't, there is a discontinuity as we cross 0Hz and we are unable to detect peaks here.
    transfnc = xf.argsort()
    xf = xf[transfnc]
    yf = yf[transfnc]

    peaks, _ = signal.find_peaks(yf, height=(np.max(yf)/100), distance=100)

    return peaks, xf, yf


def absolute_area(complex_wave):

    return abs(np.trapz(np.absolute(complex_wave)))


def lag(real_wave, imag_wave, sample_rate, wave_freq):

    forewards = np.argmax(signal.correlate(real_wave, imag_wave)) - len(real_wave) + 1
    backwards = np.argmax(signal.correlate(imag_wave, real_wave)) - len(imag_wave) + 1
    #print("forwards value is", forewards)
    #print("backwards value is", backwards)

    # This is the lag in number of samples
    lag = (abs(forewards) + abs(backwards)) / 2.0
    # This is the lag in number of seconds:
    #   lag /= float(sample_rate)
    # This is the lag in wave_freq cycles, 0 = no lag, 0.5 = 180degrees lag:
    #   lag *= float(wave_freq)
    # Complete the above 2 steps in one to avoid rounding errors when dividing a small lag by a large sample rate
    return lag / (float(sample_rate) / float(wave_freq))

