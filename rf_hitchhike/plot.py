import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import EngFormatter

import rf_hitchhike.sp.fft


def plot_spectrum(freqs: np.ndarray, power: np.ndarray, figsize=(10, 5)):
    f_center = np.mean(freqs)

    plt.figure(figsize=figsize)
    plt.plot(freqs, power, color="C0")
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Power [dB]")
    plt.gca().axvline(x=f_center, color="gray", lw=0.8, ls="--", alpha=0.9)
    plt.grid(linestyle=":")

    fmt = EngFormatter(unit="Hz")
    plt.gca().xaxis.set_major_formatter(fmt)

    plt.tight_layout()


def plot_IQ_spectrum(I: np.ndarray, Q: np.ndarray, fs: int, fast: bool = True):
    if fast:
        freqs, power = rf_hitchhike.sp.fft.quick_IQ_spectrum(I, Q, fs)
    else:
        freqs, power = rf_hitchhike.sp.fft.compute_IQ_spectrum(I, Q, fs)

    plot_spectrum(freqs, power)
