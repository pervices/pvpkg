from common import sigproc
from common import engine
from common import generator as gen
from retrying import retry
import matplotlib.pyplot as plt
import sys

@retry(stop_max_attempt_number = 3)
def test(it):

    gen.dump(it)

    # Collect.
    # First frame of TX/RX stack is gold standard (sample_count samples in middle of 1 second of TX).
    tx_stack = [ (5.0, it["sample_count" ]), (8.0, it["sample_count"]), (11.0, it["sample_count"]), (14.0, it["sample_count"]) ]
    rx_stack = [ (5.0, it["sample_count"]), (8.0, it["sample_count"]), (11.0, it["sample_count"]), (14.0, it["sample_count"]) ]
    vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)

    # Process.
    # Stacked commands vsnk channel extensions and must be indexed manually with sample_count.
    for ch, channel in enumerate(vsnk):

        print("channel %d" % ch)
        areas = []
        for i, frame in enumerate(rx_stack):
            #print(i)
            #print(frame)

            sample_count = frame[1]
            a = int(i * sample_count)
            b = int(a + sample_count)
            data = channel.data()[a : b]
            data_gold=channel.data()[0:frame[1]]

            area = sigproc.absolute_area(data)
            areas.append(area)

            # Area likeness is relative to gold standard (first stack frame).
            likeness = area / areas[0]

            sigproc.dump_file(vsnk, it["wave_freq"])
            print("\tframe %d: aboslute area: likeness %f" % (i, likeness))

            try:
                assert likeness > 0.5 and likeness < 1.5, "tx_rx_stacked_commands fail comparison"
            except:
                sigproc.dump(vsnk)
                #plotting data in interval and "gold standard"
                plt.figure()
                plt.title("stacked command area plot of channel {} between interval {} and {}".format(it["channels"], a, b))
                plt.plot(data_gold, color='gold', label='gold standard')
                plt.plot(data, label='data')
                plt.legend()
                plt.savefig(fname='stacked commands area plot comparison for channel {} between interval {} and {} at sample rate {}'.format(ch,a, b,it["sample_rate"], format='png'))
                sys.exit(1)

def main(iterations):

    for it in iterations:
        test(it)


main(gen.lo_band_basic())
main(gen.hi_band_basic())
