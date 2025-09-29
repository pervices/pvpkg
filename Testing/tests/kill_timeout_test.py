from common import engine
from common import generator as gen
import time
import cProfile

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

        # profile_cmd = """engine.run(channel_list, it["wave_freq"], sample_rate, it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)"""
        # cProfile.runctx(profile_cmd, globals=globals(), locals=locals(), sort='cumtime')

        start_time = time.clock_gettime(time.CLOCK_MONOTONIC)
        vsnk = engine.run(channel_list, it["wave_freq"], sample_rate, it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
        end_time = time.clock_gettime(time.CLOCK_MONOTONIC)
        print("[DEBUG] Time for engine run: ", (end_time-start_time))
        for v in vsnk:
            print(v.data())
if __name__ == '__main__':
    main()