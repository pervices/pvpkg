from common import sigproc
from common import engine
from common import generator as gen

import numpy as np

def main(iterations):

    # Collect.
    vsnks = []

    sample_count = 0

    for it in iterations:
        gen.dump(it)
        #Due to a bug that makes start times have no effect, tx will run for 3 seconds, rx will run for 1.5 seconds but only use the last sample_count samples
        sample_count = it["sample_count"]
        tx_stack = [ (10, int(it["sample_rate" ])*3) ]
        rx_stack = [ (10.5, int(it["sample_count"] + (it["sample_rate" ])*1.5)) ]
        vsnk = engine.run(it["channels"], it["wave_freq"], it["sample_rate"], it["center_freq"], it["tx_gain"], it["rx_gain"], tx_stack, rx_stack)
        vsnks.append(vsnk)

    # Calculate absolute area.
    areas = []
    for vsnk in vsnks:
        areas[0:len(vsnk)]
        x = 0
        for channel in vsnk:
            x = x + 1
            #Uses only the list sample_count sample, this should be changed to use all samples (which should be equal to sample_count) once theissues with tx and rx start delays are fixed
            areas[x] = [sigproc.absolute_area(channel.data()[-sample_count:-1])]
        #areas.append(area)
    areas = np.array(areas).T.tolist() # Transpose.

    print(areas)
    # Assert area is increasing per channel.
    for area in areas:
        print(area)
        for x in range (1, len(area)):
            assert area[x] - area[x-1] > 1 #makes sure the difference in area is significant

#Change the argument in the following function to select how many channels to test
main(gen.lo_band_gain_tx(4))
main(gen.lo_band_gain_rx(4))
main(gen.hi_band_gain_tx(4))
main(gen.hi_band_gain_rx(4))

