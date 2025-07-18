from gnuradio import analog
from gnuradio import blocks
from gnuradio import uhd
from gnuradio import gr

from . import crimson
import threading
from threading import Event
import multiprocessing
from inspect import currentframe, getframeinfo
import time
import subprocess
import sys
import datetime

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
        for channel_index in range(len(channels)):
            flowgraph.connect(sigs[channel_index], heds[channel_index])
            flowgraph.connect(heds[channel_index], c2ss[channel_index])
            flowgraph.connect(c2ss[channel_index], (csnk, channel_index))

        # Run.
        csnk.set_start_time(uhd.time_spec(frame[0])) #frame[0]= tx_stack[10, ] in fund_freq test
        flowgraph.run()
        #print("tx time spec is:", uhd.time_spec(frame[0]))
        for hed in heds:
            hed.reset()


def run_rx(csrc, channels, stack, sample_rate, _vsnk, timeout_occured):

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
    for channel_index in range(len(channels)):
        flowgraph.connect((csrc, channel_index), vsnk[channel_index])

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

    expected_duration = stack[0][0] + (stack[0][1]/sample_rate) #stack[0][0] is start and stack[0][1] is the sample count
    timeout_time = time.clock_gettime(time.CLOCK_MONOTONIC) + expected_duration + 10

    #print("total sample count is:", total_sample_count)
    while len(vsnk[0].data()) < total_sample_count:
        time.sleep(0.1)
        if (time.clock_gettime(time.CLOCK_MONOTONIC) > timeout_time):
            frameinfo = getframeinfo(currentframe())
            hostname = subprocess.run(["cat /proc/sys/kernel/hostname | tr -d '\n' "], shell=True, capture_output=True, text=True).stdout
            uptime = subprocess.run(["cat /proc/uptime"], shell=True, capture_output=True, text=True).stdout
            date = datetime.datetime.now() #current date and time
            iso_time = date.strftime("%Y%m%dT%H%M%S.%fZ")
            errmsg = "[ERROR][{}:{}] - UHD failed to provide expected number of samples before RX timeout - HOSTNAME:{} - TIME:{} - UPTIME:{} - SAMPS RECEIVED:{} - SAMPS EXPECTED:{}".format(frameinfo.filename, frameinfo.lineno, hostname, iso_time, uptime, str(len(vsnk[0].data())), str(total_sample_count))
            print(errmsg)
            timeout_occured.set()
            break

    flowgraph.stop()
    flowgraph.wait()

    # Cannot return from thread so extend instead.
    _vsnk.extend(vsnk)

# Multiprocess is needed for the ability to terminate, but tx and rx must be in the same process as each other
# run_helper is run as it's own process, which then spawns tx and rx threads
def run_helper(channels, wave_freq, sample_rate, center_freq, tx_gain, rx_gain, tx_stack, rx_stack, data_queue):
    rx_timeout_occured = Event()

    vsnk = [] # Will be extended when using stacked commands.
    tx_duration = 0
    tx_thread = None
    rx_duration = 0
    rx_thread = None

    # Prepare thread
    if tx_stack != None:
        # Expected tx duration = start time of last burst + (length of last burst / sample rate)
        tx_duration = tx_stack[-1][0] + (tx_stack[-1][1] / sample_rate)

        csnk = crimson.get_snk_s(channels, sample_rate, center_freq, tx_gain)
        tx_thread = threading.Thread(target = run_tx, args = (csnk, channels, tx_stack, sample_rate, wave_freq))
    if rx_stack != None:
        # Expected rx duration = start time of last burst + (length of last burst / sample rate)
        rx_duration = rx_stack[-1][0] + (rx_stack[-1][1] / sample_rate)

        csrc = crimson.get_src_c(channels, sample_rate, center_freq, rx_gain)
        rx_thread = threading.Thread(target = run_rx, args = (csrc, channels, rx_stack, sample_rate, vsnk, rx_timeout_occured))

    # Start threads
    if(tx_thread != None):
        tx_thread.start()
    if(rx_thread != None):
        rx_thread.start()

    # Wait for thread to finish with a timeout
    if(tx_thread != None):
        tx_thread.join(tx_duration + 10)
    # The data timeout is expected + 10s, make sure the control timeout is longer
    if(rx_thread != None):
        rx_thread.join(rx_duration + 20)

    # Check if thread finished
    # Timeouts here indicate that something was hanging
    if(tx_thread != None):
        if(tx_thread.is_alive()):
            print("\x1b[31mERROR: Tx flowgraph timeout\x1b[0m", file=sys.stderr)
            raise Exception ("TX CONTROL TIMED OUT")

    if(rx_thread != None):
        if(rx_thread.is_alive()):
            print("\x1b[31mERROR: Rx flowgraph timeout\x1b[0m", file=sys.stderr)
            raise Exception ("RX CONTROL TIMED OUT")

    # A timeout here means insufficent data was received
    if rx_timeout_occured.is_set():
        print("\x1b[31mERROR: Timeout while waiting for sufficient rx data\x1b[0m", file=sys.stderr)
        raise Exception ("RX DATA TIMED OUT")

    data_queue.put(vsnk)

def run(channels, wave_freq, sample_rate, center_freq, tx_gain, rx_gain, tx_stack, rx_stack):
    print("A0")

    # Queue to store data from run_helper
    data_queue = multiprocessing.Queue(1)
    print("A1")

    # Start process to run tx and rx
    helper_process = multiprocessing.Process(target = run_rx, args = (csrc, channels, rx_stack, sample_rate, vsnk, rx_timeout_occured, data_queue))
    print("A2")
    helper_process.start()
    print("A3")

    tx_duration = 0
    rx_duration = 0

    # Prepare thread
    if tx_stack != None:
        # Expected tx duration = start time of last burst + (length of last burst / sample rate)
        tx_duration = tx_stack[-1][0] + (tx_stack[-1][1] / sample_rate)

    if rx_stack != None:
        # Expected rx duration = start time of last burst + (length of last burst / sample rate)
        rx_duration = rx_stack[-1][0] + (rx_stack[-1][1] / sample_rate)

    time_limit = max(tx_duration + rx_duration) + 30
    # Wait iteration to run
    print("T1")
    helper_process.join(time_limit)
    print("T2")

    flowgraph_timeout = False
    # If the process has finished
    if(not helper_process.is_alive()):
        print("T3")
        # If the test ran successfully
        if(helper_process.exitcode == 0):
            print("T4A")
            # Return collected data
            return (data_queue.get())
        else:
            print("T4B")
            # An error (probably rx data timeout) while running the flowgraph
            print("\x1b[31mERROR: error while running flowgraph\x1b[0m", file=sys.stderr)
            raise Exception ("flowgraph error")
    else:
        print("T5")
        print("\x1b[31mERROR: Flowgraph timeout. UHD appears to be hanging forever. Issuing SIGTERM\x1b[0m", file=sys.stderr)
        flowgraph_timeout = True
        # Issue SIGTERM
        helper_process.terminate()
        # Wait for process to close
        helper_process.join(30)

    flow_sigterm_timeout = False
    if(helper_process.is_alive()):
        print("\x1b[31mERROR: Flowgraph still hanging after issuing SIGTERM. Issuing SIGKILL\x1b[0m", file=sys.stderr)
        helper_process.kill()
        flow_sigterm_timeout = True
        # Wait for process to close
        helper_process.join(30)

    if(helper_process.is_alive()):
        print("\x1b[31mERROR: Flowgraph still hanging after issuing SIGKILL\x1b[0m", file=sys.stderr)
        raise Exception ("flowgraph SIGKILL timeout")

    elif(flow_sigterm_timeout):
        raise Exception ("flowgraph SIGTERM timeout")

    elif(flowgraph_timeout):
        raise Exception ("flowgraph timeout")

    # Unreachable error message in case of a mistake during the previous elif series
    else:
        print("\x1b[31mERROR: No valid data but no flowgraph error detected. This should be unreachable\x1b[0m", file=sys.stderr)
        raise Exception ("Unexpected error")


def manual_tune_run(channels, wave_freq, tx_sample_rate, rx_sample_rate, tx_tune_request, rx_tune_request, tx_gain, rx_gain, tx_stack, rx_stack):
    # Setup
    csnk = crimson.get_snk_s(channels, tx_sample_rate, tx_tune_request, tx_gain)
    csrc = crimson.get_src_c(channels, rx_sample_rate, rx_tune_request, rx_gain)

    rx_timeout_occured = Event()

    # Run.
    vsnk = [] # Will be extended when using stacked commands.

    # Prepare thread
    # Expected tx duration = start time of last burst + (length of last burst / sample rate)
    tx_duration = tx_stack[-1][0] + (tx_stack[-1][1] / tx_sample_rate)
    tx_thread = multiprocessing.Process(target = run_tx, args = (csnk, channels, tx_stack, tx_sample_rate, wave_freq))
    rx_duration = rx_stack[-1][0] + (rx_stack[-1][1] / rx_sample_rate)
    rx_thread = multiprocessing.Process(target = run_rx, args = (csrc, channels, rx_stack, rx_sample_rate, vsnk, rx_timeout_occured))

    # Start threads
    tx_thread.start()
    rx_thread.start()

    # Wait for thread to finish with a timeout
    tx_thread.join(tx_duration + 10)
    # The data timeout is expected + 10s, make sure the control timeout is longer
    rx_thread.join(rx_duration + 20)

    # Check if thread finished
    # Timeouts here indicate that something was hanging
    if(tx_thread.is_alive()):
        print("\x1b[31mERROR: Tx flowgraph timeout\x1b[0m", file=sys.stderr)
        raise Exception ("TX CONTROL TIMED OUT")

    if(rx_thread.is_alive()):
        print("\x1b[31mERROR: Rx flowgraph timeout\x1b[0m", file=sys.stderr)
        raise Exception ("RX CONTROL TIMED OUT")

    if rx_timeout_occured.is_set():
        print("\x1b[31mERROR: Timeout while waiting for sufficient rx data\x1b[0m", file=sys.stderr)
        raise Exception ("RX TIMED OUT")

    return vsnk
