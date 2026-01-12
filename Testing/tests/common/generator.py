import inspect
import sys
from . import log

def ship_test_crimson(channels):

    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

    channels = list(range(channels))
    wave_freq = 100000
    sample_rate = 9848485
    sample_count = int(sample_rate/ 10)
    # The highest frequency uses a higher gain because the signal begins to roll off as the frequency gets higher
    tx_gains = [25, 25, 25, 25, 25, 25, 25, 30]
    rx_gains = [25, 25, 25, 25, 25, 25, 25, 30]
    center_freqs = [5000000, 300000000, 600000000, 1200000000, 2400000000, 4000000000, 4800000000, 5500000000]
    for tx_gain, rx_gain, center_freq in zip(tx_gains, rx_gains, center_freqs):
        yield locals()

def ship_test_cyan(channels):

    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

    channels = list(range(channels))
    wave_freq = 100000
    sample_rate = 9803922
    sample_count = int(sample_rate/ 10)
    # The highest frequency uses a higher gain because the signal begins to roll off as the frequency gets higher
    rx_gains = [20, 20, 20, 20, 20, 20, 20, 40, 40]
    tx_gains = [20, 20, 20, 20, 20, 20, 20, 30, 30]
    center_freqs = [5000000, 15000000, 200000000, 600000000, 1200000000, 2700000000, 4000000000, 9000000000, 17000000000]
    for tx_gain, rx_gain, center_freq in zip(tx_gains, rx_gains, center_freqs):
        yield locals()

def ship_test_cyanbaseband(channels):

    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

    channels = list(range(channels))
    wave_freq = 100000
    sample_rate = 9803922
    sample_count = int(sample_rate/ 10)
    # The highest frequency uses a higher gain because the signal begins to roll off as the frequency gets higher
    rx_gains = [20, 20, 20, 20, 20, 20, 20, 40, 40]
    tx_gains = [20, 20, 20, 20, 20, 20, 20, 30, 30]
    center_freqs = [5000000, 15000000, 200000000, 600000000, 1200000000, 2700000000, 4000000000]
    for tx_gain, rx_gain, center_freq in zip(tx_gains, rx_gains, center_freqs):
        yield locals()

def ship_test_chestnut(channels):

    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

    channels = list(range(channels))
    wave_freq = 100000
    sample_rate = 9803922
    sample_count = int(sample_rate/ 10)
    # The highest frequency uses a higher gain because the signal begins to roll off as the frequency gets higher
    rx_gains = [25, 25, 30, 40, 40, 40, 50, 50, 50, 50]
    tx_gains = [25, 25, 30, 30, 30, 30, 30, 40, 40, 40]
    center_freqs = [10000000, 200000000, 600000000, 1200000000, 2000000000, 4500000000, 5000000000, 6500000000, 7500000000, 8500000000]
    for tx_gain, rx_gain, center_freq in zip(tx_gains, rx_gains, center_freqs):
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

def lo_band_passband_flatness_test():
    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
    channels = list(range(4))
    sample_count = int(9803922/10000)
    tx_gain = 25
    rx_gain = 25
    center_freq = 15000000
    sample_rate = 9803922
    for wave_freq in list(range(-int(0.45*sample_rate),int(0.45*sample_rate),int(0.9*sample_rate/24))):
        # Only test non-zero wave frequencies
        if wave_freq != 0:
            yield locals()

def lo_band_buffer_exhaust_test():
    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
    channels = list(range(4))
    sample_count = int(9803922/1000 + 74000)
    tx_gain = 25
    rx_gain = 25
    center_freq = 15000000
    sample_rate = 9803922
    for wave_freq in [ 1000000 ]:
        yield locals()

def hi_band_wave_sweep():

    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

    channels = list(range(4))
    sample_count = int(round(25000000/10000))
    tx_gain = 25
    rx_gain = 25
    center_freq = 1000000000
    sample_rate = 25000000
    for wave_freq in [ 600000, 800000, 1000000 ]:
        yield locals()

def hi_band_wave_easy():
    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

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

    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

    channels = list(range(4))
    sample_count = int(round(25000000/10000))
    tx_gain = 25
    rx_gain = 25
    center_freq = 10000000
    sample_rate = 25000000
    for wave_freq in [ 600000, 800000, 1000000 ]:
        yield locals()

def lo_band_quick():

    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

    channels = list(range(channels))
    wave_freq = 1000000
    sample_count = 10000
    tx_gain = 25
    rx_gain = 25
    center_freq = 15000000
    sample_rate = 10000000
    yield locals()


def lo_band_basic():
    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

    wave_freq = 1000000
    sample_count = 256
    tx_gain = 25
    rx_gain = 25
    for center_freq in [ 15000000 ]:
        for sample_rate in [ 9848485, 25000000 ]:
            yield locals()


def hi_band_basic():
    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

    wave_freq = 1000000
    sample_count = 256
    tx_gain = 25
    rx_gain = 25
    for center_freq in [ 1000000000, 2000000000, 3000000000, 4000000000 ]:
        for sample_rate in [ 9848485, 25000000, 36111111 ]:
            yield locals()

def lo_band_gain_rx():

    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

    wave_freq = 1000000
    sample_count = 1000
    center_freq = 15000000
    sample_rate = 9848485
    tx_gain = 10 #increasing the fixed gain may cause saturation
    for rx_gain in [ 5, 10, 20 ]:
        yield locals()


def lo_band_gain_tx():

    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

    wave_freq = 1000000
    sample_count = 1000
    center_freq = 15000000
    sample_rate = 9848485
    rx_gain = 10#increasing the fixed gain may cause saturation
    for tx_gain in [ 5, 10, 20 ]:
        yield locals()


def hi_band_gain_tx():

    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

    wave_freq = 1000000
    sample_count = 1000
    center_freq = 2000000000
    sample_rate = 9848485
    rx_gain = 40#increasing the fixed gain may cause saturation
    for tx_gain in [ 5, 10, 20 ]:
        yield locals()


def hi_band_gain_rx():

    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

    wave_freq = 1000000
    sample_count = 1000
    center_freq = 2000000000
    sample_rate = 4062500
    tx_gain = 40#increasing the fixed gain may cause saturation
    for rx_gain in [ 10, 20, 30 ]:
        yield locals()

def lo_band_phaseCoherency():
    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
    tx_gain = 25
    rx_gain = 25
    sample_rate = 25000000
    center_freq = 0
    wave_freq = 5000000
    sample_count = int(round(sample_rate/1000))
    yield locals()

def tx_trigger():
    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
    center_freq = 0
    sample_rate = 10156250
    tx_gain = 20
    sample_count = 480
    period = 20
    setpoint = 1000
    start_time = 5.25
    num_trigger = 20
    yield locals()

def tx_rx_rate():
    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

    descriptions = ["Max achievable combined rate on all ch"]
    rx_rates = [325e6/6]
    rx_channels = [[0,1,2,3]]
    # TODO: undo this reduction
    # So that the test is stable during stand down tx will be tested at a very low rate
    # After stand down revert the decrease
    # tx_rates = [325e6/6]
    tx_rates = [325e6/32]
    tx_channels = [[0,1,2,3]]
    assert(len(rx_rates) == len(rx_channels))
    assert(len(rx_rates) == len(tx_rates))
    assert(len(rx_rates) == len(tx_channels))
    for n in range(len(rx_rates)):
        iteration_dict = {
            "description" : descriptions[n],
            "rx_rate" : rx_rates[n],
            "rx_channel" : rx_channels[n],
            "tx_rate" : tx_rates[n],
            "tx_channel" : tx_channels[n]
        }
        yield iteration_dict

def rx_rate():
    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

    descriptions = ["Max achievable rx rate on any number of ch", "Max achievable rx rate on all ch"]
    rx_rates = [162.5e6, 81.25e6]
    rx_channels = [[0, 1], [0,1,2,3]]
    assert(len(rx_rates) == len(rx_channels))
    for n in range(len(rx_rates)):
        iteration_dict = {
            "description" : descriptions[n],
            "rx_rate" : rx_rates[n],
            "rx_channel" : rx_channels[n]
        }
        yield iteration_dict

def tx_rate():
    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

    descriptions = ["Max achievable tx rate on any number of ch", "Max achievable tx rate on all ch"]
    # TODO: undo this reduction
    # So that the test is stable during stand down tx will be tested at a very low rate
    # After stand down revert the decrease
    # tx_rates = [162.5e6, 81.25e6]
    tx_rates = [162.5e6/16, 81.25e6/16]
    tx_channels = [[0], [0,1,2,3]]
    assert(len(tx_rates) == len(tx_channels))
    for n in range(len(tx_rates)):
        iteration_dict = {
            "description" : descriptions[n],
            "tx_rate" : tx_rates[n],
            "tx_channel" : tx_channels[n]
        }
        yield iteration_dict

def rx_uhd_tune():
    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
    channels = list(range(4))
    wave_freq = 1000000
    sample_count = 10000
    tx_gain = 25
    rx_gain = 25
    rx_lo = 2250000000
    sample_rate = 9848485
    for center_freq in [ (rx_lo - 2000000), rx_lo, (rx_lo + 2000000) ]: # 3 cases for dsp (pos, zero, neg).
        yield locals()

def tx_uhd_tune():
    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
    channels = list(range(4))
    wave_freq = 1000000
    sample_count = 10000
    tx_gain = 25
    rx_gain = 25
    tx_lo = 2250000000
    sample_rate = 9848485
    for center_freq in [ (tx_lo - 2000000), tx_lo, (tx_lo + 2000000) ]: # 3 cases for dsp (pos, zero, neg).
        yield locals()

def tx_rx_longterm_rate():
    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
    channels = list(range(4))
    sample_rate = 325e6/33          # 9.848485 Msps
    duration = 90                   # 90 sec
    yield locals()

def dump(iteration):
    log.pvpkg_log_info("GENERATOR", "Using configuration:")
    for key, value in iteration.items():
        log.pvpkg_log("%20s : %r" % (key, value))

class cyan:
    class lo_band:
        @staticmethod
        def passband_flatness_test():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            sample_count = int(round(25000000/10000))
            tx_gain = 25
            rx_gain = 25
            center_freq = 100000000
            sample_rate = 9803922
            for wave_freq in list(range(-int(0.45*sample_rate),int(0.45*sample_rate),int(0.9*sample_rate/24))):
                # Only test non-zero wave frequencies
                if wave_freq != 0:
                    yield locals()

        @staticmethod
        def buffer_exhaust_test():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            sample_count = int(round(25000000/10000)+4700000)
            tx_gain = 40
            rx_gain = 40
            center_freq = 10000000      # 10MHz
            sample_rate = 25000000      # 25MSps
            for wave_freq in [ 1000000 ]:
                yield locals()

        @staticmethod
        def wave_sweep():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            sample_count = int(round(25000000/10000))
            tx_gain = 40
            rx_gain = 40
            center_freq = 10000000      # 10MHz
            sample_rate = 25000000      # 25MSps
            for wave_freq in [ 600000, 800000, 1000000 ]:
                yield locals()

        @staticmethod
        def quick(channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            channels = list(range(channels))
            wave_freq = 1000000         # 1MHz
            sample_count = 10000
            tx_gain = 25
            rx_gain = 25
            center_freq = 15000000      # 15MHz
            sample_rate = 10000000      # 10MSps
            yield locals()

        @staticmethod
        def basic():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            wave_freq = 1000000         # 1MHz
            sample_count = 256
            tx_gain = 25
            rx_gain = 25
            for center_freq in [ 15000000 ]:
                for sample_rate in [ 9803922, 25000000 ]:
                    yield locals()

        @staticmethod
        def gain_rx():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            wave_freq = 1000000
            sample_count = 1000
            center_freq = 15000000  # 15MHz
            sample_rate = 10000000  # 10MSps
            tx_gain = 0 #increasing the fixed gain may cause saturation
            for rx_gain in [5, 10, 15]:
                yield locals()

        @staticmethod
        def gain_tx():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            wave_freq = 1000000
            sample_count = 1000
            center_freq = 15000000  # 15MHz
            sample_rate = 10000000  # 10MSps
            rx_gain = 0
            for tx_gain in [0, 10, 20]:
                yield locals()

        @staticmethod
        def phaseCoherency():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            sample_rate = 25000000
            # Use 5000 samples to have a more accurate frequency estimate
            sample_count = int(round(sample_rate/10000*2))
            tx_gain = 30
            rx_gain = 28
            center_freq = 100000000     # 100MHz
            wave_freq = 500000
            yield locals()

        @staticmethod
        def phaseCoherencyAllBands():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            sample_rate = 25000000
            sample_count = int(round(sample_rate/10000))
            tx_gain = 30
            rx_gain = 28
            wave_freq = 500000
            for center_freq in [100000000, 2000000000, 9000000000]: #100MHz, 2GHz, 9GHz
                yield locals()

        @staticmethod
        def tx_trigger():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            center_freq = 0
            sample_rate = 10204082
            tx_gain = 20
            sample_count = 384
            period = 20
            setpoint = 1000
            start_time = 5.25
            # Cyan buffer level requests have a resolution of 128 samples
            # In order to detect an off by 1 issue it must have more that that many samples
            num_trigger = 130
            yield locals()

        @staticmethod
        def tx_rx_rate(channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            descriptions = ["Max achievable combined rate on all ch"]
            # Higher rates are achievable outside of docker
            rx_rates = [100e6]
            rx_channels = [list(range(channels))]
            # TODO: undo this reduction
            # So that the test is stable during stand down tx will be tested at a very low rate
            # After stand down revert the decrease
            # tx_rates = [(500e6)/8]
            tx_rates = [(500e6)/8/5]
            tx_channels = [list(range(channels))]
            assert(len(rx_rates) == len(rx_channels))
            assert(len(rx_rates) == len(tx_rates))
            assert(len(rx_rates) == len(tx_channels))
            for n in range(len(rx_rates)):
                iteration_dict = {
                    "description" : descriptions[n],
                    "rx_rate" : rx_rates[n],
                    "rx_channel" : rx_channels[n],
                    "tx_rate" : tx_rates[n],
                    "tx_channel" : tx_channels[n]
                }
                yield iteration_dict

        @staticmethod
        def rx_rate(channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            descriptions = ["Max achievable rx rate on any number of ch", "Max achievable rx rate on all ch"]
            # Higher rates are achievable outside of docker
            rx_rates = [250e6, 125e6]
            rx_channels = [[0], list(range(channels))]
            assert(len(rx_rates) == len(rx_channels))
            for n in range(len(rx_rates)):
                iteration_dict = {
                    "description" : descriptions[n],
                    "rx_rate" : rx_rates[n],
                    "rx_channel" : rx_channels[n]
                }
                yield iteration_dict

        @staticmethod
        def tx_rate(channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            descriptions = ["Max achievable tx rate on any number of ch", "Max achievable tx rate on all ch"]
            # Higher rates are achievable outside of docker
            # TODO: undo this reduction
            # So that the test is stable during stand down tx will be tested at a very low rate
            # After stand down revert the decrease
            # tx_rates = [250e6, (500e6)/8]
            tx_rates = [250e6/25, (500e6)/8/5]
            tx_channels = [[0], list(range(channels))]
            assert(len(tx_rates) == len(tx_channels))
            for n in range(len(tx_rates)):
                iteration_dict = {
                    "description" : descriptions[n],
                    "tx_rate" : tx_rates[n],
                    "tx_channel" : tx_channels[n]
                }
                yield iteration_dict

    class mid_band:
        @staticmethod
        def wave_sweep():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            sample_count = int(round(25000000/10000))
            tx_gain = 40
            rx_gain = 40
            center_freq = 1000000000    # 1GHz
            sample_rate = 25000000      # 25Msps
            for wave_freq in [ 600000, 800000, 1000000 ]:
                yield locals()

        @staticmethod
        def basic():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            wave_freq = 1000000         # 1MHz
            sample_count = 256
            tx_gain = 35
            rx_gain = 35
            for center_freq in [ 2000000000, 4000000000 ]:
                for sample_rate in [ 9803922, 25000000, 35714286 ]:
                    yield locals()


        @staticmethod
        def wave_easy(channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            channels = list(range(4))
            sample_rate = 10000000      # 10MSps
            sample_count = int((round(9803922/1000)))
            #sample_count_tx = 9803922
            #sample_count_rx = int(round(9803922/1000))
            tx_gain = 25
            rx_gain = 25
            center_freq = 1000000000    # 1GHz
            for wave_freq in [ 50000 ]:
                yield locals()

        @staticmethod
        def gain_tx():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            wave_freq = 1000000
            sample_count = 1000
            center_freq = 2700000000    # 2.7GHz
            sample_rate = 10000000      # 10MSps
            rx_gain = 20#increasing the fixed gain may cause saturation
            for tx_gain in [0, 15, 30]:
                yield locals()

        @staticmethod
        def gain_rx():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            wave_freq = 1000000
            sample_count = 1000
            center_freq = 2700000000    # 2.7Hz
            sample_rate = 10000000      # 10MSps
            tx_gain = 20#increasing the fixed gain may cause saturation
            for rx_gain in [0, 15, 30]:
                yield locals()

        @staticmethod
        def rx_uhd_tune():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            wave_freq = 1000000
            sample_count = 10000
            tx_gain = 0
            rx_gain = 0
            rx_lo = 2300000000 #LO Frequency should be multiple of 100MHz for cyan/chestnut
            sample_rate = 10000000
            for center_freq in [ (rx_lo - 2000000), rx_lo, (rx_lo + 2000000) ]: # 3 cases for dsp nco (pos, zero, neg).
                yield locals()

        @staticmethod
        def tx_uhd_tune():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            wave_freq = 1000000
            sample_count = 10000
            # Using to low a gain will result in the lo feedthrough not being visible next to the main tone
            # Using to high a gain will result in either the lo feedthrough or main tone not being visible
            tx_gain = 0
            rx_gain = 0
            tx_lo = 2300000000 #LO Frequency should be multiple of 100MHz for cyan/chestnut
            sample_rate = 10000000
            for center_freq in [ (tx_lo - 2000000), tx_lo, (tx_lo + 2000000) ]: # 3 cases for dsp nco (pos, zero, neg).
                yield locals()

    class hi_band:
        @staticmethod
        def wave_sweep():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            sample_count = int(round(25000000/10000))
            tx_gain = 50
            rx_gain = 50
            center_freq = 15000000000   # 15GHz
            sample_rate = 25000000      # 25Msps
            for wave_freq in [ 600000, 800000, 1000000 ]:
                yield locals()

        @staticmethod
        def wave_easy(channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

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
        def basic():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            wave_freq = 1000000
            sample_count = 256
            tx_gain = 50
            rx_gain = 50
            for center_freq in [ 12000000000, 14000000000 ]:
                for sample_rate in [ 9803922, 25000000, 35714286 ]:
                    yield locals()


        @staticmethod
        def gain_tx():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            wave_freq = 1000000
            sample_count = 1000
            center_freq = 9000000000    # 9GHz
            sample_rate = 10000000      # 10MSps
            rx_gain = 60#increasing the fixed gain may cause saturation
            for tx_gain in [0, 15, 30]:
                yield locals()

        @staticmethod
        def gain_rx():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            wave_freq = 1000000
            sample_count = 1000
            center_freq = 9000000000    # 9GHz
            sample_rate = 10000000      # 10MSps
            tx_gain = 30#increasing the fixed gain may cause saturation
            for rx_gain in [0, 30, 60]:
                yield locals()

class chestnut:
    class lo_band:
        @staticmethod
        def passband_flatness_test():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            sample_count = int(round(25000000/10000))
            tx_gain = 25
            rx_gain = 25
            center_freq = 100000000
            sample_rate = 9803922
            for wave_freq in list(range(-int(0.45*sample_rate),int(0.45*sample_rate),int(0.9*sample_rate/24))):
                # Only test non-zero wave frequencies
                if wave_freq != 0:
                    yield locals()

        @staticmethod
        def buffer_exhaust_test():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            sample_count = int(round(25000000/10000)+4700000)
            tx_gain = 40
            rx_gain = 40
            center_freq = 10000000      # 10MHz
            sample_rate = 14705882      # 25MSps
            for wave_freq in [ 1000000 ]:
                yield locals()

        @staticmethod
        def wave_sweep():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            sample_count = int(round(25000000/10000))
            tx_gain = 40
            rx_gain = 40
            center_freq = 10000000      # 10MHz
            sample_rate = 14705882
            for wave_freq in [ 600000, 800000, 1000000 ]:
                yield locals()

        @staticmethod
        def quick(channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            channels = list(range(channels))
            wave_freq = 1000000         # 1MHz
            sample_count = 10000
            tx_gain = 25
            rx_gain = 25
            center_freq = 14705882
            sample_rate = 10000000      # 10MSps
            yield locals()

        @staticmethod
        def basic():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            wave_freq = 1000000         # 1MHz
            sample_count = 256
            tx_gain = 25
            rx_gain = 25
            for center_freq in [ 15000000 ]:
                for sample_rate in [ 9803922, 25000000 ]:
                    yield locals()

        @staticmethod
        def gain_rx():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            wave_freq = 1000000
            sample_count = 1000
            center_freq = 15000000  # 15MHz
            sample_rate = 10000000  # 10MSps
            tx_gain = 30 #increasing the fixed gain may cause saturation
            for rx_gain in [0, 15, 30]:
                yield locals()

        @staticmethod
        def gain_tx():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            wave_freq = 1000000
            sample_count = 1000
            center_freq = 15000000  # 15MHz
            sample_rate = 10000000  # 10MSps
            rx_gain = 30#increasing the fixed gain may cause saturation
            for tx_gain in [ 0, 15, 30 ]:
                yield locals()

        @staticmethod
        def phaseCoherency():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            sample_rate = 25000000
            # Use 5000 samples to have a more accurate frequency estimate
            sample_count = int(round(sample_rate/10000*2))
            tx_gain = 30
            rx_gain = 30
            center_freq = 100000000     # 100MHz
            sample_rate = 25000000
            wave_freq = 500000
            yield locals()

        @staticmethod
        def tx_trigger():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            center_freq = 0
            sample_rate = 10204082
            tx_gain = 20
            sample_count = 384
            period = 20
            setpoint = 1000
            start_time = 5.25
            # Cyan buffer level requests have a resolution of 128 samples
            # In order to detect an off by 1 issue it must have more that that many samples
            num_trigger = 130
            yield locals()

        @staticmethod
        def tx_rx_rate(channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            descriptions = ["Max achievable combined rate on all ch"]
            # Higher rates are achievable outside of docker
            rx_rates = [100e6]
            rx_channels = [list(range(channels))]
            # TODO: undo this reduction
            # So that the test is stable during stand down tx will be tested at a very low rate
            # After stand down revert the decrease
            # tx_rates = [(500e6)/8]
            tx_rates = [(500e6)/8/5]
            tx_channels = [list(range(channels))]
            assert(len(rx_rates) == len(rx_channels))
            assert(len(rx_rates) == len(tx_rates))
            assert(len(rx_rates) == len(tx_channels))
            for n in range(len(rx_rates)):
                iteration_dict = {
                    "description" : descriptions[n],
                    "rx_rate" : rx_rates[n],
                    "rx_channel" : rx_channels[n],
                    "tx_rate" : tx_rates[n],
                    "tx_channel" : tx_channels[n]
                }
                yield iteration_dict

        @staticmethod
        def rx_rate(channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            descriptions = ["Max achievable rx rate on any number of ch", "Max achievable rx rate on all ch"]
            # Higher rates are achievable outside of docker
            rx_rates = [250e6, 125e6]
            rx_channels = [[0], list(range(channels))]
            assert(len(rx_rates) == len(rx_channels))
            for n in range(len(rx_rates)):
                iteration_dict = {
                    "description" : descriptions[n],
                    "rx_rate" : rx_rates[n],
                    "rx_channel" : rx_channels[n]
                }
                yield iteration_dict

        @staticmethod
        def tx_rate(channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            descriptions = ["Max achievable tx rate on any number of ch", "Max achievable tx rate on all ch"]
            # Higher rates are achievable outside of docker
            # TODO: undo this reduction
            # So that the test is stable during stand down tx will be tested at a very low rate
            # After stand down revert the decrease
            # tx_rates = [250e6, (500e6)/8]
            tx_rates = [250e6/25, (500e6)/8/5]
            tx_channels = [[0], list(range(channels))]
            assert(len(tx_rates) == len(tx_channels))
            for n in range(len(tx_rates)):
                iteration_dict = {
                    "description" : descriptions[n],
                    "tx_rate" : tx_rates[n],
                    "tx_channel" : tx_channels[n]
                }
                yield iteration_dict

    class mid_band:
        @staticmethod
        def wave_sweep():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            sample_count = int(round(25000000/10000))
            tx_gain = 40
            rx_gain = 40
            center_freq = 1000000000    # 1GHz
            sample_rate = 14705882
            for wave_freq in [ 600000, 800000, 1000000 ]:
                yield locals()

        @staticmethod
        def basic():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            wave_freq = 1000000         # 1MHz
            sample_count = 256
            tx_gain = 35
            rx_gain = 35
            for center_freq in [ 2000000000, 4000000000 ]:
                for sample_rate in [ 9803922, 25000000, 35714286 ]:
                    yield locals()


        @staticmethod
        def wave_easy(channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            channels = list(range(4))
            sample_rate = 10000000      # 10MSps
            sample_count = int((round(9803922/1000)))
            #sample_count_tx = 9803922
            #sample_count_rx = int(round(9803922/1000))
            tx_gain = 25
            rx_gain = 25
            center_freq = 1000000000    # 1GHz
            for wave_freq in [ 50000 ]:
                yield locals()

        @staticmethod
        def gain_tx():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            wave_freq = 1000000
            sample_count = 1000
            center_freq = 2700000000    # 2.7GHz
            sample_rate = 10000000      # 10MSps
            rx_gain = 45#increasing the fixed gain may cause saturation
            for tx_gain in [0, 15, 30]:
                yield locals()

        @staticmethod
        def gain_rx():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            wave_freq = 1000000
            sample_count = 1000
            center_freq = 2700000000    # 2.7Hz
            sample_rate = 10000000      # 10MSps
            tx_gain = 30#increasing the fixed gain may cause saturation
            for rx_gain in [0, 30, 60]:
                yield locals()

        @staticmethod
        def rx_uhd_tune():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            wave_freq = 1000000
            sample_count = 10000
            tx_gain = 15
            rx_gain = 15
            rx_lo = 2300000000 #LO Frequency should be multiple of 100MHz for cyan/chestnut
            sample_rate = 10000000
            for center_freq in [ (rx_lo - 2000000), rx_lo, (rx_lo + 2000000) ]: # 3 cases for dsp nco (pos, zero, neg).
                yield locals()

        @staticmethod
        def tx_uhd_tune():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            wave_freq = 1000000
            sample_count = 10000
            # Using to low a gain will result in the lo feedthrough not being visible next to the main tone
            # Using to high a gain will result in either the lo feedthrough or main tone not being visible
            tx_gain = 15
            rx_gain = 15
            tx_lo = 2300000000 #LO Frequency should be multiple of 100MHz for cyan/chestnut
            sample_rate = 10000000
            for center_freq in [ (tx_lo - 2000000), tx_lo, (tx_lo + 2000000) ]: # 3 cases for dsp nco (pos, zero, neg).
                yield locals()

    class hi_band:
        @staticmethod
        def wave_sweep():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            sample_count = int(round(25000000/10000))
            tx_gain = 50
            rx_gain = 60
            center_freq = 7000000000   # 7GHz
            sample_rate = 14705882
            for wave_freq in [ 600000, 800000, 1000000 ]:
                yield locals()

        @staticmethod
        def wave_easy(channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            channels = list(range(4))
            sample_rate = 9803922
            sample_count = int((round(9803922/1000)))
            #sample_count_tx = 9803922
            #sample_count_rx = int(round(9803922/1000))
            tx_gain = 50
            rx_gain = 60
            center_freq = 7000000000   # 7GHz
            for wave_freq in [ 50000 ]:
                yield locals()

        @staticmethod
        def basic():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            wave_freq = 1000000
            sample_count = 256
            tx_gain = 50
            rx_gain = 60
            for center_freq in [ 6500000000, 8500000000 ]:
                for sample_rate in [ 9803922, 25000000, 35714286 ]:
                    yield locals()


        @staticmethod
        def gain_tx():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            wave_freq = 1000000
            sample_count = 1000
            center_freq = 7000000000    # 7GHz
            sample_rate = 10000000      # 10MSps
            rx_gain = 75#increasing the fixed gain may cause saturation
            for tx_gain in [0, 15, 30]:
                yield locals()

        @staticmethod
        def gain_rx():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            wave_freq = 1000000
            sample_count = 1000
            center_freq = 7000000000    # 7GHz
            sample_rate = 10000000      # 10MSps
            tx_gain = 30#increasing the fixed gain may cause saturation
            for rx_gain in [45, 60, 75]:
                yield locals()
