import inspect
import sys

center_freq_list=[50000000, 300000000, 600000000, 1200000000, 2400000000, 4000000000, 5000000000, 5500000000]
# def ship_test():
#     print(sys._getframe().f_code.co_name)
#     channels = list(range(4))
#     wave_freq = 50000
#     sample_rate=int(325000000/325)
#     sample_count = 4096
#     tx_gain = 25
#     rx_gain = 25
#     for center_freq in center_freq_list:
#         yield locals()
        
class Shiptest_Crimson():
    def __init__(self, center_freq_list, channels, wave_freq, sample_rate, sample_count, tx_gain, rx_gain):
        #print(sys._getframe().f_code.co_name)
        self.center_freq_list=center_freq_list
        self.channels=channels
        self.sample_count=sample_count
        self.wave_freq=wave_freq
        self.sample_rate=sample_rate
        self.tx_gain=tx_gain
        self.rx_gain=rx_gain
        print(sample_rate, wave_freq, tx_gain)
        #self.center_freq=center_freq
        # for center_freq in self.center_freq_list:
        #     yield locals()
            
Shiptest_Crimson1=Shiptest_Crimson([50000000, 300000000, 600000000, 1200000000, 2400000000, 4000000000, 5000000000, 5500000000], list(range(4)), 50000, int(325000000/325), 4096, 25, 25)

#UHD_version
import os
stream = os.popen('uhd_find_devices')
uhd_output = stream.read()
#print(uhd_output)

#Crimson version info
stream = os.popen('uhd_usrp_info -v')
crimson_output = stream.read()
#print(crimson_output)
        
        

def hi_band_wave_sweep():

    print(sys._getframe().f_code.co_name)

    channels = list(range(4))
    sample_count = int(round(25000000/10000))
    tx_gain = 25
    rx_gain = 25
    center_freq = 1000000000
    sample_rate = 25000000
    for wave_freq in [ 500000, 600000, 700000, 800000, 900000, 1000000 ]:
        yield locals()

def hi_band_wave_easy():
    print(sys._getframe().f_code.co_name)

    channels = list(range(4))
    sample_rate = 9848485
    sample_count = int((round(9848485/1000)))
    #sample_count_tx = 9848485
    #sample_count_rx = int(round(9848485/1000))
    tx_gain = 25
    rx_gain = 25
    center_freq = 1000000000
    for wave_freq in [ 50000 ]:
        yield locals()

def lo_band_wave_sweep():

    print(sys._getframe().f_code.co_name)

    channels = list(range(4))
    sample_count = int(round(25000000/10000))
    tx_gain = 25
    rx_gain = 25
    center_freq = 10000000
    sample_rate = 25000000
    for wave_freq in [ 500000, 600000, 700000, 800000, 900000, 1000000 ]:
        yield locals()


def lo_band_quick():

    print(sys._getframe().f_code.co_name)

    channels = list(range(channels))
    wave_freq = 1000000
    sample_count = 10000
    tx_gain = 25
    rx_gain = 25
    center_freq = 15000000
    sample_rate = 10000000
    yield locals()


def lo_band_basic():

    print(sys._getframe().f_code.co_name)

    channels = list(range(4))
    wave_freq = 1000000
    sample_count = 256
    tx_gain = 25
    rx_gain = 25
    for center_freq in [ 15000000 ]:
        for sample_rate in [ 9848485, 25000000 ]:
            yield locals()


def hi_band_basic():

    print(sys._getframe().f_code.co_name)

    channels = list(range(4))
    wave_freq = 1000000
    sample_count = 256
    tx_gain = 25
    rx_gain = 25
    for center_freq in [ 1000000000, 2000000000, 3000000000, 4000000000 ]:
        for sample_rate in [ 9848485, 25000000, 36111111 ]:
            yield locals()

def lo_band_gain_rx(channels):

    print(sys._getframe().f_code.co_name)

    channels = list(range(channels))
    wave_freq = 1000000
    sample_count = 1000
    center_freq = 150000
    sample_rate = 9848485
    tx_gain = 10 #increasing the fixed gain may cause saturation
    for rx_gain in [ 5, 10, 20 ]:
        yield locals()


def lo_band_gain_tx(channels):

    print(sys._getframe().f_code.co_name)

    channels = list(range(channels))
    wave_freq = 1000000
    sample_count = 1000
    center_freq = 150000
    sample_rate = 9848485
    rx_gain = 10#increasing the fixed gain may cause saturation
    for tx_gain in [ 5, 10, 20 ]:
        yield locals()


def hi_band_gain_tx(channels):

    print(sys._getframe().f_code.co_name)

    channels = list(range(channels))
    wave_freq = 1000000
    sample_count = 1000
    center_freq = 2000000000
    sample_rate = 9848485
    rx_gain = 40#increasing the fixed gain may cause saturation
    for tx_gain in [ 5, 10, 20 ]:
        yield locals()


def hi_band_gain_rx(channels):

    print(sys._getframe().f_code.co_name)

    channels = list(range(channels))
    #print(channels)
    wave_freq = 1000000
    sample_count = 1000
    centre_freq = 2031250
    sample_rate = 4062500
    tx_gain = 40#increasing the fixed gain may cause saturation
    for rx_gain in [ 5, 10, 20 ]:
        yield locals()

def lo_band_phaseCoherency(channels):
    
    print(sys._getframe().f_code.co_name)
    

    channels = list(range(4))
    sample_count = int(round(25000000/10000))
    tx_gain = 25
    rx_gain = 25
    center_freq = 10000000
    sample_rate = 25000000
    wave_freq = 500000

    for i in range(10):
        yield locals()

def dump(iteration):
    for key, value in iteration.items():
        print("%20s : %r" % (key, value))

