import inspect
import sys

def ship_test_crimson(channels):

    print(sys._getframe().f_code.co_name)

    channels = list(range(channels))
    wave_freq = 100000
    sample_rate = 9848485
    sample_count = int(sample_rate/ 10)
    # The highest frequency uses a higher gain because the signal begins to roll off as the frequency gets higher
    tx_gains = [25, 25, 25, 25, 25, 25, 25, 30]
    rx_gains = [25, 25, 25, 25, 25, 25, 25, 30]
    center_freqs = [5000000, 300000000, 600000000, 1200000000, 2400000000, 4000000000, 5000000000, 5500000000]
    # #name = "Tx Operation"
    # for center_freq in [25000000, 300000000, 600000000]: #Just so my tests can go faster
    #     yield locals()
    for tx_gain, rx_gain, center_freq in zip(tx_gains, rx_gains, center_freqs):
        yield locals()

def ship_test_cyan(channels):

    print(sys._getframe().f_code.co_name)

    channels = list(range(channels))
    wave_freq = 100000
    sample_rate = 9803922
    sample_count = int(sample_rate/ 10)
    # rx_gain = 16
    # tx_gain = 15
    # for center_freq in [0, 200000000]:
    #         yield locals()
    for rx_gain, tx_gain, center_hold in zip([16, 43.5, 44], [15, 15, 26.5], [[0, 200000000], [1000000000, 5000000000], [7000000000, 15000000000]]):
        for center_freq in center_hold:
            yield locals()


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
    center_freq = 2000000000
    sample_rate = 4062500
    tx_gain = 40#increasing the fixed gain may cause saturation
    for rx_gain in [ 10, 20, 30 ]:
        yield locals()

def lo_band_phaseCoherency(channels):
    print(sys._getframe().f_code.co_name)
    channels = list(range(4))
    sample_count = int(round(25000000/10000))
    tx_gain = 25
    rx_gain = 25
    center_freq = 10000000
    wave_freq = 500000
    for i in range(10):
        yield locals()

def lo_band_phaseCoherency_short(channels):
    print(sys._getframe().f_code.co_name)
    channels = list(range(4))
    sample_count = int(round(25000000/10000))
    tx_gain = 25
    rx_gain = 25
    center_freq = 10000000
    sample_rate = 25000000
    wave_freq = 500000
    for i in range(2):
        yield locals()

def dump(iteration):
    for key, value in iteration.items():
        print("%20s : %r" % (key, value))

class cyan: 

    class lo_band:
        @staticmethod
        def wave_sweep(channels):
            print(sys._getframe().f_code.co_name)

            channels = list(range(4))
            sample_count = int(round(25000000/10000))
            tx_gain = 25
            rx_gain = 25
            center_freq = 10000000      # 10MHz
            sample_rate = 25000000      # 25Msps
            for wave_freq in [ 500000, 600000, 700000, 800000, 900000, 1000000 ]:
                yield locals()

        @staticmethod 
        def quick(channels):
            print(sys._getframe().f_code.co_name)

            channels = list(range(channels))
            wave_freq = 1000000
            sample_count = 10000
            tx_gain = 25
            rx_gain = 25
            center_freq = 15000000
            sample_rate = 10000000
            yield locals()

        @staticmethod
        def basic(channels):
            print(sys._getframe().f_code.co_name)

            channels = list(range(4))
            wave_freq = 1000000
            sample_count = 256
            tx_gain = 25
            rx_gain = 25
            for center_freq in [ 15000000 ]:
                for sample_rate in [ 9803922, 25000000 ]:
                    yield locals()        

        @staticmethod
        def gain_rx(channels):
            print(sys._getframe().f_code.co_name)

            channels = list(range(channels))
            wave_freq = 1000000
            sample_count = 1000
            center_freq = 150000000    # 150MHz
            sample_rate = 9803922
            tx_gain = 10 #increasing the fixed gain may cause saturation
            for rx_gain in [ 5, 10, 20 ]:
                yield locals()

        @staticmethod
        def gain_tx(channels):
            print(sys._getframe().f_code.co_name)

            channels = list(range(channels))
            wave_freq = 1000000
            sample_count = 1000
            center_freq = 150000000    # 150MHz
            sample_rate = 9803922
            rx_gain = 10#increasing the fixed gain may cause saturation
            for tx_gain in [ 5, 10, 20 ]:
                yield locals()

        @staticmethod
        def phaseCoherency(channels):
            print(sys._getframe().f_code.co_name)
            channels = list(range(4))
            sample_count = int(round(25000000/10000))
            tx_gain = 25
            rx_gain = 25
            center_freq = 10000000
            wave_freq = 500000
            for i in range(10):
                yield locals()

        @staticmethod
        def phaseCoherency_short(channels):
            print(sys._getframe().f_code.co_name)
            channels = list(range(4))
            sample_count = int(round(25000000/10000))
            tx_gain = 25
            rx_gain = 25
            center_freq = 10000000
            sample_rate = 25000000
            wave_freq = 500000
            for i in range(2):
                yield locals()


    class mid_band:
        @staticmethod
        def wave_sweep(channels):
            print(sys._getframe().f_code.co_name)

            channels = list(range(4))
            sample_count = int(round(25000000/10000))
            tx_gain = 25
            rx_gain = 25
            center_freq = 1000000000    # 1GHz
            sample_rate = 25000000      # 25Msps
            for wave_freq in [ 500000, 600000, 700000, 800000, 900000, 1000000 ]:
                yield locals()

        @staticmethod
        def basic(channels):
            print(sys._getframe().f_code.co_name)

            channels = list(range(4))
            wave_freq = 1000000
            sample_count = 256
            tx_gain = 25
            rx_gain = 25
            for center_freq in [ 1000000000, 2000000000, 3000000000, 4000000000 ]:
                for sample_rate in [ 9848485, 25000000, 36111111 ]:
                    yield locals()


        @staticmethod
        def wave_easy(channels):
            print(sys._getframe().f_code.co_name)

            channels = list(range(4))
            sample_rate = 9803922
            sample_count = int((round(9803922/1000)))
            #sample_count_tx = 9848485
            #sample_count_rx = int(round(9848485/1000))
            tx_gain = 25
            rx_gain = 25
            center_freq = 1000000000    # 1GHz
            for wave_freq in [ 50000 ]:
                yield locals()

        @staticmethod
        def gain_tx(channels):
            print(sys._getframe().f_code.co_name)

            channels = list(range(channels))
            wave_freq = 1000000
            sample_count = 1000
            center_freq = 2000000000    # 2GHz
            sample_rate = 9803922
            rx_gain = 40#increasing the fixed gain may cause saturation
            for tx_gain in [ 5, 10, 20 ]:
                yield locals()

        @staticmethod
        def gain_rx(channels):
            print(sys._getframe().f_code.co_name)

            channels = list(range(channels))
            #print(channels)
            wave_freq = 1000000
            sample_count = 1000
            center_freq = 2000000000    # 2GHz
            sample_rate = 9803922
            tx_gain = 40#increasing the fixed gain may cause saturation
            for rx_gain in [ 10, 20, 30 ]:
                yield locals()

    
    class hi_band:
        @staticmethod
        def wave_sweep(channels):
            print(sys._getframe().f_code.co_name)

            channels = list(range(4))
            sample_count = int(round(25000000/10000))
            tx_gain = 25
            rx_gain = 25
            center_freq = 15000000000   # 15GHz
            sample_rate = 25000000      # 25Msps
            for wave_freq in [ 500000, 600000, 700000, 800000, 900000, 1000000 ]:
                yield locals()

        @staticmethod
        def wave_easy(channels):
            print(sys._getframe().f_code.co_name)

            channels = list(range(4))
            sample_rate = 9803922
            sample_count = int((round(9803922/1000)))
            #sample_count_tx = 9803922
            #sample_count_rx = int(round(9803922/1000))
            tx_gain = 25
            rx_gain = 25
            center_freq = 15000000000   # 15GHz
            for wave_freq in [ 50000 ]:
                yield locals()

        @staticmethod
        def basic(channels):
            print(sys._getframe().f_code.co_name)

            channels = list(range(4))
            wave_freq = 1000000
            sample_count = 256
            tx_gain = 25
            rx_gain = 25
            for center_freq in [ 11000000000, 12000000000, 13000000000, 14000000000 ]:
                for sample_rate in [ 9803922, 25000000, 36111111 ]:
                    yield locals()


        @staticmethod
        def gain_tx(channels):
            print(sys._getframe().f_code.co_name)

            channels = list(range(channels))
            wave_freq = 1000000
            sample_count = 1000
            center_freq = 15000000000   # 15GHz
            sample_rate = 9803922
            rx_gain = 40#increasing the fixed gain may cause saturation
            for tx_gain in [ 5, 10, 20 ]:
                yield locals()

        @staticmethod
        def gain_rx(channels):
            print(sys._getframe().f_code.co_name)

            channels = list(range(channels))
            #print(channels)
            wave_freq = 1000000
            sample_count = 1000
            center_freq = 15000000000   # 15GHz
            sample_rate = 9803922
            tx_gain = 40#increasing the fixed gain may cause saturation
            for rx_gain in [ 10, 20, 30 ]:
                yield locals()