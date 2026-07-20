import matplotlib
matplotlib.use('QtAgg')

import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
from scipy.signal import butter, sosfilt, sosfilt_zi
from matplotlib.widgets import Slider

SAMPLE_RATE = 44100
CHUNK_SIZE  = 1024
MAX_FREQ    = 5000

# --- Design filters ---
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

zi_bass   = sosfilt_zi(sos_bass)
zi_mid    = sosfilt_zi(sos_mid)
zi_treble = sosfilt_zi(sos_treble)

# --- Shared state ---
latest_fft = np.zeros(CHUNK_SIZE // 2 + 1)
gains = {'bass': 1.0, 'mid': 1.0, 'treble': 1.0}

# --- Audio callback ---
def audio_callback(indata, frames, time, status):
    global latest_fft, zi_bass, zi_mid, zi_treble
    audio = indata[:, 0]

    bass,   zi_bass   = sosfilt(sos_bass,   audio, zi=zi_bass)
    mid,    zi_mid    = sosfilt(sos_mid,     audio, zi=zi_mid)
    treble, zi_treble = sosfilt(sos_treble,  audio, zi=zi_treble)

    mixed = (gains['bass']   * bass +
             gains['mid']    * mid  +
             gains['treble'] * treble)

    windowed   = mixed * np.hanning(len(mixed))
    latest_fft = np.abs(np.fft.rfft(windowed))

# --- Set up plot ---
freqs = np.fft.rfftfreq(CHUNK_SIZE, d=1/SAMPLE_RATE)
mask  = freqs <= MAX_FREQ

fig, ax = plt.subplots(figsize=(10, 7))
plt.subplots_adjust(bottom=0.25)  # make room for sliders

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

# --- Sliders ---
ax_bass   = plt.axes([0.15, 0.15, 0.65, 0.03], facecolor='black')
ax_mid    = plt.axes([0.15, 0.10, 0.65, 0.03], facecolor='black')
ax_treble = plt.axes([0.15, 0.05, 0.65, 0.03], facecolor='black')

slider_bass   = Slider(ax_bass,   'Bass',   0.0, 3.0, valinit=1.0, color='cyan')
slider_mid    = Slider(ax_mid,    'Mid',    0.0, 3.0, valinit=1.0, color='magenta')
slider_treble = Slider(ax_treble, 'Treble', 0.0, 3.0, valinit=1.0, color='yellow')

for slider, label in [(slider_bass, 'Bass'), (slider_mid, 'Mid'), (slider_treble, 'Treble')]:
    slider.label.set_color('white')
    slider.valtext.set_color('white')

def update_gains(val):
    gains['bass']   = slider_bass.val
    gains['mid']    = slider_mid.val
    gains['treble'] = slider_treble.val

slider_bass.on_changed(update_gains)
slider_mid.on_changed(update_gains)
slider_treble.on_changed(update_gains)

plt.ion()
plt.show()

# --- Main loop ---
print("Listening... Close the window to stop.")
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
