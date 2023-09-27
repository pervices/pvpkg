import subprocess
import sys

from gnuradio import gr


PATH = '/usr/lib/uhd/examples/benchmark_rate'



def rx_benchmark(header='', duration=10, rx_rate=65e6, rx_channels="0,1,2,3", drop_threshold=0, seq_threshold=0, multi_streamer=True, rx_otw=True, sc='sc16', rx_cpu="sc16", rx_delay=0):
    print('\n\n\n')
    print("*****************************\n")
    print('RX/TX', rx_cpu, 'multi-streamer' if multi_streamer else 'single','rx_delay='+str(rx_delay),'\n')
    print("*****************************\n\n")

    sample = subprocess.check_output([PATH, '--duration', str(duration), '--rx_rate', str(rx_rate), '--rx_channels', rx_channels, '--drop-threshold', str(drop_threshold), '--seq-threshold', str(seq_threshold),'--multi_streamer' if multi_streamer else '', '--rx_otw', sc, '--rx_cpu', rx_cpu, '--rx_delay', str(rx_delay)])
    sample = sample.decode()

    benchmark_summary = sample.split('Benchmark rate summary:\n')[1]
    results = benchmark_summary.split('\n')[0:10]

    for result in results:
        result = result.split(':')
        result_entry = result[0].lstrip()
        result_data  = int(result[1])

        print(result_entry, result_data)
        if result_entry == 'Num received samples':
            continue

        try:
            assert result_data == 0
        except:
            print('ERROR with rx_benchmark', result_entry, result_data);
            sys.exit(1)





def tx_benchmark(header='', duration=10, tx_rate=65e6, tx_channels="0,1,2,3", drop_threshold=0, seq_threshold=0, multi_streamer=True, tx_otw=True, sc='sc16', tx_cpu="sc16", tx_delay=5):
    print('\n\n\n')
    print("*****************************\n")
    print('TX', tx_cpu, 'multi-streamer' if multi_streamer else 'single', 'tx_delay='+str(tx_delay),'\n')
    print("*****************************\n\n")

    sample = subprocess.check_output([PATH, '--duration', str(duration), '--tx_rate', str(tx_rate), '--tx_channels', tx_channels, '--drop-threshold', str(drop_threshold), '--seq-threshold', str(seq_threshold),'--multi_streamer' if multi_streamer else '', '--tx_otw', sc, '--tx_cpu', tx_cpu, '--tx_delay', str(tx_delay)])
    sample = sample.decode()

    benchmark_summary = sample.split('Benchmark rate summary:\n')[1]
    results = benchmark_summary.split('\n')[0:10]

    for result in results:
        result = result.split(':')
        result_entry = result[0].lstrip()
        result_data  = int(result[1])

        print(result_entry, result_data)
        if result_entry == 'Num transmitted samples':
            continue

        try:
            assert result_data == 0
        except:
            print('ERROR with rx_benchmark', result_entry, result_data);
            sys.exit(1)

def rx_tx_benchmark(duration=10, tx_rate=21666667, rx_rate=21666667, channels="0,1,2,3", drop_threshold=0, seq_threshold=0, multi_streamer=True, tx_otw=True, sc='sc16', tx_cpu="sc16", rx_cpu='sc16', tx_delay=5, rx_delay=5):
    print('\n\n\n')
    print("*****************************\n")
    print('RX/TX', tx_cpu, 'multi-streamer' if multi_streamer else 'single', 'tx_delay='+str(tx_delay),'rx_delay='+str(rx_delay),'\n')
    print("*****************************\n\n")

    sample = subprocess.check_output([PATH, '--duration', str(duration), '--tx_rate', str(tx_rate), '--rx_rate', str(rx_rate), '--channels', channels, '--drop-threshold', str(drop_threshold), '--seq-threshold', str(seq_threshold),'--multi_streamer' if multi_streamer else '', '--tx_otw', sc, '--tx_cpu', tx_cpu, 'rx-cpu', rx_cpu, '--tx_delay', str(tx_delay), '--rx_delay', str(rx_delay)])
    sample = sample.decode()

    benchmark_summary = sample.split('Benchmark rate summary:\n')[1]
    results = benchmark_summary.split('\n')[0:10]

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
            print('ERROR with tx_rx_benchmark', result_entry, result_data);
            sys.exit(1)


def main():
    tx_benchmark(header='Tx, all channels, sc16')
    tx_benchmark(header='Tx, channel 0, sc16', tx_channels="0")
    tx_benchmark(header='Tx, channel 0&1, sc16', tx_channels="0,1")
    tx_benchmark(header='Tx, all channels, fc32', tx_cpu='fc32')

    rx_benchmark(header='Rx, multi-streamer, sc16, no delay')
    rx_benchmark(header='Rx, multi-streamer, sc16, 5s delay', rx_delay=5)
    rx_benchmark(header='Rx, multi-streamer, fc32, 5s delay', rx_rate=21666667, rx_cpu='fc32', rx_delay=5)
    rx_benchmark(header='Rx, single, fc32, 0s delay', rx_rate=21666667, rx_cpu='fc32', multi_streamer=False)

    rx_tx_benchmark(header="Rx/Tx sc16, single, with delay", multi_streamer=False)
    rx_tx_benchmark(header="Rx/Tx sc16, multi, nodelay", tx_delay=0.5, rx_delay=0)
    rx_tx_benchmark(header="Rx/Tx fc32, single, nodelay", tx_delay=0.5, rx_delay=0, multi_streamer=False, rx_cpu='fc32', tx_cpu="fc32")

main()















