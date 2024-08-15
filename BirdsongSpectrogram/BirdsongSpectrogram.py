#!/usr/bin/env python

"""
BirdsongSpectrogram Copyright (C) 2020 Dr. Ralf Antonius Timmermann

Birdsong Spectrogram as derived from the audio signal. The spectrogram is being
updated as the audio signal is streaming in. The spectrogram's update interval
can be adjusted by hotkeys ctrl-j and ctrl-k. However, the lower limit
is determined by the time needed for MATPLOTLIB to update the spectrogram
(between 0.3 and 0.5 sec). ctrl-x and ctrl-y stop and exit the program,
respectively. ESC to resume. The sample rate, the sample width
(no of samples of each slice) for the FFT, and the overlap of the slices
with each other (no of samples) can be adjusted accordingly.

Fast MATPLOTLIB plotting was deployed by utilizing blitting (no mem leaks
observed here). If the upper subplot was not to be updated, one could reach
update times of 0.18 sec (>5 fps)

The plot comprises two subplots, the upper displaying the streaming
audio signal, whilst the lower displays the birdsong spectrogram between
frequencies from 0 to RATE/2 Hz.

This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import timeit
import time
from pynput import keyboard
from skimage import util
import logging


__author__ = "Dr. Ralf Antonius Timmermann"
__copyright__ = "Copyright (C) Dr. Ralf Antonius Timmermann"
__credits__ = ""
__license__ = "GPLv3"
__version__ = "0.4.0"
__maintainer__ = "Dr. Ralf A. Timmermann"
__email__ = "ralf.timmermann@gmx.de"
__status__ = "Production"

print(__doc__)


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

myformat = "%(asctime)s.%(msecs)03d %(levelname)s:\t%(message)s"
logging.basicConfig(format=myformat,
                    level=logging.INFO,
                    datefmt="%H:%M:%S")
# logging.getLogger().setLevel(logging.DEBUG)


class Birdsong:

    def __init__(self):
        self.record_seconds: float = 1  # lengths of audio signal chunks
        self.visible: bool = True
        self.x: bool = True
        self.q: bool = False

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

    def on_activate_x(self):
        self.x = not self.x
        print("stop/resume with ctrl-x")

    def on_activate_y(self):
        self.x = True
        self.q = True
        print("quitting...")

    def on_activate_k(self):
        self.record_seconds += 0.1
        print("Recording Time: {0:1.1f}s".format(self.record_seconds))

    def on_activate_j(self):
        self.record_seconds -= 0.1
        if self.record_seconds < 0:
            self.record_seconds = 0
        print("Recording Time: {0:1.1f}s".format(self.record_seconds))

    def on_activate_v(self):
        # toggles on/off plot in time domain
        self.visible = not self.visible

    def animate(self) -> None:
        """
        While the stream is active audio output is created and piled up on variable amp such that WIDTH sec
        are filled. The upper subplot displays the audio signal, whilst the lower displays the birdsong spectrogram.
        """
        ln, image, axbackground, ax1background = None, None, None, None
        _firstplot = True
        win = np.hanning(M)
        plt.ion()  # Stop matplotlib windows from blocking
        # Setup figure, axis, lines, text and initiate plot and copy background
        fig = plt.gcf()
        fig.set_size_inches(12, 8)
        # upper subplot
        ax = fig.add_subplot(211)
        # lower subplot
        ax1 = fig.add_subplot(212)

        # start Recording
        self.stream.start_stream()
        amp = []

        while self.stream.is_active():
            # interrupt on hotkey 'ctrl-x' and resume on 'esc'
            if not self.x:
                self.stream.stop_stream()
                while not self.x:
                    time.sleep(.01)
                self.stream.start_stream()
            if self.q:
                self.stream.stop_stream()
                break

            logging.debug('Starting Audio Stream...')
            time.sleep(self.record_seconds)
            # Convert the list of numpy-arrays into a 1D array (column-wise)
            # loop until callback_output is not empty anymore!
            while not self.callback_output:
                pass

            _start = timeit.default_timer()

            chunk = np.hstack(self.callback_output)
            # clear stream and pile up on amp
            self.callback_output = []
            amp = np.hstack((amp, chunk))
            samples = len(amp)
            logging.debug('Number of samples:' + str(samples))
            rest = samples - WIDTH*RATE
            if rest > 0:
                # cut off preceeding rest to result in 5 second windows
                amp = amp[rest:]
                samples = len(amp)
            l = amp.shape[0] / RATE
            # The resulting slices object contains one slice per row.
            slices = util.view_as_windows(amp, window_shape=(M,), step=STEP)
            logging.debug(f'Audio shape: {amp.shape}, Sliced audio shape: {slices.shape}')
            t = np.arange(samples) / RATE
            t = t - max(t)  # offset along x-axis

            # Hanning apodization
            slices = (slices * win).T
            # rfft is faster than fft
            spectrum = np.abs(np.fft.rfft(slices, axis=0)[1:M//2+1])
            sp = np.abs(spectrum)
            sp = 20 * np.log10(sp / np.max(sp))

            _stop = timeit.default_timer()
            logging.debug("time utilized for FFT [s]: " + str(_stop - _start))

            _start = timeit.default_timer()

            # instantiate first plot and copy background
            if _firstplot:
                ln, = ax.plot(t, amp)
                image = ax1.imshow(
                    sp,
                    origin='lower',
                    cmap='viridis',
                    extent=(-l, 0., 0., RATE / 2. / 1000.)
                )
                # set once as do not change
                ax.set_xlim([-WIDTH, 0.])
                ax.set_ylabel('Intensity/arb. units')
                ax1.set_aspect('auto')
                ax1.set_xlim([-WIDTH, 0.])
                ax1.set_xlabel('Time/s')
                ax1.set_ylabel('Frequency/kHz')
                axbackground = fig.canvas.copy_from_bbox(ax.bbox)
                ax1background = fig.canvas.copy_from_bbox(ax1.bbox)
                """
                see also here: https://bastibe.de/2013-05-30-speeding-up-matplotlib.html
                no idea whether this poses still validity
                """
                plt.pause(0.001)
                _firstplot = False
            else:
                # upper subplot
                ln.set_xdata(t)
                ln.set_ydata(amp)
                # lower subplot
                image.set_data(sp)
                image.set_extent((-l, 0., 0., RATE / 2. / 1000.))
                # Rescale the axis so that the data can be seen in the plot
                # if you know the bounds of your data you could just set this once
                # so that the axis don't keep changing
                ax.relim()
                ax.autoscale_view()
                ax1.relim()
                ax1.autoscale_view()
                # restore background
                fig.canvas.restore_region(axbackground)
                fig.canvas.restore_region(ax1background)
                # redraw just the points
                ax.draw_artist(ln)
                ax1.draw_artist(image)
                # fill in the axes rectangle
                fig.canvas.blit(ax.bbox)
                fig.canvas.blit(ax1.bbox)
            ax.set_visible(self.visible)
            fig.canvas.flush_events()

            _stop = timeit.default_timer()
            logging.debug("time utilized for matplotlib [s]: " + str(_stop - _start))


def main():
    a = Birdsong()
    h = keyboard.GlobalHotKeys(
        {
            '<ctrl>+x': a.on_activate_x,
            '<ctrl>+y': a.on_activate_y,
            '<ctrl>+j': a.on_activate_j,
            '<ctrl>+k': a.on_activate_k,
            '<ctrl>+v': a.on_activate_v
        }
    )
    h.start()
    a.animate()
    plt.close('all')

    return 0
