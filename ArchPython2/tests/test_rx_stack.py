from gnuradio import blocks
from gnuradio import uhd
from gnuradio import gr

from common import crimson
import time

# This test does not use the engine as it only tests the RX 

def main():

    # Crimson TNG Setup.
    channels = range(4)
    sample_rate = 20e6
    sample_count = 4096

    # Crimson TNG acts as a source by providing complex float samples.
    csrc = crimson.get_src_c(channels, sample_rate, 15e6, 1.0)

    # Vector buffer that accepts complex float samples.
    vsnk = [blocks.vector_sink_c() for channel in channels]

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
    flowgraph = gr.top_block()
    for channel in channels:
        flowgraph.connect((csrc, channel), vsnk[channel])

    # The flowgraph must be started before commands are sent.
    flowgraph.start()

    # Enqueue one RX command every second starting at <start> and ending at <end> times.
    csrc.set_time_now(uhd.time_spec(0.0))
    start = 3
    end = 8
    for second in range(start, end, 1):
        cmd = uhd.stream_cmd_t(uhd.stream_cmd_t.STREAM_MODE_NUM_SAMPS_AND_DONE)
        cmd.num_samps = sample_count
        cmd.stream_now = False
        cmd.time_spec = uhd.time_spec(second)
        csrc.issue_stream_cmd(cmd)

    # Poll for incoming RX commands and print the length of the vector sink.
    for second in range(end):
        for channel in channels:
            print "%d: %d" % (second, len(vsnk[channel].data()))
        time.sleep(1.0)

    # Cleanup and validate.
    flowgraph.stop()
    flowgraph.wait()
    for channel in channels:
        expect_sample_count = sample_count * (end - start)
        actual_sample_count = len(vsnk[channel].data())
        assert expect_sample_count == actual_sample_count


main()

