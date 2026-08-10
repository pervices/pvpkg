import time

# gnuradio/uhd is imported lazily inside each function (instead of at module
# scope) because these functions only ever run inside the forked child
# process spawned by common.engine. UHD's log-delivery thread is created the
# first time libuhd is loaded; if that happens in the parent before fork(),
# the thread does not survive into the child and UHD_LOG_* output is
# silently dropped there. Importing here instead ensures libuhd (and its log
# thread) is first loaded in the child.

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

