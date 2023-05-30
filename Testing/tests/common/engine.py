from gnuradio import analog
from gnuradio import blocks
from gnuradio import uhd
from gnuradio import gr

from . import crimson
import threading
import time

default_amp = 9830.1 #the same as gnu radio, but in sc

def run_tx(csnk, channels, stack, sample_rate, wave_freq):

    """                                       +-----------+
    +---------+   +---------+   +---------+   |           |
    | sigs[0] |-->| heds[0] |-->| c2ss[0] |-->|ch[0]      |
    +---------+   +---------+   +---------+   |           |
    +---------+   +---------+   +---------+   |           |
    | sigs[1] |-->| heds[1] |-->| c2ss[1] |-->|ch[1]      |
    +---------+   +---------+   +---------+   |           |
                                              |           |
    +---------+   +---------+   +---------+   |           |
    | sigs[N] |-->| heds[N] |-->| c2ss[N] |-->|ch[N]      |
    +---------+   +---------+   +---------+   |      csnk |
                                              +-----------+
    """
    for frame in stack: #in fund_freq.py this is tx_stack

        # Connect.
        sigs = [analog.sig_source_c(
            sample_rate, analog.GR_SIN_WAVE, wave_freq, 2.0e4, 0.0)
            for ch in channels]

        heds = [blocks.head(gr.sizeof_gr_complex, frame[1]) #block_head=(sizeofstream_dataformat, nitems)= (sizeofgr_complex, frame[1]) = (16bit I & 16bit Q, tx_stack[ , it["sample_rate"]) in fund_freq test

            for ch in channels]

        c2ss = [blocks.complex_to_interleaved_short(True)
            for ch in channels]

        flowgraph = gr.top_block()
        for ch in channels:
            flowgraph.connect(sigs[ch], heds[ch])
            flowgraph.connect(heds[ch], c2ss[ch])
            flowgraph.connect(c2ss[ch], (csnk, ch))

        # Run.
        csnk.set_start_time(uhd.time_spec(frame[0])) #frame[0]= tx_stack[10, ] in fund_freq test
        flowgraph.run()
        #print("tx time spec is:", uhd.time_spec(frame[0]))
        for hed in heds:
            hed.reset()


def run_rx(csrc, channels, stack, sample_rate, _vsnk):

    """
    +-----------+
    |           |   +---------+
    |      ch[0]|-->| vsnk[0] |
    |           |   +---------+
    |           |   +---------+
    |      ch[1]|-->| vsnk[1] |
    |           |   +---------+
    |           |
    |           |   +---------+
    |      ch[N]|-->| vsnk[N] |
    | csrc      |   +---------+
    +-----------+
    """

    # Connect.
    vsnk = [blocks.vector_sink_c() for ch in channels]

    flowgraph = gr.top_block()
    for ch in channels:
        flowgraph.connect((csrc, ch), vsnk[ch])

    # Run. The flowgraph must be started before stream commands are sent.
    flowgraph.start()

    for frame in stack: #rx_stack in fund_freq

        cmd = uhd.stream_cmd_t(uhd.stream_mode_t.STREAM_MODE_NUM_SAMPS_AND_DONE)
        cmd.num_samps = frame[1] #frame[1]= rx_stack[( , it["sample_count"])] in fund_freq
        cmd.stream_now = False
        #print(frame[0])
        cmd.time_spec = uhd.time_spec(frame[0]) #frame[0]=rx_stack[ 10.005, ] in fund_freq
        csrc.issue_stream_cmd(cmd)
        #print("rx stack time is:", cmd.time_spec)

    # Wait for completion.
    total_sample_count = sum([frame[1] for frame in stack])
    #print("total sample count is:", total_sample_count)
    while len(vsnk[0].data()) < total_sample_count:
        time.sleep(0.1)

    flowgraph.stop()
    flowgraph.wait()

    # Cannot return from thread so extend instead.
    _vsnk.extend(vsnk)


def run(channels, wave_freq, sample_rate, center_freq, tx_gain, rx_gain, tx_stack, rx_stack, ampl=default_amp):

    # Setup.
    csnk = crimson.get_snk_s(channels, sample_rate, center_freq, tx_gain, ampl)
    csrc = crimson.get_src_c(channels, sample_rate, center_freq, rx_gain, ampl)

    # Run.
    vsnk = [] # Will be extended when using stacked commands.
    threads = [
        threading.Thread(target = run_tx, args = (csnk, channels, tx_stack, sample_rate, wave_freq)),
        threading.Thread(target = run_rx, args = (csrc, channels, rx_stack, sample_rate, vsnk)),
        ]
    for thread in threads:
        thread.start()

    # Stop.
    for thread in threads:
        thread.join()

    return vsnk

