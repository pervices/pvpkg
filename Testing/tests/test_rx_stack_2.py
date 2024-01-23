from gnuradio import blocks
from gnuradio import uhd
from gnuradio import gr
from common import pdf_report
from common import crimson
from common import test_args
import time
import math
import numpy as np
import sys
import os

# This test does not use the engine as it only tests the RX

def main():
    targs = test_args.TestArgs(testDesc="Rx Sample Count Test 2")

    global report

    report = pdf_report.ClassicShipTestReport("rx_stack2", targs.serial, targs.report_dir, targs.docker_sha)
    if(targs.product == 'Tate'):
        report.insert_title_page("Cyan RX Sample Count Test")
        # Cyan NRNT Setup.
        channels = np.array([0,1,2,3])
        sample_rate = 100e6
        sample_count = 4096

        # Cyan acts as a source by providing complex float samples.
        csrc = crimson.get_src_c(channels, sample_rate, 100e6, 1.0)

    else:
        report.insert_title_page("Crimson RX Sample Count Test")
        # Crimson TNG Setup.
        channels = np.array([0,1,2,3])
        sample_rate = 20312500
        sample_count = 4096

        # Crimson TNG acts as a source by providing complex float samples.
        csrc = crimson.get_src_c(channels, sample_rate, 15e6, 1.0)


    test_table = [
        ['Channel', 'Expected Sample Count', 'Actual Sample Count', 'Result']
    ]

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
    host_start_time = time.perf_counter()
    start = 10       #Start Time
    end = 15         #End Time
    interval = 1    #Increment time (Wait this long between subsequent Rx commands)
    poll_delay = interval/2.0 # When to poll the data to see how much has been received

    #Create an expected Rx sample count array for the amount of samples expected to be received
    sample_count_array=np.arange(sample_count, int(sample_count*((end-start)+1)), sample_count, dtype=np.int32)
    zero_count_array=np.zeros(start, dtype=np.int32)
    expect_count_array= np.append(zero_count_array, sample_count_array)
    print("the theoretical expected sample count array is:", expect_count_array)

    # PDF report table for expected count
    table_data_expect_count_array = [['0']*len(expect_count_array)]
    for i in range(len(expect_count_array)):
        table_data_expect_count_array[0][i] = str(expect_count_array[i])
    report.insert_text_large("Test Results")
    report.insert_table(table_data_expect_count_array, 20, "Theoretical expected sample count array, for all channels")

    for second in range(start, end, interval):
        cmd = uhd.stream_cmd_t(uhd.stream_mode_t.STREAM_MODE_NUM_SAMPS_AND_DONE)
        cmd.num_samps = sample_count
        cmd.stream_now = False
        cmd.time_spec = uhd.time_spec(second)
        csrc.issue_stream_cmd(cmd)

    #Poll for incoming RX commands and print the length of the vector sink.

    ch_1_array = [0] * end
    ch_2_array = [0] * end
    ch_3_array = [0] * end
    ch_4_array = [0] * end

    config_time = time.perf_counter() - host_start_time
    sampling_start_time = math.ceil(config_time)
    time.sleep(sampling_start_time - config_time)

    for second in range(sampling_start_time, end):
        start_time = time.perf_counter()
        time.sleep(poll_delay)

        ch_1_array[second] = (len(vsnk[0].data()))
        ch_2_array[second] = (len(vsnk[1].data()))
        ch_3_array[second] = (len(vsnk[2].data()))
        ch_4_array[second] = (len(vsnk[3].data()))

        #Populate slot 1 of that array with the sample count for that time interval
        print("%d: %d: %d" % (0, second, len(vsnk[0].data())))
        print("%d: %d: %d" % (1, second, len(vsnk[1].data())))
        print("%d: %d: %d" % (2, second, len(vsnk[2].data())))
        print("%d: %d: %d" % (3, second, len(vsnk[3].data())))

        while(time.perf_counter() - start_time < interval):
            pass

    ch_1_actual_array=np.asarray(ch_1_array)
    ch_2_actual_array=np.asarray(ch_2_array)
    ch_3_actual_array=np.asarray(ch_3_array)
    ch_4_actual_array=np.asarray(ch_4_array)
    print("the collected channel 1 sample count array is:", ch_1_actual_array)
    print("the collected channel 2 sample count array is:", ch_2_actual_array)
    print("the collected channel 3 sample count array is:", ch_3_actual_array)
    print("the collected channel 4 sample count array is:", ch_4_actual_array)

    # PDF report result tables
    table_data_ch1_array = [['0']*len(ch_1_array)]
    # rotate the table
    for i in range(len(ch_1_array)):
        table_data_ch1_array[0][i] = str(ch_1_array[i])

    table_data_ch2_array = [['0']*len(ch_2_array)]
    for i in range(len(ch_2_array)):
        table_data_ch2_array[0][i] = str(ch_2_array[i])

    table_data_ch3_array = [['0']*len(ch_3_array)]
    for i in range(len(ch_3_array)):
        table_data_ch3_array[0][i] = str(ch_3_array[i])

    table_data_ch4_array = [['0']*len(ch_4_array)]
    for i in range(len(ch_4_array)):
        table_data_ch4_array[0][i] = str(ch_4_array[i])


    report.insert_table(table_data_ch1_array, 20, "Collected channel 1 sample count array")
    report.insert_table(table_data_ch2_array, 20, "Collected channel 2 sample count array")
    report.insert_table(table_data_ch3_array, 20, "Collected channel 3 sample count array")
    report.insert_table(table_data_ch4_array, 20, "Collected channel 4 sample count array")

    test_fail = 0
    #Test 2: Make sure that slots 0..start = 0, and start..end increment by sample count.
    try:
        assert (np.array_equal((ch_1_actual_array),(expect_count_array)))
        assert (np.array_equal((ch_2_actual_array),(expect_count_array)))
        assert (np.array_equal((ch_3_actual_array),(expect_count_array)))
        assert (np.array_equal((ch_4_actual_array),(expect_count_array)))
    except:
        print('expected and actual array are not equal, fail')
        test_fail = 1

    if (test_fail):
        report.insert_text_large("Test failed")
    else:
        report.insert_text_large("Test passed")

    report.save()
    print("PDF report saved at " + report.get_filename())

    if (test_fail):
        sys.exit(1)

main()
