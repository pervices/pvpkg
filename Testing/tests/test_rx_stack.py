from gnuradio import blocks
from gnuradio import uhd
from gnuradio import gr

from common import crimson
import time
import numpy as np
import sys

# This test does not use the engine as it only tests the RX 

def main():

    # Crimson TNG Setup.
    channels = np.array([0,1,2,3])
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
    start = 3       #Start Time
    end = 8         #End Time
    interval = 1    #Increment time (Wait this long between subsequent Rx commands)

    interval_additional_delay_coefficient = 0.1          # Time at which we poll between Rx commands
    for second in range(start, end, interval):
        cmd = uhd.stream_cmd_t(uhd.stream_mode_t.STREAM_MODE_NUM_SAMPS_AND_DONE)
        cmd.num_samps = sample_count
        cmd.stream_now = False
        cmd.time_spec = uhd.time_spec(second)
        csrc.issue_stream_cmd(cmd)

    # Poll for incoming RX commands and print the length of the vector sink.
    for sec in range(end):
        for channel in channels:
            #print(channel)
            print("%d: %d: %d" % (channel, sec, len(vsnk[channel].data())))
            print(len(vsnk[channel].data()))
            #Populate slot 1 of that array with the sample count for that time interval
        time.sleep(interval+interval*interval_additional_delay_coefficient)

    #Poll for incoming RX commands and print the length of the vector sink.

    #make a pass/fail object that defaults true;
    # Cleanup and validate.
    flowgraph.stop()
    flowgraph.wait()

    #Test 1: assure length of all Rx samples received are as expected
    for channel in channels:
        expect_sample_count = sample_count * (end - start)
        actual_sample_count = len((vsnk[channel].data()))

        print("the expected sample count and the actual sample count are:", expect_sample_count,actual_sample_count)
        #Assert that both are true (or make a global pass bool)
        assert expect_sample_count == actual_sample_count

main()

