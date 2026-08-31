import sys
from . import log
import re

def ship_test_crimson(channels):

    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

    channels = list(range(channels))
    wave_freq = 100000
    sample_rate = 9848485
    sample_count = int(sample_rate/ 10)
    # The highest frequency uses a higher gain because the signal begins to roll off as the frequency gets higher
    tx_gains = [0, 25, 25, 25, 25, 25, 25, 32]
    rx_gains = [25, 25, 25, 25, 25, 25, 25, 28]
    center_freqs = [5000000, 300000000, 600000000, 1200000000, 2400000000, 4000000000, 4800000000, 5500000000]
    for tx_gain, rx_gain, center_freq in zip(tx_gains, rx_gains, center_freqs):
        yield locals()

def ship_test_calamine(channels):

    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

    channels = list(range(channels))
    wave_freq = 100000
    sample_rate = 9848485
    sample_count = int(sample_rate/ 10)
    # The highest frequency uses a higher gain because the signal begins to roll off as the frequency gets higher
    tx_gains = [0, 25, 25, 25, 25, 30, 25, 30]
    rx_gains = [0, 25, 25, 25, 25, 30, 25, 30]
    center_freqs = [600000000, 2400000000, 4000000000, 9000000000, 17000000000, 24000000000, 35000000000]
    for tx_gain, rx_gain, center_freq in zip(tx_gains, rx_gains, center_freqs):
        yield locals()

def ship_test_cyan(channels):

    log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

    channels = list(range(channels))
    wave_freq = 100000
    sample_rate = 9803922
    sample_count = int(sample_rate/ 10)
    # The highest frequency uses a higher gain because the signal begins to roll off as the frequency gets higher
    rx_gains = [15, 15, 5, 20, 30, 30, 40, 50, 40]
    tx_gains = [15, 5, 10, 10, 5, 20, 20, 30, 30]
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

import os

_uhd_output = None
_crimson_output = None

def get_uhd_output(addr=None):
    global _uhd_output
    if _uhd_output is None:
        args_flag = f'--args="addr={addr}"' if addr else ""
        stream = os.popen(f'uhd_find_devices {args_flag}')
        _uhd_output = stream.read()
    return _uhd_output

def get_crimson_output(addr=None):
    global _crimson_output
    if _crimson_output is None:
        args_flag = f'--args="addr={addr}"' if addr else ""
        stream = os.popen(f'uhd_usrp_info {args_flag} -v')
        _crimson_output = stream.read()
    return _crimson_output

def dump(iteration):
    log.pvpkg_log_info("GENERATOR", "Using configuration:")
    for key, value in iteration.items():
        if key != "self":
            log.pvpkg_log("%20s : %r" % (key, value))

# Since Crimson supports multiple system sample rates, detect and store the system rate to be used for calculating appropriate values for tests.
class crimson_properties:
    def __init__(self):
        # Need to support Crimson tests for 300msps and 325msps
        valid_system_rates = [300e6, 325e6]
        # The unit sample rate. Used to calculate appropriate values for both 300msps and 325msps tests.
        system_rate = None

        rate_match = re.search(r"System sample rate: ([0-9]+)", get_crimson_output())
        if rate_match:
            system_rate = int(rate_match.group(1))

        # Default to 325msps if any unexpected value was returned
        if system_rate not in valid_system_rates:
            log.pvpkg_log_warning("GENERATOR",
                "Detected system sample rate of '{}' which does not match any of the supported rates: {}\nTests will run for 325MSps instead."
                    .format(system_rate, valid_system_rates))
            system_rate = 325e6
        
        self.system_rate = system_rate

class crimson:
    class lo_band(crimson_properties):
        # Confirm the passband is flat by comparing amplitudes of peaks across passband frequencies
        def passband_flatness_test(self):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            sample_rate = int(self.system_rate / 33)
            sample_count = int(sample_rate / 10e3)
            tx_gain = 25
            rx_gain = 25
            center_freq = 15e6
            # Crimson passband is ~90% of the sample rate, so test frequencies within that range (-45% to 45%)
            for wave_freq in list(range(-int(0.45*sample_rate),int(0.45*sample_rate+1),int(0.9*sample_rate/24))):
                # Only test non-zero wave frequencies
                if wave_freq != 0:
                    yield locals()

        # Confirm expected frequency but transmit more samples than the size of the tx buffer
        def buffer_exhaust_test(self):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            # The amount of samples to send to exhaust the tx buffer before starting rx
            buffer_shift = 74000
            sample_rate = int(self.system_rate / 33)
            sample_count = int(sample_rate/1000 + buffer_shift)
            tx_gain = 25
            rx_gain = 25
            center_freq = 15e6
            wave_freq = 1e6
            yield locals()

        # Used for fundamental frequency test
        def wave_sweep(self):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            sample_rate = 25e6
            sample_count = int(round(sample_rate/10e3))
            tx_gain = 25
            rx_gain = 25
            center_freq = 10e6
            for wave_freq in [ 600e3, 800e3, 1e6 ]:
                yield locals()

        def quick(self, channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(channels))
            sample_rate = 10e6
            sample_count = 10e3
            tx_gain = 25
            rx_gain = 25
            center_freq = 15e6
            wave_freq = 1e6
            yield locals()

        # Used for stacked commands test
        def basic(self):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            sample_count = 256
            tx_gain = 25
            rx_gain = 25
            wave_freq = 1e6
            for center_freq in [ 15e6 ]:
                for sample_rate in [ int(self.system_rate / 33), 25e6 ]:
                    yield locals()

        # Test increase in tx gain with everything else fixed
        def gain_tx(self):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            sample_rate = int(self.system_rate / 33)
            sample_count = 1000
            center_freq = 15e6
            wave_freq = 1e6
            rx_gain = 10 # increasing the fixed gain may cause saturation
            for tx_gain in [ 5, 10, 20 ]:
                yield locals()

        # Test increase in rx gain with everything else fixed
        def gain_rx(self):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            sample_rate = int(self.system_rate / 33)
            sample_count = 1000
            center_freq = 15e6
            wave_freq = 1e6
            tx_gain = 10 # increasing the fixed gain may cause saturation
            for rx_gain in [ 5, 10, 20 ]:
                yield locals()

        def phaseCoherency(self):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            sample_rate = 25e6
            sample_count = int(sample_rate/1000)
            tx_gain = 25
            rx_gain = 25
            center_freq = 10e6
            wave_freq = 500e3
            yield locals()

        def tx_trigger(self):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            # Data was generated for SR=10156250, so use closest SR possible that's >= 10156250
            if self.system_rate == 300e6:
                sample_rate = 10344828
            else:
                sample_rate = 10156250
            sample_count = 480
            tx_gain = 20
            center_freq = 0
            period = 20
            setpoint = 1000
            num_trigger = 20
            start_time = 5.25
            yield locals()

        def tx_rx_rate(self, channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            descriptions = ["Max achievable combined rate on all ch"]
            # Higher rates are achievable outside of docker
            rx_rates = [int(self.system_rate / 6)]
            rx_channels = [list(range(channels))]
            tx_rates = [int(self.system_rate / 6)]
            tx_channels = [list(range(channels))]
            assert(len(rx_rates) == len(rx_channels))
            assert(len(rx_rates) == len(tx_rates))
            assert(len(rx_rates) == len(tx_channels))
            for n in range(len(rx_rates)):
                iteration_dict = {
                    "description" : descriptions[n],
                    "rx_rate" : rx_rates[n],
                    "rx_channels" : rx_channels[n],
                    "tx_rate" : tx_rates[n],
                    "tx_channels" : tx_channels[n]
                }
                yield iteration_dict

        def tx_rate(self, channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            descriptions = ["Max achievable tx rate on any number of ch", "Max achievable tx rate on all ch"]
            tx_rates = [int(self.system_rate / 2), int(self.system_rate / 4)]
            tx_channels = [[0], list(range(channels))]
            assert(len(tx_rates) == len(tx_channels))
            for n in range(len(tx_rates)):
                iteration_dict = {
                    "description" : descriptions[n],
                    "tx_rate" : tx_rates[n],
                    "tx_channels" : tx_channels[n]
                }
                yield iteration_dict

        def rx_rate(self, channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            descriptions = ["Max achievable rx rate on any number of ch", "Max achievable rx rate on all ch"]
            # Higher rates are achievable outside of docker
            rx_rates = [int(self.system_rate / 2), int(self.system_rate / 4)]
            rx_channels = [[0, 1], list(range(channels))]
            assert(len(rx_rates) == len(rx_channels))
            for n in range(len(rx_rates)):
                iteration_dict = {
                    "description" : descriptions[n],
                    "rx_rate" : rx_rates[n],
                    "rx_channels" : rx_channels[n]
                }
                yield iteration_dict

        def tx_rx_longterm_rate(self):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            sample_rate = int(self.system_rate / 33)
            duration = 90
            yield locals()

    class hi_band(crimson_properties):
        # Used for fundamental frequency test
        def wave_sweep(self):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            sample_rate = 25e6
            sample_count = int(round(sample_rate / 10e3))
            tx_gain = 25
            rx_gain = 25
            center_freq = 1e9
            for wave_freq in [ 600e3, 800e3, 1e6 ]:
                yield locals()

        def wave_easy(self):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            sample_rate = int(self.system_rate / 33)
            sample_count = int((round(sample_rate / 1000)))
            tx_gain = 25
            rx_gain = 25
            center_freq = 1e9
            for wave_freq in [ 50e3 ]:
                yield locals()

        # Used for stacked commands test
        def basic(self):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            sample_count = 256
            tx_gain = 25
            rx_gain = 25
            wave_freq = 1e6
            for center_freq in [ 1e9, 2e9, 3e9, 4e9 ]:
                for sample_rate in [ int(self.system_rate / 33), 25e6, int(self.system_rate / 9) ]:
                    yield locals()

        # Test increase in tx gain with everything else fixed
        def gain_tx(self):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            sample_rate = int(self.system_rate / 33)
            sample_count = 1000
            center_freq = 2e9
            wave_freq = 1e6
            rx_gain = 40 # increasing the fixed gain may cause saturation
            for tx_gain in [ 5, 10, 20 ]:
                yield locals()

        # Test increase in rx gain with everything else fixed
        def gain_rx(self):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            sample_rate = int(self.system_rate / 33)
            sample_count = 1000
            center_freq = 2e9
            wave_freq = 1e6
            tx_gain = 40 # increasing the fixed gain may cause saturation
            for rx_gain in [ 10, 20, 30 ]:
                yield locals()

        # Test manual tuning through UHD
        def tx_uhd_tune(self):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            sample_rate = int(self.system_rate / 33)
            sample_count = 10e3
            tx_gain = 25
            rx_gain = 25
            wave_freq = 1e6
            tx_lo = 2.25e9
            for center_freq in [ (tx_lo - 2e6), tx_lo, (tx_lo + 2e6) ]: # 3 cases for dsp (pos, zero, neg).
                yield locals()

        def rx_uhd_tune(self):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            sample_rate = int(self.system_rate / 33)
            sample_count = 10e3
            tx_gain = 25
            rx_gain = 25
            wave_freq = 1e6
            rx_lo = 2.25e9
            for center_freq in [ (rx_lo - 2e6), rx_lo, (rx_lo + 2e6) ]: # 3 cases for dsp (pos, zero, neg).
                yield locals()

class calamine:
    class lo_band: # 0-6GHz is lowband
        @staticmethod
        def passband_flatness_test():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            sample_count = int(round(25000000/10000))
            tx_gain = 10
            rx_gain = 10
            center_freq = 15000000      # 15MHz
            sample_rate = 10000000      # 10MSps
            for wave_freq in list(range(-int(0.45*sample_rate),int(0.45*sample_rate+1),int(0.9*sample_rate/24))):
                # Only test non-zero wave frequencies
                if wave_freq != 0:
                    yield locals()

        @staticmethod
        def buffer_exhaust_test():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            sample_count = int(round(25000000/10000)+74000)
            tx_gain = 10
            rx_gain = 10
            center_freq = 15000000          # 15MHz
            sample_rate = 10000000          # 10MSps
            for wave_freq in [ 1000000 ]:   # 1MHz
                yield locals()

        @staticmethod
        def wave_sweep():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            tx_gain = 25
            rx_gain = 25
            center_freq = 1000000000    # 1GHz
            sample_rate = 25000000      # 25MSps
            sample_count = int(round(sample_rate/10000))
            for wave_freq in [ 600000, 800000, 1000000 ]:   # 600kHz, 800kHz, 1MHz
                yield locals()

        @staticmethod
        def quick(channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(channels))
            wave_freq = 1000000         # 1MHz
            sample_count = 10000
            tx_gain = 0
            rx_gain = 0
            center_freq = 15000000      # 15MHz
            sample_rate = 10000000      # 10MSps
            yield locals()

        @staticmethod
        def basic():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            wave_freq = 1000000     # 1MHz
            sample_count = 256
            tx_gain = 25
            rx_gain = 25
            for center_freq in [ 2000000000, 4000000000 ]:              # 2GHz, 4GHz
                for sample_rate in [ 10000000, 25000000, 37500000 ]:    # 10MSps, 25MSps, 37.5MSps
                    yield locals()

        @staticmethod
        def gain_tx():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            wave_freq = 1000000         # 1MHz
            sample_count = 1000
            center_freq = 2000000000    # 2GHz
            sample_rate = 10000000      # 10MSps
            rx_gain = 20                #increasing the fixed gain may cause saturation
            for tx_gain in [0, 15, 30]:
                yield locals()

        @staticmethod
        def gain_rx():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            wave_freq = 1000000         # 1MHz
            sample_count = 1000
            center_freq = 2000000000    # 2GHz
            sample_rate = 10000000      # 10MSps
            tx_gain = 20                #increasing the fixed gain may cause saturation
            for rx_gain in [0, 15, 30]:
                yield locals()

        @staticmethod
        def phaseCoherency():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            sample_rate = 25000000      # 25MSps  
            sample_count = int(round(sample_rate/1000))
            tx_gain = 5
            rx_gain = 5
            center_freq = 10000000      # 10MHz
            wave_freq = 500000          # 500kHz
            yield locals()

        @staticmethod
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

        @staticmethod
        def tx_rx_rate(channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            descriptions = ["Max achievable combined rate on all ch"]
            # Higher rates are achievable outside of docker
            rx_rates = [300e6/6]
            rx_channels = [list(range(channels))]
            tx_rates = [300e6/6]
            tx_channels = [list(range(channels))]
            assert(len(rx_rates) == len(rx_channels))
            assert(len(rx_rates) == len(tx_rates))
            assert(len(rx_rates) == len(tx_channels))
            for n in range(len(rx_rates)):
                iteration_dict = {
                    "description" : descriptions[n],
                    "rx_rate" : rx_rates[n],
                    "rx_channels" : rx_channels[n],
                    "tx_rate" : tx_rates[n],
                    "tx_channels" : tx_channels[n]
                }
                yield iteration_dict

        @staticmethod
        def rx_rate(channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            descriptions = ["Max achievable rx rate on any number of ch", "Max achievable rx rate on all ch"]
            # Higher rates are achievable outside of docker
            rx_rates = [150e6, 75e6]
            rx_channels = [[0, 1], list(range(channels))]
            assert(len(rx_rates) == len(rx_channels))
            for n in range(len(rx_rates)):
                iteration_dict = {
                    "description" : descriptions[n],
                    "rx_rate" : rx_rates[n],
                    "rx_channels" : rx_channels[n]
                }
                yield iteration_dict

        @staticmethod
        def tx_rate(channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            descriptions = ["Max achievable tx rate on any number of ch", "Max achievable tx rate on all ch"]
            tx_rates = [150e6, 75e6]
            tx_channels = [[0], list(range(channels))]
            assert(len(tx_rates) == len(tx_channels))
            for n in range(len(tx_rates)):
                iteration_dict = {
                    "description" : descriptions[n],
                    "tx_rate" : tx_rates[n],
                    "tx_channels" : tx_channels[n]
                }
                yield iteration_dict

        @staticmethod
        def tx_rx_longterm_rate():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            sample_rate = int(300e6 / 33)
            duration = 90
            yield locals()

    class mid_band: # 6GHz-20GHz is midband
        @staticmethod
        def wave_sweep():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            tx_gain = 25
            rx_gain = 25
            center_freq = 10000000000   # 10GHz
            sample_rate = 25000000      # 25Msps
            sample_count = int(round(sample_rate/10000))
            for wave_freq in [ 600000, 800000, 1000000 ]:   # 600kHz, 800kHz, 1MHz
                yield locals()

        @staticmethod
        def wave_easy(channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            sample_rate = 10000000          # 10MSps
            sample_count = int((round(sample_rate/1000)))
            tx_gain = 25
            rx_gain = 25
            center_freq = 15000000000       # 15GHz
            for wave_freq in [ 50000 ]:     # 5kHz
                yield locals()

        @staticmethod
        def basic():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            wave_freq = 1000000          # 1MHz
            sample_count = 256
            tx_gain = 25
            rx_gain = 25
            for center_freq in [ 8e9, 12e9, 16e9 ]:                     # 8GHz, 12GHz, 16GHz
                for sample_rate in [ 10000000, 25000000, 37500000 ]:    # 10MSps, 25MSps, 37.5MSps
                    yield locals()

        @staticmethod
        def gain_tx():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            wave_freq = 1000000         # 1MHz
            sample_count = 1000
            center_freq = 9000000000    # 9GHz
            sample_rate = 10000000      # 10MSps
            rx_gain = 25                #increasing the fixed gain may cause saturation
            for tx_gain in [0, 15, 30]:
                yield locals()

        @staticmethod
        def gain_rx():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            wave_freq = 1000000         # 1MHz
            sample_count = 1000
            center_freq = 9000000000    # 9GHz
            sample_rate = 10000000      # 10MSps
            tx_gain = 25                #increasing the fixed gain may cause saturation
            for rx_gain in [0, 15, 30]:
                yield locals()

        @staticmethod
        def rx_uhd_tune():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            wave_freq = 1000000         # 1MHz
            sample_count = 10000
            tx_gain = 0
            rx_gain = 0
            rx_lo = 8250000000          # 8.25GHz
            sample_rate = 10000000      # 10MSps
            for center_freq in [ (rx_lo - 2000000), rx_lo, (rx_lo + 2000000) ]: # 3 cases for dsp (pos, zero, neg).
                yield locals()

        @staticmethod
        def tx_uhd_tune():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            wave_freq = 1000000         # 1MHz
            sample_count = 10000
            # Using too low a gain will result in the lo feedthrough not being visible next to the main tone
            # Using too high a gain will result in either the lo feedthrough or main tone not being visible
            tx_gain = 0
            rx_gain = 0
            tx_lo = 8250000000          # 8.25GHz
            sample_rate = 10000000      # 10MSps
            for center_freq in [ (tx_lo - 2000000), tx_lo, (tx_lo + 2000000) ]: # 3 cases for dsp nco (pos, zero, neg).
                yield locals()

    class hi_band: # 20GHz-40GHz is highband
        @staticmethod
        def wave_sweep():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            sample_count = int(round(25000000/10000))
            tx_gain = 25
            rx_gain = 25
            center_freq = 35000000000   # 35GHz
            sample_rate = 25000000      # 25Msps
            for wave_freq in [ 600000, 800000, 1000000 ]:   # 600kHz, 800kHz, 1MHz
                yield locals()

        @staticmethod
        def wave_easy(channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            sample_rate = 10000000      # 10MHz
            sample_count = int((round(sample_rate/1000)))
            tx_gain = 25
            rx_gain = 25
            center_freq = 35000000000   # 35GHz
            for wave_freq in [ 50000 ]: # 50kHz
                yield locals()

        @staticmethod
        def basic():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            wave_freq = 1000000     # 1MHz
            sample_count = 256
            tx_gain = 25
            rx_gain = 25
            for center_freq in [ 24e9, 35e9 ]:  # 24GHz, 35GHz
                for sample_rate in [ 10000000, 25000000, 37500000 ]: # 10MSps, 25MSps, 37.5MSps
                    yield locals()

        @staticmethod
        def gain_tx():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            wave_freq = 1000000         # 1MHz
            sample_count = 1000
            center_freq = 30000000000   # 30GHz
            sample_rate = 10000000      # 10MSps
            rx_gain = 25                #increasing the fixed gain may cause saturation
            for tx_gain in [0, 10, 20]:
                yield locals()

        @staticmethod
        def gain_rx():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            wave_freq = 1000000         # 1MHz
            sample_count = 1000
            center_freq = 30000000000   # 30GHz
            sample_rate = 10000000      # 10MSps
            tx_gain = 25                #increasing the fixed gain may cause saturation
            for rx_gain in [0, 15, 30]:
                yield locals()

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
            for wave_freq in list(range(-int(0.45*sample_rate),int(0.45*sample_rate+1),int(0.9*sample_rate/24))):
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
            tx_rates = [(500e6)/8]
            tx_channels = [list(range(channels))]
            assert(len(rx_rates) == len(rx_channels))
            assert(len(rx_rates) == len(tx_rates))
            assert(len(rx_rates) == len(tx_channels))
            for n in range(len(rx_rates)):
                iteration_dict = {
                    "description" : descriptions[n],
                    "rx_rate" : rx_rates[n],
                    "rx_channels" : rx_channels[n],
                    "tx_rate" : tx_rates[n],
                    "tx_channels" : tx_channels[n]
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
                    "rx_channels" : rx_channels[n]
                }
                yield iteration_dict

        @staticmethod
        def tx_rate(channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            descriptions = ["Max achievable tx rate on any number of ch", "Max achievable tx rate on all ch"]
            # Higher rates are achievable outside of docker
            tx_rates = [250e6, (500e6)/8]
            tx_channels = [[0], list(range(channels))]
            assert(len(tx_rates) == len(tx_channels))
            for n in range(len(tx_rates)):
                iteration_dict = {
                    "description" : descriptions[n],
                    "tx_rate" : tx_rates[n],
                    "tx_channels" : tx_channels[n]
                }
                yield iteration_dict

        @staticmethod
        def tx_rx_longterm_rate():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            sample_rate = 9615384
            duration = 90
            yield locals()

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
            for wave_freq in list(range(-int(0.45*sample_rate),int(0.45*sample_rate+1),int(0.9*sample_rate/24))):
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
            tx_rates = [(500e6)/8]
            tx_channels = [list(range(channels))]
            assert(len(rx_rates) == len(rx_channels))
            assert(len(rx_rates) == len(tx_rates))
            assert(len(rx_rates) == len(tx_channels))
            for n in range(len(rx_rates)):
                iteration_dict = {
                    "description" : descriptions[n],
                    "rx_rate" : rx_rates[n],
                    "rx_channels" : rx_channels[n],
                    "tx_rate" : tx_rates[n],
                    "tx_channels" : tx_channels[n]
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
                    "rx_channels" : rx_channels[n]
                }
                yield iteration_dict

        @staticmethod
        def tx_rate(channels):
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)

            descriptions = ["Max achievable tx rate on any number of ch", "Max achievable tx rate on all ch"]
            # Higher rates are achievable outside of docker
            tx_rates = [250e6, (500e6)/8]
            tx_channels = [[0], list(range(channels))]
            assert(len(tx_rates) == len(tx_channels))
            for n in range(len(tx_rates)):
                iteration_dict = {
                    "description" : descriptions[n],
                    "tx_rate" : tx_rates[n],
                    "tx_channels" : tx_channels[n]
                }
                yield iteration_dict

        @staticmethod
        def tx_rx_longterm_rate():
            log.pvpkg_log_info("GENERATOR", sys._getframe().f_code.co_name)
            channels = list(range(4))
            sample_rate = 9615384
            duration = 90
            yield locals()

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
