# Live Audio Spectrum Analyzer

A real-time audio spectrum analyzer built in Python that reads from your laptop microphone, computes a Fast Fourier Transform (FFT), and displays the frequency spectrum as a live plot.

Built as a software-first DSP project to explore signal processing concepts before implementing them on hardware.

![Python](https://img.shields.io/badge/Python-3.12-blue) ![NumPy](https://img.shields.io/badge/NumPy-scientific-orange) ![Matplotlib](https://img.shields.io/badge/Matplotlib-visualization-green)

---

## Demo

Speak, whistle, or play music near your microphone and watch the frequency spectrum update in real time.

---

## Filter Validation

Experimentally validated each Butterworth filter's frequency response by sweeping sine waves across the audio spectrum and comparing measured attenuation against theoretical Bode plots. Measured and theoretical responses match to within 1dB across the full frequency range.

![Filter Validation](filter_validation.png)

---

## DSP Concepts Demonstrated

- **Fast Fourier Transform (FFT)** — converts time-domain audio samples into the frequency domain, revealing how much energy exists at each frequency
- **Hanning Window** — applied to each audio chunk before the FFT to reduce spectral leakage caused by the sharp edges of finite-length signals
- **Nyquist Theorem** — the sample rate of 44100 Hz allows accurate representation of frequencies up to 22050 Hz, covering the full range of human hearing
- **Real FFT (rfft)** — since audio is a real-valued signal, only the positive frequency components are computed, halving the output size
- **Log Scale Magnitude** — displayed on a logarithmic Y axis to match how humans perceive loudness and to better visualize low-energy frequency components

---

## How It Works
Audio is captured in chunks of 1024 samples at 44100 Hz. Each chunk is windowed and passed through an FFT, producing 513 frequency bins from 0 Hz to 22050 Hz. The plot displays bins up to 5000 Hz and updates at roughly 30 fps.

The audio callback and plot rendering run on separate threads — the callback only writes FFT data to a shared buffer, while the main thread handles all plot updates. This prevents Tkinter threading conflicts.

---

## Requirements

- Python 3.12+
- numpy
- scipy
- matplotlib
- sounddevice
- PyQt5

Install all dependencies with:

```bash
pip install numpy scipy matplotlib sounddevice PyQt5
```

---

## Usage

```bash
git clone https://github.com/nathantenn/spectrum-analyzer.git
cd spectrum-analyzer
python spectrum_analyzer.py
```

A plot window will open and begin reacting to your microphone input. Close the window to stop.

---

## Configuration

At the top of `spectrum_analyzer.py` you can adjust:

| Parameter | Default | Description |
|---|---|---|
| `SAMPLE_RATE` | 44100 Hz | Audio sample rate |
| `CHUNK_SIZE` | 1024 | Samples per FFT frame — larger = better frequency resolution, slower response |
| `MAX_FREQ` | 5000 Hz | Highest frequency displayed on the plot |

---

## What's Next

- Add a peak frequency display to identify the dominant frequency in real time
- Implement a bandpass filter using `scipy.signal` to isolate specific frequency ranges
- Build a note detector that maps peak frequency to musical notes (guitar tuner)
- Port the FIR filter design to Verilog and implement on an FPGA

---

## Author

**Nathan Ten** — 3rd Year Electrical and Computer Engineering student at UC San Diego, specializing in Circuits and Systems.

[GitHub](https://github.com/nathantenn)
