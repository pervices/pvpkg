from common import sigproc
from common import engine
from common import generator as gen
from retrying import retry

#@retry(stop_max_attempt_number = 3)
def test(it):

    gen.dump(it)

    # Collect.
    tx_stack = [ (10.0, it["sample_rate" ]) ] # One seconds worth.
    rx_stack = [ (10.5, it["sample_count"]) ]
    vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)

    # Process.
    reals = []
    imags = []
    for ch, channel in enumerate(vsnk):

        real = [datum.real for datum in channel.data()]
        imag = [datum.imag for datum in channel.data()]

        reals.append(real)
        imags.append(imag)

        real_coherency = sigproc.lag(real, reals[0], it["sample_rate"], it["wave_freq"])
        imag_coherency = sigproc.lag(imag, imags[0], it["sample_rate"], it["wave_freq"])

        print("channel %2d: real coherency %f" % (ch, real_coherency))
        print("channel %2d: imag coherency %f" % (ch, imag_coherency))

        thresh = 0.05

        try:
            assert \
                real_coherency > -thresh and real_coherency < thresh and \
                imag_coherency > -thresh and imag_coherency < thresh
        except:
            sigproc.dump(vsnk)
            raise


def main(iterations):

    for it in iterations:
        test(it)


main(gen.lo_band_wave_sweep())
main(gen.hi_band_wave_sweep())

