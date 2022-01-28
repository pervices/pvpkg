from common import sigproc
from common import engine
from common import generator as gen
from retrying import retry
import sys

@retry(stop_max_attempt_number = 3)
def test(it):

    gen.dump(it)

    # Collect.
    tx_stack = [ (10.0, it["sample_rate" ]) ] # One seconds worth.
    rx_stack = [ (10.5, it["sample_count"]) ]
    vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)

    # Process.
    for ch, channel in enumerate(vsnk):

        real = [datum.real for datum in channel.data()]
        imag = [datum.imag for datum in channel.data()]

        lag = sigproc.lag(real, imag, it["sample_rate"], it["wave_freq"])

        print("channel %2d: lag %f" % (ch, lag))

        try:
            assert lag > 0.20 and lag < 0.30 # About PI/4 (90 Degrees)
        except:
            sigproc.dump(vsnk)
            sys.exit(1)
            


def main(iterations):

    for it in iterations:
        test(it)


main(gen.hi_band_wave_sweep())

