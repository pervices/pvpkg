import subprocess
import sys

from gnuradio import gr


PATH = '/usr/lib/uhd/examples/benchmark_rate'



def rx_benchmark(header='', duration=10, rx_rate=65e6, rx_channels="0,1,2,3", drop_threshold=0, seq_threshold=0, multi_streamer=True, rx_otw=True, sc='sc16', rx_cpu="sc16", rx_delay=0):
    # sample = b'\n[00:00:00.001327] Creating the usrp device with: ...\nUsing Device: Single USRP:\n  Device: Crimson_TNG Device\n  Mboard 0: FPGA Board\n  RX Channel: 0\n    RX DSP: 0\n    RX Dboard: A\n    RX Subdev: RX Board\n  RX Channel: 1\n    RX DSP: 1\n    RX Dboard: B\n    RX Subdev: RX Board\n  RX Channel: 2\n    RX DSP: 2\n    RX Dboard: C\n    RX Subdev: RX Board\n  RX Channel: 3\n    RX DSP: 3\n    RX Dboard: D\n    RX Subdev: RX Board\n  TX Channel: 0\n    TX DSP: 0\n    TX Dboard: A\n    TX Subdev: TX Board\n  TX Channel: 1\n    TX DSP: 1\n    TX Dboard: B\n    TX Subdev: TX Board\n  TX Channel: 2\n    TX DSP: 2\n    TX Dboard: C\n    TX Subdev: TX Board\n  TX Channel: 3\n    TX DSP: 3\n    TX Dboard: D\n    TX Subdev: TX Board\n\n[00:00:02.777343090] Setting device timestamp to 0...\n[00:00:05.122759308] Testing receive rate 65.000000 Msps on 1 channels\n[00:00:05.770122556] Testing receive rate 65.000000 Msps on 1 channels\n[00:00:06.434822104] Testing receive rate 65.000000 Msps on 1 channels\n[00:00:07.99982647] Testing receive rate 65.000000 Msps on 1 channels\n[00:00:17.317633880] Benchmark complete.\n\n\nBenchmark rate summary:\n  Num received samples:     1752556432\n  Num dropped samples:      0\n  Num overruns detected:    0\n  Num transmitted samples:  0\n  Num sequence errors (Tx): 0\n  Num sequence errors (Rx): 0\n  Num underruns detected:   0\n  Num late commands:        0\n  Num timeouts (Tx):        0\n  Num timeouts (Rx):        0\n\n\nDone!\n\n'
    print("*****************************\n")
    print(header,'\n')
    print("*****************************\n\n")
    sample = subprocess.check_output([PATH, '--duration', str(duration), '--rx_rate', str(rx_rate), '--rx_channels', rx_channels, '--drop-threshold', str(drop_threshold), '--seq-threshold', str(seq_threshold),'--multi_streamer' if multi_streamer else '', '--rx_otw', sc, '--rx_cpu', rx_cpu, '--rx_delay', str(rx_delay)])
    sample = sample.decode()
    benchmark_summary = sample.split('Benchmark rate summary:\n')[1]
    results = benchmark_summary.split('\n')[0:10]

    data_entry = {}
    for result in results:
        result = result.split(':')
        result_entry = result[0].lstrip()
        result_data  = int(result[1])

        print(result_entry, result_data)
        if result_entry in ['Num received samples', 'Num transmitted samples']:
            continue

        try:
            assert result_data == 0
        except:
            print('ERROR with rx_benchmark', result_entry, result_data);
            sys.exit(1)


rx_benchmark(header='Rx, multi-streamer, sc16, no delay')
rx_benchmark(header='Rx, multi-streamer, sc16, 5s delay', rx_delay=5)
rx_benchmark(header='Rx, multi-streamer, fc32, 5s delay', rx_rate=20e6, rx_cpu='fc32')
rx_benchmark(header='Rx, single, fc32, 0s delay', rx_rate=20e6, rx_cpu='fc32', rx_delay=5, multi_streamer=False)



# def tx_benchmark():

# def rx_tx_benchmark():
