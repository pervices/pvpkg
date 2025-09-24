from common import engine
from common import generator as gen

tx_burst = 5.0 #burst should be slightly delayed to ensure all data is being collected
rx_burst = 5.25

def main():
    iterations = gen.lo_band_phaseCoherency()
    channel_list = [i for i in range(4)]
    
    for it in iterations:
        gen.dump(it)
        sample_rate = int(it["sample_rate"])
        tx_stack = [ (tx_burst , sample_rate)]
        rx_stack = [ (rx_burst, int(it["sample_count"]))]

        vsnk = engine.run(channel_list, it["wave_freq"], sample_rate, it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)

        for v in vsnk:
            print(v.data())
if __name__ == '__main__':
    main()