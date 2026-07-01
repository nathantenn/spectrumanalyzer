import matplotlib
matplotlib.use('QtAgg')

import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd

SAMPLE_RATE = 44100
CHUNK_SIZE  = 4096  # Larger chunk for better frequency resolution
DURATION    = 3     # seconds to record

print(f"Recording {DURATION} seconds of audio for noise analysis...")
print("Stay quiet for the first half, then make a steady tone (whistle/hum) for the second half.")

# --- Record audio ---
audio = sd.rec(int(DURATION * SAMPLE_RATE),
               samplerate=SAMPLE_RATE,
               channels=1,
               dtype='float32')
sd.wait()
audio = audio[:, 0]
print("Recording done.")

# --- Split into noise and signal sections ---
mid = len(audio) // 2
noise_segment  = audio[:mid]   # first half — quiet
signal_segment = audio[mid:]   # second half — your tone

# --- Compute power spectral density for each ---
def compute_psd(segment, chunk_size):
    # Average FFT magnitude over multiple chunks for a stable estimate
    num_chunks = len(segment) // chunk_size
    psds = []
    for i in range(num_chunks):
        chunk = segment[i*chunk_size:(i+1)*chunk_size]
        windowed = chunk * np.hanning(len(chunk))
        fft_mag = np.abs(np.fft.rfft(windowed)) / chunk_size
        psds.append(fft_mag**2)
    return np.mean(psds, axis=0)

freqs = np.fft.rfftfreq(CHUNK_SIZE, d=1/SAMPLE_RATE)
noise_psd  = compute_psd(noise_segment,  CHUNK_SIZE)
signal_psd = compute_psd(signal_segment, CHUNK_SIZE)

# --- Find signal peak and noise floor ---
peak_idx   = np.argmax(signal_psd)
peak_freq  = freqs[peak_idx]
peak_power = signal_psd[peak_idx]

# Noise floor: median power away from the signal peak
mask = np.ones(len(freqs), dtype=bool)
mask[max(0, peak_idx-10):peak_idx+10] = False  # exclude peak region
noise_floor = np.median(signal_psd[mask])

# --- Calculate SNR ---
snr_db = 10 * np.log10(peak_power / (noise_floor + 1e-10))

print(f"\nPeak frequency : {peak_freq:.1f} Hz")
print(f"Noise floor    : {10 * np.log10(noise_floor + 1e-10):.1f} dBFS")
print(f"SNR            : {snr_db:.1f} dB")

# --- Plot ---
fig, axes = plt.subplots(2, 1, figsize=(11, 8))

for ax, psd, title in [
    (axes[0], noise_psd,  'Noise Floor (quiet recording)'),
    (axes[1], signal_psd, f'Signal + Noise (tone at {peak_freq:.1f} Hz) — SNR: {snr_db:.1f} dB'),
]:
    psd_db = 10 * np.log10(np.maximum(psd, 1e-10))
    ax.plot(freqs, psd_db, color='cyan', linewidth=0.8)
    ax.axhline(10 * np.log10(noise_floor + 1e-10), color='yellow',
               linestyle='--', linewidth=1, label='Noise floor')
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Power (dBFS)')
    ax.set_title(title)
    ax.set_xlim(0, 8000)
    ax.set_facecolor('black')
    fig.patch.set_facecolor('black')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    ax.legend(facecolor='black', labelcolor='white')
    ax.grid(True, color='gray', alpha=0.3)

plt.tight_layout()
plt.savefig('noise_analysis.png', facecolor='black', bbox_inches='tight', dpi=150)
plt.show()
print("Plot saved to noise_analysis.png")