import inspect
import sys

def hi_band_wave_sweep():

    print(sys._getframe().f_code.co_name)

    channels = list(range(4))
    sample_count = 256
    tx_gain = 25
    rx_gain = 25
    center_freq = 1000000000
    sample_rate = 25000000
    for wave_freq in [ 500000, 600000, 700000, 800000, 900000, 1000000 ]:
        yield locals()

def lo_band_wave_sweep():

    print(sys._getframe().f_code.co_name)

    channels = list(range(4))
    sample_count = 256
    tx_gain = 25
    rx_gain = 25
    center_freq = 10000000
    sample_rate = 25000000
    for wave_freq in [ 500000, 600000, 700000, 800000, 900000, 1000000 ]:
        yield locals()


def lo_band_quick():

    print(sys._getframe().f_code.co_name)

    channels = list(range(4))
    wave_freq = 1000000
    sample_count = 1000
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
        for sample_rate in [ 10000000, 25000000 ]:
            yield locals()


def hi_band_basic():

    print(sys._getframe().f_code.co_name)

    channels = list(range(4))
    wave_freq = 1000000
    sample_count = 256
    tx_gain = 25
    rx_gain = 25
    for center_freq in [ 1000000000, 2000000000, 3000000000, 4000000000 ]:
        for sample_rate in [ 10000000, 25000000, 36111111 ]:
            yield locals()


def lo_band_gain_rx(channels):

    print(sys._getframe().f_code.co_name)

    channels = list(range(channels))
    wave_freq = 1000000
    sample_count = 1000
    center_freq = 15000000
    sample_rate = 9848485
    tx_gain = 25
    for rx_gain in [ 5, 10, 20 ]:
        yield locals()


def lo_band_gain_tx(channels):

    print(sys._getframe().f_code.co_name)

    channels = list(range(channels))
    wave_freq = 1000000
    sample_count = 1000
    center_freq = 15000000
    sample_rate = 9848485
    rx_gain = 25
    for tx_gain in [ 5, 10, 20 ]:
        yield locals()


def hi_band_gain_tx(channels):

    print(sys._getframe().f_code.co_name)

    channels = list(range(channels))
    wave_freq = 1000000
    sample_count = 1000
    center_freq = 2000000000
    sample_rate = 9848485
    rx_gain = 40
    for tx_gain in [ 5, 10, 20 ]:
        yield locals()


def hi_band_gain_rx(channels):

    print(sys._getframe().f_code.co_name)

    channels = list(range(channels))
    wave_freq = 1000000
    sample_count = 1000
    center_freq = 2000000000
    sample_rate = 9848485
    tx_gain = 30
    for rx_gain in [ 5, 10, 20 ]:
        yield locals()


def dump(iteration):

    for key, value in iteration.items():
        print("%20s : %r" % (key, value))

