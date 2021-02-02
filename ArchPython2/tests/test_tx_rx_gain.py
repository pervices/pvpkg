from common import sigproc
from common import engine
from common import generator as gen

import numpy as np

def main(iterations):

    # Collect.
    vsnks = []
    for it in iterations:
        gen.dump(it)
        tx_stack = [ (10.0, it["sample_rate" ]) ] # One seconds worth.
        rx_stack = [ (10.5, it["sample_count"]) ]
        vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
        vsnks.append(vsnk)

    # Calculate absolute area.
    areas = []
    for vsnk in vsnks:
        area = [sigproc.absolute_area(channel.data()) for channel in vsnk]
        areas.append(area)
    areas = np.array(areas).T.tolist() # Transpose.

    # Assert area is increasing per channel.
    for area in areas:
        print area
        assert area == sorted(area)


main(gen.lo_band_gain_tx(1))
main(gen.lo_band_gain_rx(1))
main(gen.hi_band_gain_tx(1))
main(gen.hi_band_gain_rx(1))

