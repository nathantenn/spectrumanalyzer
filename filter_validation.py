import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, sosfilt, sosfreqz

SAMPLE_RATE = 44100
NYQUIST     = SAMPLE_RATE / 2
DURATION    = 0.1  # seconds of sine wave per frequency point

# --- Design filters ---
def make_sos(btype, cutoffs, order=4):
    if isinstance(cutoffs, list):
        cutoffs = [c / NYQUIST for c in cutoffs]
    else:
        cutoffs = cutoffs / NYQUIST
    return butter(order, cutoffs, btype=btype, output='sos')

sos_bass   = make_sos('low',  300)
sos_mid    = make_sos('band', [300, 3000])
sos_treble = make_sos('high', 3000)

filters = [
    (sos_bass,   'Bass (0-300Hz)',   'cyan'),
    (sos_mid,    'Mid (300-3000Hz)', 'magenta'),
    (sos_treble, 'Treble (3000Hz+)', 'yellow'),
]

# --- Frequency sweep ---
test_freqs = np.logspace(np.log10(20), np.log10(20000), 200)
t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)

fig, ax = plt.subplots(figsize=(11, 6))

for sos, label, color in filters:
    # --- Theoretical Bode plot ---
    w, h = sosfreqz(sos, worN=8000, fs=SAMPLE_RATE)
    theoretical_db = 20 * np.log10(np.maximum(np.abs(h), 1e-10))
    ax.plot(w, theoretical_db, color=color, linestyle='--',
            linewidth=1.5, alpha=0.6, label=f'{label} (theoretical)')

    # --- Experimental sweep ---
    measured_db = []
    for freq in test_freqs:
        if freq >= NYQUIST:
            measured_db.append(-80)
            continue
        sine = np.sin(2 * np.pi * freq * t)
        filtered = sosfilt(sos, sine)
        # Measure RMS of output, skip first 20% to ignore transient
        start = int(len(filtered) * 0.2)
        rms_in  = np.sqrt(np.mean(sine[start:]**2))
        rms_out = np.sqrt(np.mean(filtered[start:]**2))
        ratio = rms_out / (rms_in + 1e-10)
        measured_db.append(20 * np.log10(np.maximum(ratio, 1e-10)))

    ax.plot(test_freqs, measured_db, color=color, linewidth=2,
            label=f'{label} (measured)')

# --- Formatting ---
ax.axhline(-3, color='white', linestyle=':', linewidth=0.8, label='-3dB point')
ax.set_xscale('log')
ax.set_xlim(20, 20000)
ax.set_ylim(-80, 5)
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Magnitude (dB)')
ax.set_title('Filter Validation — Measured vs Theoretical Bode Plot')
ax.set_facecolor('black')
fig.patch.set_facecolor('black')
ax.tick_params(colors='white')
ax.xaxis.label.set_color('white')
ax.yaxis.label.set_color('white')
ax.title.set_color('white')
ax.legend(facecolor='black', labelcolor='white', fontsize=8)
ax.grid(True, color='gray', alpha=0.3)
plt.tight_layout()
plt.show()

plt.savefig('filter_validation.png', facecolor='black', bbox_inches='tight', dpi=150)
print("Plot saved to filter_validation.png")