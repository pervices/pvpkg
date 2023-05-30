from gnuradio import uhd

default_ampl = 9830.1 #default amplitude usually 0.3, just formatted it to be SC

def calibrate(end, channels, sample_rate, center_freq, gain, ampl=default_ampl):

    end.set_samp_rate(sample_rate)
    end.set_clock_source("internal")

    for channel in channels:
        end.set_center_freq(center_freq, channel)
        end.set_gain(gain, channel)
        end.set_amplitude(ampl, channel)

    end.set_time_now(uhd.time_spec(0.0))



def get_snk_s(channels, sample_rate, center_freq, gain, ampl=default_ampl):

    snk = uhd.usrp_sink("crimson", uhd.stream_args(cpu_format="sc16", otw_format="sc16", channels=channels))
    calibrate(snk, channels, sample_rate, center_freq, gain, ampl)
    return snk


def get_src_c(channels, sample_rate, center_freq, gain, ampl=default_ampl):

    src = uhd.usrp_source("crimson", uhd.stream_args(cpu_format="fc32", otw_format="sc16", channels=channels), False)
    calibrate(src, channels, sample_rate, center_freq, gain, ampl)
    return src

