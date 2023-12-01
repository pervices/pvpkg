from gnuradio import uhd

def calibrate(end, channels, sample_rate, center_freq, gain):

    end.set_samp_rate(sample_rate)
    end.set_clock_source("internal")

    for channel_index in range(len(channels)):
        end.set_center_freq(center_freq, channel_index)
        end.set_gain(gain, channel_index)

    end.set_time_now(uhd.time_spec(0.0))


def get_snk_s(channels, sample_rate, center_freq, gain):

    snk = uhd.usrp_sink("crimson", uhd.stream_args(cpu_format="sc16", otw_format="sc16", channels=channels))
    calibrate(snk, channels, sample_rate, center_freq, gain)
    return snk


def get_src_c(channels, sample_rate, center_freq, gain):

    src = uhd.usrp_source("crimson", uhd.stream_args(cpu_format="fc32", otw_format="sc16", channels=channels), False)
    calibrate(src, channels, sample_rate, center_freq, gain)
    return src

