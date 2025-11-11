from typing import Literal

from numpy.typing import NDArray
from scipy import signal as sps


def decimate(x: NDArray, factor: int) -> NDArray:
    """
    Downsample a real or complex signal by an integer factor using FIR filtering.

    Parameters
    ----------
    x : NDArray
        Input signal.
    factor : int
        Decimation factor (integer > 1).

    Returns
    -------
    y : NDArray
        Downsampled signal after low-pass anti-aliasing filter.
    """
    return sps.decimate(x, factor, ftype="fir", zero_phase=True)


def multistage_decimate(x: NDArray, factor: int, max_stage: int = 8) -> NDArray:
    """
    Perform cascaded FIR decimation in multiple stages for large overall factors.

    Parameters
    ----------
    x : NDArray
        Input signal.
    factor : int
        Total desired decimation factor.
    max_stage : int, optional
        Maximum factor per stage. Defaults to 8.

    Returns
    -------
    y : NDArray
        Downsampled signal after multistage decimation.
    """
    remaining = factor
    y = x
    while remaining > 1:
        stage = min(remaining, max_stage)
        y = decimate(y, stage)
        remaining //= stage

    return y


def downsample(
    x: NDArray,
    factor: int,
    method: Literal["auto", "poly", "decimate", "multi"] = "auto",
    max_factor: int = 8,
) -> NDArray:
    """
    Downsample a signal using one of several methods.

    Parameters
    ----------
    x : NDArray
        Input signal.
    factor : int
        Total decimation factor.
    method : {'auto', 'poly', 'decimate', 'multi'}, optional
        Resampling strategy:
        - 'auto' : choose 'poly' for large factors, 'decimate' otherwise.
        - 'poly' : use polyphase FIR resampling.
        - 'decimate' : use single-stage FIR decimation.
        - 'multi' : perform cascaded FIR decimation.
    max_factor : int, optional
        Threshold factor above which 'poly' is selected in 'auto' mode.

    Returns
    -------
    y : NDArray
        Downsampled signal.
    """
    if method == "auto":
        method = "poly" if factor > max_factor else "decimate"

    match method:
        case "poly":
            y = sps.resample_poly(x, up=1, down=factor)
        case "multi":
            y = multistage_decimate(x, factor, max_stage=max_factor)
        case _:
            y = decimate(x, factor)

    return y
