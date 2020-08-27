# BIRDSONG SPECTROGRAM

Birdsong Spectrogram as derived from the audio signal with the spectrogram 
constantly being updated as the audio signal is streaming in. The update interval
can be adjusted through hotkeys ctrl-j or ctrl-k. However, the low limit
is determined by MATPLOTLIB to update the spectrogram,
between 0.3 and 0.5 sec. ctrl-x and ctrl-y discontinue and exit the program,
respectively, ESC to resume. The sample rate, the sample width
(no of samples of each slice) for the FFT, and the overlap of the slices
with each other (no of samples) can be adjusted accordingly.

Fast MATPLOTLIB plotting was deployed by utilizing blitting (no memory leaks
were observed).

The plot comprises two subplots, the upper displaying the streaming
audio signal in the time domain, whilst the lower displays the birdsong 
spectrogram between frequencies from 0 to RATE/2 Hz.

On certain Linux distributions, a package named python-tk (or similar) needs 
to be installed, when running in virtual environments.

Run the program with: <em>python3 -m BirdsongSpectrogram</em>

You may want to test current package and enjoy it when listening to 
[link to youtube!](https://www.youtube.com/watch?v=NK2_bcQcoD4)

It'll look similar to this:
![image info](./pictures/BirdsongSpectrogram.png)
