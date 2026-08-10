import time

# "from gnuradio import uhd" intializes logging, however logging breaks across forks (multiprocessing)
# To ensure logging works correctly only import uhd from within functions that are called in the forks
# Adding "from gnuradio import uhd" would break UHD_LOG_*

def calibrate(end, channels, sample_rate, center_freq, gain):
    from gnuradio import uhd

    end.set_samp_rate(sample_rate)
    end.set_clock_source("internal")

    for channel_index in range(len(channels)):
        end.set_center_freq(center_freq, channel_index)
        end.set_gain(gain, channel_index)

    end.set_time_now(uhd.time_spec(0.0))


def get_snk_s(channels, sample_rate, center_freq, gain, addr):
    from gnuradio import uhd

    snk = uhd.usrp_sink(f"crimson,addr={addr}", uhd.stream_args(cpu_format="sc16", otw_format="sc16", channels=channels))
    calibrate(snk, channels, sample_rate, center_freq, gain)
    return snk


def get_src_c(channels, sample_rate, center_freq, gain, addr):
    from gnuradio import uhd

    src = uhd.usrp_source(f"crimson,addr={addr}", uhd.stream_args(cpu_format="fc32", otw_format="sc16", channels=channels), False)
    calibrate(src, channels, sample_rate, center_freq, gain)
    return src

