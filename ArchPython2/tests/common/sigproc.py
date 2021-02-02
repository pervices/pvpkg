import scipy.fftpack
import numpy as np
import sys

from scipy import signal

def dump(vsnk):

    sample_count = xrange(len(vsnk[0].data()))
    channels = xrange(len(vsnk))

    for sample in sample_count:
        for channel in channels:
            datum = vsnk[channel].data()[sample]
            sys.stdout.write("%10.5f %10.5f\t" % (datum.real, datum.imag))
        sys.stdout.write("\n")

    sys.stdout.write("\n")


def fundamental(real_wave, sample_rate):

    N = len(real_wave)
    T = 1.0 / sample_rate
    x  = np.linspace(0.0, N * T, N)
    xf = np.linspace(0.0, 1.0 / (2.0 * T), N / 2)
    yf = 2.0 / N * np.abs(scipy.fftpack.fft(real_wave)[:N // 2])
    indices = np.argwhere(yf > np.max(yf) / 2)

    return np.mean(xf[indices])


def absolute_area(complex_wave):

    return abs(np.trapz(np.absolute(complex_wave)))


def lag(real_wave, imag_wave, sample_rate, wave_freq):

    forewards = np.argmax(signal.correlate(real_wave, imag_wave)) - len(real_wave) + 1
    backwards = np.argmax(signal.correlate(imag_wave, real_wave)) - len(imag_wave) + 1

    lag = (abs(forewards) + abs(backwards)) / 2.0

    return lag / (float(sample_rate) / float(wave_freq))

