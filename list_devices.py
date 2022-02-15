"""
Chris Francis (chris.francis@iitgn.ac.in)

List all audio devices that support 1 or more input channels

Usage:

python3 list_devices.py
"""

import pyaudio


def list_devices():
    """
    Function to print the index and name of all audio 
    devices that support 1 or more input channels

    Args: None
    Returns: None
    """
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get("deviceCount")
    print("\nFound", numdevices, "devices. The following have one or more input channels:\n")
    for i in range(numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get("maxInputChannels")) > 0:
            print("Input Device Index", i, "-", p.get_device_info_by_host_api_device_index(0, i).get("name"))

if __name__ == "__main__":
    """
    Main function
    """
    list_devices()