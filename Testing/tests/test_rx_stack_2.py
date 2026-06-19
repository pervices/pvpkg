from gnuradio import blocks
from gnuradio import uhd
from gnuradio import gr
from common import pdf_report
from common import crimson
from common import test_args
from common import log
import time
import math
import numpy as np
import sys
import os

# This test does not use the engine as it only tests the RX

def main():
    targs = test_args.TestArgs(testDesc="Rx Sample Count Test 2")
    test_fail = 0

    global report

    report = pdf_report.ClassicShipTestReport("rx_stack2", targs.serial, targs.report_dir, targs.docker_sha)
    if(targs.product == 'Tate' or targs.product == "BasebandTate"):
        report.insert_title_page("Cyan RX Sample Count Test")
        # Cyan NRNT Setup.
        # If the channels argument was set, it will override the default four channels.
        if targs.channels != None:
            channels = targs.channels
        else:
            channels = np.array([0,1,2,3])

        sample_rate = 100e6
        sample_count = 4096

        # Cyan acts as a source by providing complex float samples.
        csrc = crimson.get_src_c(channels, sample_rate, 100e6, 1.0)

    elif(targs.product == 'Lily'):
        report.insert_title_page("Chestnut RX Sample Count Test")
        # Chestnut Setup.
        # If the channels argument was set, it will override the default four channels.
        if targs.channels != None:
            channels = targs.channels
        else:
            channels = np.array([0,1,2,3])

        sample_rate = 100e6
        sample_count = 4096

        # Cyan acts as a source by providing complex float samples.
        csrc = crimson.get_src_c(channels, sample_rate, 100e6, 1.0)

    elif(targs.product == "Vaunt"):
        report.insert_title_page("Crimson RX Sample Count Test")
        # Crimson TNG Setup.
        # If the channels argument was set, it will override the default four channels.
        if targs.channels != None:
            channels = targs.channels
        else:
            channels = np.array([0,1,2,3])

        sample_rate = 20312500
        sample_count = 4096

        # Crimson TNG acts as a source by providing complex float samples.
        csrc = crimson.get_src_c(channels, sample_rate, 15e6, 1.0)

    elif(targs.product == "Avery"):
        report.insert_title_page("Calamine RX Sample Count Test")
        # Calamine Setup.
        # If the channels argument was set, it will override the default four channels.
        if targs.channels != None:
            channels = targs.channels
        else:
            channels = np.array([0,1,2,3])

        sample_rate = 300e6/16
        sample_count = 4096

        # Calamine acts as a source by providing complex float samples.
        csrc = crimson.get_src_c(channels, sample_rate, 15e6, 1.0)

    else:
        log.pvpkg_log_error("RX_STACK_2", "Unrecognized product argument")
        test_fail = 1


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
    log.pvpkg_log_info("RX_STACK_2", "The theoretical expected sample count array is: {}".format(expect_count_array))

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

    # Initialize channel arrays
    ch_arrays = [[0] * end for _ in channels]

    config_time = time.perf_counter() - host_start_time
    sampling_start_time = math.ceil(config_time)
    time.sleep(sampling_start_time - config_time)

    for second in range(sampling_start_time, end):
        start_time = time.perf_counter()
        time.sleep(poll_delay)

        # Store sample counts of each channel
        for i, ch in enumerate(ch_arrays):
            ch[second] = (len(vsnk[i].data()))

        #Populate slot 1 of that array with the sample count for that time interval
        log.pvpkg_log("<CH: SECOND: SAMPLE_COUNT>")
        for i, ch in enumerate(ch_arrays):
            log.pvpkg_log("%d: %d: %d" % (i, second, ch[second]))

        while(time.perf_counter() - start_time < interval):
            pass

    # Print sample count for each channel
    ch_actual_arrays = [np.asarray(ch_array) for ch_array in ch_arrays]
    for i, ch in channels:
        log.pvpkg_log_info("RX_STACK_2", "The collected channel {} sample count array is: {}".format(ch, ch_actual_arrays[i]))

    # PDF report result tables
    table_data_ch_arrays = [[['0']*len(ch_arr)] for ch_arr in ch_arrays]
    for i, ch in enumerate(ch_arrays):
        # rotate the table
        for j in range(len(ch)):
            table_data_ch_arrays[i][0][j] = str(ch[j])


    # Add tables to report
    for i, ch in channels:
        report.insert_table(table_data_ch_arrays[i], 20, "Collected channel {} sample count array".format(ch))

    #Test 2: Make sure that slots 0..start = 0, and start..end increment by sample count.
    try:
        for ch_array in ch_actual_arrays:
            assert (np.array_equal((ch_array),(expect_count_array)))
    except:
        log.pvpkg_log_error("RX_STACK_2", 'expected and actual array are not equal, fail')
        test_fail = 1

    if (test_fail):
        report.insert_text_large("Test failed")
    else:
        report.insert_text_large("Test passed")

    report.save()
    log.pvpkg_log_info("RX_STACK_2", "PDF report saved at " + report.get_filename())

    if (test_fail):
        sys.exit(1)

main()
