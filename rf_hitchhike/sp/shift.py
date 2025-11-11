import numpy as np
from numpy.typing import NDArray

from .resample import downsample


def shift_IQ_frequency(
    I: NDArray, Q: NDArray, fs: float, f_offset: float
) -> tuple[NDArray, NDArray]:
    """
    Frequency-shift a complex baseband signal by a specified offset.

    Parameters
    ----------
    I, Q : NDArray
        Real-valued in-phase and quadrature components of equal length.
    fs : float
        Sampling frequency in Hz.
    f_offset : float
        Frequency offset in Hz. Positive values shift the spectrum downward
        (toward baseband), negative values upward.

    Returns
    -------
    I_shifted, Q_shifted : tuple of NDArray
        The frequency-shifted in-phase and quadrature components.
    """
    x = I + 1j * Q
    t = np.arange(len(x)) / fs
    x_shifted = x * np.exp(-1j * 2 * np.pi * f_offset * t)

    return np.real(x_shifted), np.imag(x_shifted)


def extract_IQ_subband(
    I: NDArray, Q: NDArray, fs: float, fc: float, f_target: float, new_bw: float
) -> tuple[NDArray, NDArray, float]:
    """
    Extract and downsample a sub-band centered on ``f_target`` from a recording centered on ``fc``.

    Parameters
    ----------
    I, Q : NDArray
        Real-valued in-phase and quadrature components of the input signal.
    fs : float
        Original sampling frequency in Hz.
    fc : float
        Center frequency of the original recording in Hz.
    f_target : float
        Absolute center frequency of the desired sub-band in Hz.
    new_bw : float
        Desired bandwidth of the sub-band in Hz (half the final sampling rate).

    Returns
    -------
    I_sub, Q_sub : NDArray
        Downsampled I and Q components corresponding to the extracted sub-band.
    fs_sub : float
        New sampling frequency in Hz after decimation.
    """
    f_offset = f_target - fc
    I, Q = shift_IQ_frequency(I, Q, fs, f_offset)
    factor = int(fs / (2 * new_bw))
    I = downsample(I, factor)
    Q = downsample(Q, factor)
    fs = fs / factor

    return I, Q, fs
