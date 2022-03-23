"""
Chris Francis (chris.francis@iitgn.ac.in)

Record and plot microphone audio in real-time

Usage:

python3 record.py [OPTIONS] INDEX

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
import numpy as np
from matplotlib import pyplot as plt
from optparse import OptionParser
from scipy.io.wavfile import write
from datetime import datetime
from low_pass import butter_lowpass_filter

CHUNKSIZE = 128
CHANNELS = 1
CUTOFF = 0.5
ORDER = 5
FFT_RESOLUTION = 1/6

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
        ax = fig.add_subplot(1, 1, 1)

        line, = ax.plot([])
        line_2, = ax.plot([])
        text = ax.text(0.8, 0.9, "", transform=ax.transAxes)
        ax.set_xlim(0, rate*duration)
        ax.set_ylim(-32800, 32800)

        fig.canvas.draw()   
        background = fig.canvas.copy_from_bbox(ax.bbox)
        plt.show(block=False)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, input_device_index=device_index,channels=CHANNELS, rate=rate, input=True, frames_per_buffer=CHUNKSIZE)

    frames = []
    fft_chunk_size = int(rate / CHUNKSIZE / FFT_RESOLUTION)
    for _ in range(int(rate / CHUNKSIZE * duration)):
        data = stream.read(CHUNKSIZE, exception_on_overflow = False)
        frames.append(np.frombuffer(data, dtype=np.int16))
        
        # amplitude_frame = butter_lowpass_filter(data=np.hstack(frames), cutoff=CUTOFF, fs=rate, order=ORDER)[-int(rate/ FFT_RESOLUTION):]
        

        if plot:
            y = np.hstack(frames)
            x = np.linspace(0, len(y), len(y), endpoint=False)
            line.set_data(x, y)
            y_low_pass = butter_lowpass_filter(data=y, cutoff=CUTOFF, fs=rate, order=ORDER)
            line_2.set_data(x, y_low_pass)
            amplitude_frame = y_low_pass[-int(rate/ FFT_RESOLUTION):]
            fft_out = np.fft.fft(amplitude_frame)
            major_peak = abs(np.fft.fftfreq(int(rate/ FFT_RESOLUTION), d=1/rate)[np.argmax(abs(fft_out))])
            text.set_text("Major peak: " + str(major_peak) + " Hz")
            
            fig.canvas.restore_region(background)
            ax.draw_artist(line)
            ax.draw_artist(line_2)
            ax.draw_artist(text)
            fig.canvas.blit(ax.bbox)
            fig.canvas.flush_events()

    recorded_audio = np.hstack(frames)
    print("\n", len(recorded_audio), "samples recorded")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # save as a wav file
    write(str(datetime.now()).replace(" ", "_") + ".wav", rate, recorded_audio)


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
