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
    csrc = crimson.get_src_c(channels, sample_rate, 15e6, 5.0)

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
    start = 10       #Start Time
    end = 15         #End Time
    interval = 1    #Increment time (Wait this long between subsequent Rx commands)

    #Create an expected Rx sample count array for the amount of samples expected to be received
    sample_count_array=np.arange(sample_count, int(sample_count*((end-start)+1)), sample_count, dtype=np.int32)
    zero_count_array=np.zeros(start, dtype=np.int32)
    expect_count_array= np.append(zero_count_array, sample_count_array)
    print("the theoretical expected sample count array is:", expect_count_array)

    interval_additional_delay_coefficient = 0.1          # Time at which we poll between Rx commands
    for second in range(start, end, interval):
        cmd = uhd.stream_cmd_t(uhd.stream_mode_t.STREAM_MODE_NUM_SAMPS_AND_DONE)
        cmd.num_samps = sample_count
        cmd.stream_now = False
        cmd.time_spec = uhd.time_spec(second)
        csrc.issue_stream_cmd(cmd)

    #Poll for incoming RX commands and print the length of the vector sink.

    ch_1_array = []
    ch_2_array = []
    ch_3_array = []
    ch_4_array = []
    for second in range(end):
        #print(channel)
        print("%d: %d: %d" % (0, second, len(vsnk[0].data())))
        ch_1_array.append(len(vsnk[0].data()))
        print("%d: %d: %d" % (1, second, len(vsnk[1].data())))
        ch_2_array.append(len(vsnk[1].data()))
        print("%d: %d: %d" % (2, second, len(vsnk[2].data())))
        ch_3_array.append(len(vsnk[2].data()))
        print("%d: %d: %d" % (3, second, len(vsnk[3].data())))
        ch_4_array.append(len(vsnk[3].data()))
        #Populate slot 1 of that array with the sample count for that time interval
        time.sleep(interval+interval*interval_additional_delay_coefficient)

    ch_1_actual_array=np.asarray(ch_1_array)
    ch_2_actual_array=np.asarray(ch_2_array)
    ch_3_actual_array=np.asarray(ch_3_array)
    ch_4_actual_array=np.asarray(ch_4_array)
    print("the collected channel 1 sample count array is:", ch_1_actual_array)
    print("the collected channel 2 sample count array is:", ch_2_actual_array)
    print("the collected channel 3 sample count array is:", ch_3_actual_array)
    print("the collected channel 4 sample count array is:", ch_4_actual_array)

    #Test 2: Make sure that slots 0..start = 0, and start..end increment by sample count.
    try:
        assert (np.array_equal((ch_1_actual_array),(expect_count_array)))
        assert (np.array_equal((ch_2_actual_array),(expect_count_array)))
        assert (np.array_equal((ch_3_actual_array),(expect_count_array)))
        assert (np.array_equal((ch_4_actual_array),(expect_count_array)))
    except:
        print('expected and actual array are not equal, fail')
        sys.exit(1)

main()
