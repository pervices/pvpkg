from gnuradio import blocks
from gnuradio import uhd
from gnuradio import gr

from common import crimson
from common import pdf_report
from common import test_args
import time, sys, os
import numpy as np

# This test does not use the engine as it only tests the RX

def main():
    targs = test_args.TestArgs(testDesc="Rx Sample Count Test")
    failed = 0 # flag for marking fails

    global report

    report = pdf_report.ClassicShipTestReport("rx_stack", targs.serial, targs.report_dir, targs.docker_sha)
    if(targs.product == 'Tate' or targs.product == "BasebandTate"):
        report.insert_title_page("Cyan RX Sample Count Test")
        # Cyan NRNT Setup.
        channels = np.array([0,1,2,3])
        sample_rate = 100e6
        sample_count = 4096

        # Cyan acts as a source by providing complex float samples.
        csrc = crimson.get_src_c(channels, sample_rate, 100e6, 1.0)

    if(targs.product == 'Lily'):
        report.insert_title_page("Chestnut RX Sample Count Test")
        # Chestnut Setup.
        channels = np.array([0,1,2,3])
        sample_rate = 100e6
        sample_count = 4096

        # Chestnut acts as a source by providing complex float samples.
        csrc = crimson.get_src_c(channels, sample_rate, 100e6, 1.0)

    elif(targs.product == "Vaunt"):
        report.insert_title_page("Crimson RX Sample Count Test")
        # Crimson TNG Setup.
        channels = np.array([0,1,2,3])
        sample_rate = 20312500
        sample_count = 4096

        # Crimson TNG acts as a source by providing complex float samples.
        csrc = crimson.get_src_c(channels, sample_rate, 15e6, 1.0)

    else:
        print("ERROR: unrecognized product argument", file=sys.stderr)
        failed = 1

    test_table = [
        ['Channel', 'Expected Sample Count', 'Actual Sample Count', 'Result']
    ]

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
        test_table.append([str(channel), str(expect_sample_count), str(actual_sample_count), bool_to_passfail(expect_sample_count == actual_sample_count)])

        #Assert that both are true (or make a global pass bool)
        try:
            assert expect_sample_count == actual_sample_count
        except:
            failed = 1

    report.insert_text_large("Test Results")
    report.insert_table(test_table, 20)

    report.save()
    print("PDF report saved at " + report.get_filename())

    if (failed == 1):
        sys.exit(1)

def bool_to_passfail(input) -> str:
    if (input):
        return 'Pass'
    return 'Fail'

if __name__ == '__main__':
    main()

