"""
Chris Francis (chris.francis@iitgn.ac.in)

Record and plot microphone audio in real-time

Usage:

python3 pc_rec.py [OPTIONS] INDEX

* INDEX
    INDEX is the index of the input audio device to be used. 

* OPTIONS:
    -p, --plot
        Plot the recorded audio. Default: False
    
    -d, --dur DURATION
        DURATION is the number of seconds to be recorded. Default: 20
    
    -r, --rate RATE
        RATE is the sampling rate to be used while recording. Default: 1000
"""

import pyaudio
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from optparse import OptionParser
from scipy.io.wavfile import write
from datetime import datetime
from low_pass import butter_lowpass_filter
from peaks import avg_rr

CHUNKSIZE = 128
CHANNELS = 1
CUTOFF = 0.5
ORDER = 5
FFT_RESOLUTION = 1/16

def record(device_index:int, rate:int = 1000, duration:int = 20, plot:bool = False):
    """
    Function to record and plot microphone audio in real-time

    Args:
        device_index: int
            index of the input audio device to be used

        rate: int, default: 1000
            sampling rate to be used while recording
        
        duration: int, default: 20
            number of seconds to be recorded

        plot: bool, default: False
            whether to plot the recorded audio

    Returns:
        None
    """
    if plot:
        fig = plt.figure(figsize=(21, 9), dpi=80)
        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)

        line_1, = ax1.plot([])
        line_2, = ax2.plot([], color='r')
        text = ax2.text(0.8, 0.9, "", transform=ax2.transAxes)
        ax1.set_xlim(0, rate*duration)
        ax1.set_ylim(-35000, 35000)
        ax1.set_title("Recorded Audio", loc="left")
        ax2.set_xlim(0, rate*duration)
        ax2.set_ylim(-12000, 12000)
        ax2.set_title("Filtered Audio", loc="left")
        ax2.set_xlabel("Sample")

        fig.canvas.draw()
        background1 = fig.canvas.copy_from_bbox(ax1.bbox)
        background2 = fig.canvas.copy_from_bbox(ax2.bbox)
        plt.show(block=False)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, input_device_index=device_index,channels=CHANNELS, rate=rate, input=True, frames_per_buffer=CHUNKSIZE)

    frames = []
    peaks = []
    for _ in range(int(rate / CHUNKSIZE * duration)):
        data = stream.read(CHUNKSIZE, exception_on_overflow = False)
        frames.append(np.frombuffer(data, dtype=np.int16))
                

        if plot:
            y = np.hstack(frames)
            x = np.linspace(0, len(y), len(y), endpoint=False)
            line_1.set_data(x, y)
            y_low_pass = butter_lowpass_filter(data=y, cutoff=CUTOFF, fs=rate, order=ORDER)
            line_2.set_data(x, y_low_pass)
            amplitude_frame = y_low_pass[-int(rate/ FFT_RESOLUTION):]
            fft_out = np.fft.fft(amplitude_frame)
            major_peak = round(abs(np.fft.fftfreq(int(rate/ FFT_RESOLUTION), d=1/rate)[np.argmax(abs(fft_out))]), 4)
            text.set_text("Major peak: " + str(major_peak) + " Hz, " + str(60*major_peak) + " b.p.m")
            peaks.append(major_peak)
            
            fig.canvas.restore_region(background1)
            fig.canvas.restore_region(background2)
            ax1.draw_artist(line_1)
            ax2.draw_artist(line_2)
            ax2.draw_artist(text)
            fig.canvas.blit(ax1.bbox)
            fig.canvas.blit(ax2.bbox)
            fig.canvas.flush_events()

    recorded_audio = np.hstack(frames)
    print("\n", len(recorded_audio), "samples recorded")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # save files
    dir_name = str(datetime.now()).replace(" ", "_")
    os.mkdir(dir_name)
    write(os.path.join(dir_name, "recorded_audio.wav"), rate, recorded_audio)
    filtered_audio = butter_lowpass_filter(data=recorded_audio, cutoff=CUTOFF, fs=rate, order=ORDER)
    write(os.path.join(dir_name, "filtered_audio.wav"), rate, filtered_audio)
    rr = pd.DataFrame({"rr": [60*peak for peak in peaks]})
    rr.to_csv(os.path.join(dir_name, "rr.csv"), index=False)
    avg_rr_gt = avg_rr(rate, duration, filtered_audio)
    with open(os.path.join(dir_name, "gt.txt"), 'w') as f:
        f.write(str(avg_rr_gt))


if __name__ == "__main__":
    """
    Main function
    """
    parser = OptionParser()

    parser.add_option("-p", "--plot", action="store_true", dest="plot", 
	help="Plot recorded audio. Default: %default",
	default=False)

    parser.add_option("-d", "--dur", dest="dur", type='int', 
	help="Number of seconds to be recorded. Default: %default", default=20)

    parser.add_option("-r", "--rate", dest="rate", type='int', 
	help="Sampling rate to be used while recording. Default: %default", default=1000)

    (options, args) = parser.parse_args()
    
    try:
        assert(len(args) == 1)
    except:
        print("Input device index not provided.")
        exit()

    record(int(args[0]), options.rate, options.dur, options.plot)
