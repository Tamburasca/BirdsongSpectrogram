#!/usr/bin/env python

"""
Birdsong Spectrogram derived from the computer's internal microphone audio signal. The spectrogram is being
updated as the audio signal is streaming in. The spectrogram's update interval can be adjusted by the page up/down keys.
However, the lower limit is determined by the time needed for matplotlib to update the spectrogram (between 0.3 and
0.5 sec). The hotkeys 'c' and 'y' stop and exit the program, respectively. 'ESC' to resume. The sample rate RATE
(samples/sec), the sample width M (no of samples of each slice) for the FFT, and the overlap of the slices STEP with
each other (no of samples) can be adjusted accordingly. The audio signal is being apodized through a Hanning window
before running the FFT.

Fast MATPLOTLIB plotting was deployed by utilizing blitting (no mem leaks observed here). There's - I am pretty sure -
enough room for making it even near-live. If the upper subplot was not to be updated, one could reach update times of
0.18 sec (>5 fps)

The plot comprises two subplots, the upper displaying the streaming audio signal, whilst the lower displays the
birdsong spectrogram between frequencies from 0 to RATE/2 Hz.

Runs with
python       >=3.6
keyboard     >=0.13.5
PyAudio      >=0.2.11
numpy        >=1.18.1
matplotlib   >=3.2.1
scikit-image >=0.17.2
"""

__author__ = "Dr. Ralf Antonius Timmermann"
__copyright__ = "Copyright (C) Dr. Ralf Antonius Timmermann"
__credits__ = ""
__license__ = "GPLv3"
__version__ = "0.1"
__maintainer__ = "Dr. Ralf A. Timmermann"
__email__ = "rtimmermann@astro.uni-bonn.de"
__status__ = "Development"

import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import timeit
import time
import keyboard
from skimage import util

# do not modify below
FORMAT = pyaudio.paInt16
# mono, not stereo
CHANNELS = 1
# rate Hz, samples / sec
RATE = 44100
# size of slices: samples per FFT
M = 1024
# slices overlapping the previous STEP samples
STEP = 100
# width of plot window in sec
WIDTH = 5

_debug = False


class TunerHarpsichord:

    def __init__(self):
        """
        :param a1: float
            tuning frequency for a1
        :param tuning: string
            tuning temperament
        """
        # lengths of audio signal chunks
        self.record_seconds = 1
        self.rc = None

        self.callback_output = []
        audio = pyaudio.PyAudio()
        self.stream = audio.open(format=FORMAT,
                                 channels=CHANNELS,
                                 rate=RATE,
                                 output=False,
                                 input=True,
                                 stream_callback=self.callback)

    def callback(self, in_data, frame_count, time_info, flag):
        """
        :param in_data:
        :param frame_count:
        :param time_info:
        :param flag:
        :return:
        """
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        self.callback_output.append(audio_data)

        return None, pyaudio.paContinue

    @property
    def animate(self):
        """
        While the stream is active audio output is created and piled up on variable amp such that that WIDTH sec
        are filled. The upper subplot displays the audio signal, whilst the lower displays the birdsong spectrogram.

        :return:
        string
            return code
        """
        win = np.hanning(M + 1)[:-1]
        _firstplot = True
        plt.ion()  # Stop matplotlib windows from blocking

        # start Recording
        self.stream.start_stream()
        amp = []
        while self.stream.is_active():
            # interrupt on hotkey
            if self.rc == 'c':
                self.stream.stop_stream()
                keyboard.wait('esc')
                self.stream.start_stream()
                self.rc = None
            elif self.rc == 'y':
                return 'y'

            print('Starting Audio Stream...')
            time.sleep(self.record_seconds)
            # Convert the list of numpy-arrays into a 1D array (column-wise)
            # loop until callback_output is not not empty any more!
            while not self.callback_output:
                pass

            _start = timeit.default_timer()

            chunk = np.hstack(self.callback_output)
            # clear stream and pile up on amp
            self.callback_output = []
            amp = np.hstack((amp, chunk))
            samples = len(amp)
            #print('Number of samples', samples)
            rest = samples - WIDTH*RATE
            if rest > 0:
                # cut off preceeding rest to result in 5 second windows
                amp = amp[rest:]
                samples = len(amp)
            L = amp.shape[0] / RATE
            # The resulting slices object contains one slice per row.
            slices = util.view_as_windows(amp, window_shape=(M,), step=STEP)
            print(f'Audio shape: {amp.shape}, Sliced audio shape: {slices.shape}')
            t = np.arange(samples) / RATE
            #print(f'Audio length: {L:.2f} seconds')

            # Hanning apodization
            slices = slices * win
            slices = slices.T
            spectrum = np.fft.fft(slices, axis=0)[:M // 2 + 1:-1]
            spectrum = np.abs(spectrum)
            S = np.abs(spectrum)
            S = 20 * np.log10(S / np.max(S))

            _stop = timeit.default_timer()
            if _debug:
                print("time utilized for FFT [s]: " + str(_stop - _start))

            _start = timeit.default_timer()

            # instantiate first plot and copy background
            if _firstplot:
                # Setup figure, axis, lines, text and initiate plot and copy background
                fig = plt.gcf()
                ax = fig.add_subplot(211)
                ax1 = fig.add_subplot(212)
                fig.set_size_inches(12, 8)
                ln, = ax.plot(amp)
                image = ax1.imshow(S, origin='lower', cmap='viridis', extent=(0, L, 0, RATE / 2 / 1000))
                # set once as do not change
                # upper subplot
                ax.set_xlim([0., WIDTH])
                ax.set_ylabel('Intensity/arb. units')
                # lower subplot
                ax1.set_aspect('auto')
                ax1.set_xlim([0., WIDTH])
                ax1.set_xlabel('Time/s')
                ax1.set_ylabel('Frequency/kHz')
                axbackground = fig.canvas.copy_from_bbox(ax.bbox)
                ax1background = fig.canvas.copy_from_bbox(ax1.bbox)
            # upper subplot
            ln.set_xdata(t)
            ln.set_ydata(amp)
            # lower subplot
            image.set_data(S)
            image.set_extent((0, L, 0, RATE / 2 / 1000))
            # Rescale the axis so that the data can be seen in the plot
            # if you know the bounds of your data you could just set this once
            # so that the axis don't keep changing
            ax.relim()
            ax.autoscale_view()
            ax1.relim()
            ax1.autoscale_view()
            if _firstplot:
                fig.canvas.draw()
                _firstplot = False
            else:
                # restore background
                fig.canvas.restore_region(axbackground)
                fig.canvas.restore_region(ax1background)
                # redraw just the points
                ax.draw_artist(ln)
                ax1.draw_artist(image)
                # fill in the axes rectangle
                fig.canvas.blit(ax.bbox)
                fig.canvas.blit(ax1.bbox)
            fig.canvas.flush_events()

            _stop = timeit.default_timer()
            if _debug:
                print("time utilized for matplotlib [s]: " + str(_stop - _start))

        return self.rc

    def on_press(self, key):
        """
        interrupts on a key and set self.rc accordingly
        :param key: string
            interrupt key
        :return:
            None
        """
        if key == 'c':
            print("continue with ESC")
            self.rc = 'c'
        elif key == 'y':
            self.stream.stop_stream()
            print("quitting...")
            self.rc = 'y'
        elif key == 'j':
            self.record_seconds += 0.1
            print("Recording Time: {0:1.1f}s".format(self.record_seconds))
        elif key == 'k':
                self.record_seconds -= 0.1
                if self.record_seconds >= 0:
                    print("Recording Time: {0:1.1f}s".format(self.record_seconds))
                else:
                    print("Recording Time cannot be smaller than zero!".format(self.record_seconds))
                    self.record_seconds = 0

        return None


if __name__ == "__main__":
    a = TunerHarpsichord()
    keyboard.add_hotkey('c', a.on_press, args='c')
    keyboard.add_hotkey('y', a.on_press, args='y')
    keyboard.add_hotkey('page up', a.on_press, args='j')
    keyboard.add_hotkey('page down', a.on_press, args='k')

    a.animate
    plt.close('all')