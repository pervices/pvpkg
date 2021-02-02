from gnuradio import analog
from gnuradio import blocks
from gnuradio import uhd
from gnuradio import gr

import crimson
import threading
import time

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
    for frame in stack:

        # Connect.
        sigs = [analog.sig_source_c(
            sample_rate, analog.GR_SIN_WAVE, wave_freq, 2.0e4, 0.0)
            for ch in channels]

        heds = [blocks.head(gr.sizeof_gr_complex, frame[1])
            for ch in channels]

        c2ss = [blocks.complex_to_interleaved_short(True)
            for ch in channels]

        flowgraph = gr.top_block()
        for ch in channels:
            flowgraph.connect(sigs[ch], heds[ch])
            flowgraph.connect(heds[ch], c2ss[ch])
            flowgraph.connect(c2ss[ch], (csnk, ch))

        # Run.
        csnk.set_start_time(uhd.time_spec(frame[0]))
        flowgraph.run()
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

    for frame in stack:

        cmd = uhd.stream_cmd_t(uhd.stream_cmd_t.STREAM_MODE_NUM_SAMPS_AND_DONE)
        cmd.num_samps = frame[1]
        cmd.stream_now = False
        cmd.time_spec = uhd.time_spec(frame[0])
        csrc.issue_stream_cmd(cmd)

    # Wait for completion.
    total_sample_count = sum([frame[1] for frame in stack])
    while len(vsnk[0].data()) < total_sample_count:
        time.sleep(0.1)

    flowgraph.stop()
    flowgraph.wait()

    # Cannot return from thread so extend instead.
    _vsnk.extend(vsnk)


def run(channels, wave_freq, sample_rate, center_freq, tx_gain, rx_gain, tx_stack, rx_stack):

    # Setup.
    csnk = crimson.get_snk_s(channels, sample_rate, center_freq, tx_gain)
    csrc = crimson.get_src_c(channels, sample_rate, center_freq, rx_gain)

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

