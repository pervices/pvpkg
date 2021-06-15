import os
from common import sigproc
from common import engine
from common import generator as gen
from retrying import retry
import numpy as np

@retry(stop_max_attempt_number = 3)
def test(it):
    gen.dump(it)


    tx_stack = [ (10.0, it["sample_rate" ]) ] # One seconds worth.
    rx_stack = [ (10.5, it["sample_count"]) ]
    vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)

    for ch, channel in enumerate(vsnk):
        real = [datum.real for datum in channel.data()]
        imag = [datum.imag for datum in channel.data()]

        fund_real = sigproc.fundamental(real, it["sample_rate"])
        fund_imag = sigproc.fundamental(imag, it["sample_rate"])

        like_real = float(it["wave_freq"]) / fund_real
        like_imag = float(it["wave_freq"]) / fund_imag

        print("channel %2d: real %10.0f Hz (%8.5f) :: imag %10.0f Hz (%8.5f)" % (ch, fund_real, like_real, fund_imag, like_imag))

    #Uncomment this when you want to see all real and imag results
        #sigproc.dump_file(vsnk, it["wave_freq"])

        try:
            assert (like_real > 0.95 and like_real < 1.05 and like_imag > 0.95 and like_imag < 1.05), "like_real and like_imag do not meet requirements, fail"
        except:
            sigproc.dump(vsnk)
            raise


def main(iterations):

    for it in iterations:
        test(it)


main(gen.hi_band_wave_sweep())

