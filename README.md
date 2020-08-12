# BIRDSONG SPECTROGRAM

Birdsong Spectrogram as derived from the audio signal. The spectrogram is being
updated as the audio signal is streaming in. The spectrogram's update interval
can be adjusted by hotkeys ctrl-j and ctrl-k. However, the lower limit
is determined by the time needed for MATPLOTLIB to update the spectrogram
(between 0.3 and 0.5 sec). ctrl-x and ctrl-y stop and exit the program,
respectively. ESC to resume. The sample rate, the sample width
(no of samples of each slice) for the FFT, and the overlap of the slices
with each other (no of samples) can be adjusted accordingly.

Fast MATPLOTLIB plotting was deployed by utilizing blitting (no mem leaks
observed here). 

The plot comprises two subplots, the upper displaying the streaming
audio signal, whilst the lower displays the birdsong spectrogram between
frequencies from 0 to RATE/2 Hz.

On UNIX OS please consider to run the package with sudo rights, owing to the particular requirement of the keyboard
module: sudo python3 -m BirdsongSpectrogram

You may want to test and enjoy it with 
[link to youtube!](https://www.youtube.com/watch?v=NK2_bcQcoD4)

It'll look like this:
![image info](./pictures/BirdsongSpectrogram.png)
