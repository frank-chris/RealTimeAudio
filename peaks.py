from scipy.signal import find_peaks
import numpy as np


def avg_rr(sr:float, dur:float, x:np.array):
    """
    Function to return the average respiration rate using peak detection
    on the filtered signal

    Args:
        sr: float
            sampling rate

        dur: float
            duration

        x: np.array
            low pass filtered audio signal
    """
    peaks, _ = find_peaks(x)
    
    avg_respiration_rate = 60/dur*len(peaks)

    return avg_respiration_rate
