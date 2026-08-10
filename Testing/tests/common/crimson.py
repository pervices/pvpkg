import time

# gnuradio/uhd is imported lazily inside each function (instead of at module
# scope) because these functions only ever run inside the forked child
# process spawned by common.engine. UHD's log-delivery thread is created the
# first time libuhd is loaded; if that happens in the parent before fork(),
# the thread does not survive into the child and UHD_LOG_* output is
# silently dropped there. Importing here instead ensures libuhd (and its log
# thread) is first loaded in the child.

def calibrate(end, channels, sample_rate, center_freq, gain, lo_offset=None):
    from gnuradio import uhd

    end.set_samp_rate(sample_rate)
    end.set_clock_source("internal")

    # lo_offset is only given for manual tuning; building the tune_request here
    # (rather than in the caller) keeps uhd.tune_request construction inside
    # the forked child, same reasoning as the deferred import above.
    freq_arg = uhd.tune_request(center_freq, lo_offset) if lo_offset is not None else center_freq
    for channel_index in range(len(channels)):
        end.set_center_freq(freq_arg, channel_index)
        end.set_gain(gain, channel_index)

    end.set_time_now(uhd.time_spec(0.0))


def get_snk_s(channels, sample_rate, center_freq, gain, addr, lo_offset=None):
    from gnuradio import uhd

    snk = uhd.usrp_sink(f"crimson,addr={addr}", uhd.stream_args(cpu_format="sc16", otw_format="sc16", channels=channels))
    calibrate(snk, channels, sample_rate, center_freq, gain, lo_offset)
    return snk


def get_src_c(channels, sample_rate, center_freq, gain, addr, lo_offset=None):
    from gnuradio import uhd

    src = uhd.usrp_source(f"crimson,addr={addr}", uhd.stream_args(cpu_format="fc32", otw_format="sc16", channels=channels), False)
    calibrate(src, channels, sample_rate, center_freq, gain, lo_offset)
    return src

