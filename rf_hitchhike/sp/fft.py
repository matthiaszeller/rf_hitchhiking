import numpy as np
from numpy.typing import NDArray

from .resample import downsample
from .shift import shift_IQ_frequency


def compute_IQ_spectrum(I: NDArray, Q: NDArray, fs: float) -> tuple[NDArray, NDArray]:
    """
    Compute the power spectrum of a complex baseband (I/Q) signal.

    Parameters
    ----------
    I, Q : NDArray
        Real-valued in-phase and quadrature components of the signal.
    fs : float
        Sampling frequency in Hz.

    Returns
    -------
    freqs : NDArray
        Frequency axis in Hz, centered at 0.
    power : NDArray
        Power spectral density in dB.
    """
    if I.ndim != 1 or Q.ndim != 1:
        raise ValueError("I and Q must be 1D arrays")
    if I.shape != Q.shape:
        raise ValueError("I and Q must have the same shape")

    x = I + 1j * Q
    n = len(x)
    freqs = np.fft.fftshift(np.fft.fftfreq(n, 1 / fs))
    fft = np.fft.fftshift(np.fft.fft(x))

    power = 10 * np.log10(np.abs(fft) ** 2 + 1e-12)

    return freqs, power


def quick_IQ_spectrum(
    I: NDArray,
    Q: NDArray,
    fs: float,
    target_points: int = 2_000_000,
    f_offset: float = 0.0,
) -> tuple[NDArray, NDArray]:
    """
    Quickly estimate the spectrum of an I/Q signal by optional frequency shift
    and automatic decimation.

    Parameters
    ----------
    I, Q : NDArray
        Real-valued in-phase and quadrature components of the input signal.
    fs : float
        Sampling frequency in Hz.
    target_points : int, optional
        Target number of samples after decimation for manageable FFT size.
    f_offset : float, optional
        Frequency offset in Hz to mix before computing the spectrum.

    Returns
    -------
    freqs : NDArray
        Frequency axis in Hz after resampling, centered at 0.
    power : NDArray
        Power spectrum in dB.
    """
    if f_offset != 0.0:
        I, Q = shift_IQ_frequency(I, Q, fs, f_offset)

    n = len(I)
    factor = max(1, int(np.ceil(n / target_points)))
    if factor > 1:
        I = downsample(I, factor, method="auto")
        Q = downsample(Q, factor, method="auto")
        fs = fs / factor

    return compute_IQ_spectrum(I, Q, fs)
