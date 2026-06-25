import matplotlib
matplotlib.use('QtAgg')

import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd

# --- Configuration ---
SAMPLE_RATE = 44100
CHUNK_SIZE  = 1024
MAX_FREQ    = 5000

# Shared buffer between audio thread and main thread
latest_fft = np.zeros(CHUNK_SIZE // 2 + 1)

# --- Audio callback: ONLY store data, never touch the plot ---
def audio_callback(indata, frames, time, status):
    global latest_fft
    audio = indata[:, 0]
    windowed = audio * np.hanning(len(audio))
    latest_fft = np.abs(np.fft.rfft(windowed))

# --- Set up the plot ---
freqs = np.fft.rfftfreq(CHUNK_SIZE, d=1/SAMPLE_RATE)
mask  = freqs <= MAX_FREQ

fig, ax = plt.subplots()
line, = ax.plot(freqs[mask], np.ones(mask.sum()), color='cyan')
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Magnitude (dB)")
ax.set_title("Live Audio Spectrum Analyzer")
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

# --- Main loop: all plot updates happen here on the main thread ---
print("Listening... Press Ctrl+C to stop.")
with sd.InputStream(callback=audio_callback,
                    channels=1,
                    samplerate=SAMPLE_RATE,
                    blocksize=CHUNK_SIZE):
    while plt.fignum_exists(fig.number):
        # Clamp to minimum of 1 to avoid log(0) errors
        fft_data = np.maximum(latest_fft[mask], 1)
        line.set_ydata(fft_data)
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(0.03)