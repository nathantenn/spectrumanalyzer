import matplotlib
matplotlib.use('QtAgg')

import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
from scipy.signal import butter, sosfilt, sosfilt_zi

SAMPLE_RATE = 44100
CHUNK_SIZE  = 1024
MAX_FREQ    = 5000

# --- Filter gains (start equal) ---
BASS_GAIN   = 1.0
MID_GAIN    = 1.0
TREBLE_GAIN = 1.0

# --- Design filters (use second-order sections for stability) ---
def make_sos(btype, cutoffs, order=4):
    nyquist = SAMPLE_RATE / 2
    if isinstance(cutoffs, list):
        cutoffs = [c / nyquist for c in cutoffs]
    else:
        cutoffs = cutoffs / nyquist
    return butter(order, cutoffs, btype=btype, output='sos')

sos_bass   = make_sos('low',  300)
sos_mid    = make_sos('band', [300, 3000])
sos_treble = make_sos('high', 3000)

# --- Initialize filter states (preserves continuity between chunks) ---
zi_bass   = sosfilt_zi(sos_bass)
zi_mid    = sosfilt_zi(sos_mid)
zi_treble = sosfilt_zi(sos_treble)

# --- Shared buffer ---
latest_fft = np.zeros(CHUNK_SIZE // 2 + 1)

# --- Audio callback ---
def audio_callback(indata, frames, time, status):
    global latest_fft, zi_bass, zi_mid, zi_treble
    audio = indata[:, 0]

    # Apply each filter and scale by gain
    bass,   zi_bass   = sosfilt(sos_bass,   audio, zi=zi_bass)
    mid,    zi_mid    = sosfilt(sos_mid,     audio, zi=zi_mid)
    treble, zi_treble = sosfilt(sos_treble,  audio, zi=zi_treble)

    # Mix the bands together
    mixed = (BASS_GAIN * bass) + (MID_GAIN * mid) + (TREBLE_GAIN * treble)

    # FFT of the mixed output
    windowed   = mixed * np.hanning(len(mixed))
    latest_fft = np.abs(np.fft.rfft(windowed))

# --- Set up plot ---
freqs = np.fft.rfftfreq(CHUNK_SIZE, d=1/SAMPLE_RATE)
mask  = freqs <= MAX_FREQ

fig, ax = plt.subplots()
line, = ax.plot(freqs[mask], np.ones(mask.sum()), color='cyan')
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Magnitude (dB)')
ax.set_title('Live Audio Equalizer')
ax.set_yscale('log')
ax.set_ylim(1, 10000)
ax.set_facecolor('black')
fig.patch.set_facecolor('black')
ax.tick_params(colors='white')
ax.xaxis.label.set_color('white')
ax.yaxis.label.set_color('white')
ax.title.set_color('white')
plt.ion()
plt.show()

# --- Main loop ---
print("Listening... Press Ctrl+C to stop.")
with sd.InputStream(callback=audio_callback,
                    channels=1,
                    samplerate=SAMPLE_RATE,
                    blocksize=CHUNK_SIZE):
    while plt.fignum_exists(fig.number):
        fft_data = np.maximum(latest_fft[mask], 1)
        line.set_ydata(fft_data)
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(0.03)