# RealTimeAudio
Record, process and plot microphone audio in real-time

## Requirements

* [pyaudio](https://people.csail.mit.edu/hubert/pyaudio/)

```
sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev

sudo apt-get install python-dev

sudo apt-get install python3-pyaudio
```

* [scipy](https://scipy.org/)

```
pip install scipy
```

* [matplotlib](https://matplotlib.org/)

```
pip install matplotlib
```

* [numpy](https://numpy.org/)

```
pip install numpy
```

## Usage

```
python3 record.py [OPTIONS] INDEX
```

* **INDEX**   
    INDEX is the index of the input audio device to be used (run `python3 list_devices.py` to get a list of the indices and names of all audio devices with one or more input channels). 
    
* **OPTIONS:**   
    -p, --plot   
        Plot the recorded audio. Default: False   
       
    -d, --dur DURATION   
        DURATION is the number of seconds to be recorded. Default: 20   
       
    -r, --rate RATE   
        RATE is the sampling rate to be used while recording. Default: 16000   
        
---

_Chris Francis (chris.francis@iitgn.ac.in)_  
