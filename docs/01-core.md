# 🛰️ RTL-SDR Exploration

## 🧩 Terminology Quick Reference

| Term             | Meaning                                                                                        |
|------------------|------------------------------------------------------------------------------------------------|
| **I/Q samples**  | Complex-valued samples representing amplitude and phase of RF signal. Basis of SDR processing. |
| **Demodulation** | Converting modulated RF signals (AM/FM/FSK/etc.) into baseband audio or data.                  |
| **Baseband**     | Signal shifted down to near 0 Hz for digital processing.                                       |
| **Tuner**        | Analog front-end (e.g., R820T2) selecting the frequency band and converting to IF.             |
| **ADC**          | Analog-to-digital converter sampling the IF signal (part of RTL2832U).                         |
| **Gain**         | RF amplification level; affects sensitivity and noise floor.                                   |
| **Waterfall**    | Time-frequency visualization showing signal power vs. time.                                    |
| **Bias-tee**     | Circuit that injects DC voltage on the antenna line to power active devices (like LNAs).       |
| **Sample rate**  | Number of I/Q samples per second (defines bandwidth).                                          |
| **Bandwidth**    | Portion of spectrum captured; ≈ sample rate of the SDR.                                        |
| **SNR**          | Signal-to-Noise Ratio; measure of signal quality.                                              |

These concepts form the conceptual backbone of SDR operation.


## 🧠 DSP Fundamentals (Quick Reference)

- **Demodulation:** extracting the baseband (audio or digital) signal from the I/Q stream.
- **Filtering:** isolating specific frequency ranges or rejecting interference.
- **Decimation:** lowering sample rate after filtering to save computation.
- **FFT / Spectrum display:** transforming I/Q data into frequency-domain power estimates.
- **Decoding:** interpreting the demodulated data (e.g., audio, telemetry, digital packets).

GNU Radio and similar frameworks let you build these stages graphically or in code.


## Hardware Setup

This document summarizes the components and antennas included in your **radio frequency exploration kit** based on the **Nooelec NESDR SMArt v5**, along with the **LaNA Low Noise Amplifier** and **Flamingo+ FM Bandstop Filter**.
Together, these components allow you to explore, analyze, and decode a wide range of RF signals from **100 kHz to 1.75 GHz**.

### 📦 Components Overview

| Component                                   | Type                                      | Frequency Range           | Purpose / Function                                                                        | Notable Features                                                                                                            |
|---------------------------------------------|-------------------------------------------|---------------------------|-------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| **Nooelec NESDR SMArt v5**                  | RTL-SDR (Software Defined Radio Receiver) | 100 kHz – 1.75 GHz        | Core receiver that digitizes RF signals into I/Q data for demodulation and visualization. | R820T2 tuner; RTL2832U demodulator; 0.5 PPM TCXO; Aluminum case for shielding; SMA connector; USB powered.                  |
| **Nooelec LaNA**                            | Low-Noise Amplifier (LNA)                 | 20 MHz – 4 GHz            | Amplifies weak signals before they reach the SDR, improving signal-to-noise ratio (SNR).  | Very low noise figure; Internal EMI shielding; ESD protection; Multiple power options (bias-tee, USB, DC); Gain ≈ 20–25 dB. |
| **Nooelec Flamingo+ FM Bandstop Filter v2** | FM Notch Filter                           | 88 – 108 MHz (attenuated) | Rejects strong FM broadcast signals to prevent overload and intermodulation.              | > 60–70 dB attenuation in FM band; Passes DC bias; Minimal loss outside FM (< 0.25 dB).                                     |


### 📡 Included Antennas (3 total)

| Antenna                        | Type / Design         | Nominal Frequency                                  | Typical Use                                                | Notes & Features                                                                                                    |
|--------------------------------|-----------------------|----------------------------------------------------|------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| **Telescopic Whip Antenna**    | Adjustable monopole   | Variable (~20 MHz – 1 GHz)                         | General-purpose broadband reception.                       | Length-adjustable; optimal when ≈ ¼ wavelength of target frequency; best for wideband scanning and experimentation. |
| **433 MHz Antenna (ISM Band)** | Fixed-length monopole | ~433 MHz                                           | ISM applications (remote sensors, LoRa, wireless devices). | Tuned for 433 MHz; efficient and resonant; good for narrowband IoT signals.                                         |
| **UHF Antenna**                | Fixed-length monopole | ~400–900 MHz (typically centered near 800–900 MHz) | Public safety, GSM, TETRA, general UHF reception.          | Compact, optimized for upper UHF band.                                                                              |


### ⚙️ Recommended Signal Chain Setup

To minimize interference and maximize sensitivity:

```
Antenna → Flamingo+ FM Filter → LaNA (LNA) → NESDR SMArt v5 → USB (Computer)
```

- **Filter first:** protects the LNA and SDR from powerful FM transmitters.
- **LNA next:** amplifies weak signals with low added noise.
- **SDR last:** digitizes the clean, amplified signal for analysis.


### 🔌 Power Notes for LaNA

- **Via bias-tee (preferred):** if your SDR supports bias-tee (3–5 V DC).
- **Via MicroUSB:** use included adapter (3.3–5.5 V DC).
- **Via DC barrel adapter:** optional input; use only one power source at a time.
- Avoid long-term operation above 5.5 V DC.


### 🧠 Summary

This setup gives you a **versatile and high-performance RF exploration platform**, ideal for:
- Spectrum analysis
- Decoding digital and analog radio signals
- ADS-B aircraft tracking
- Weather satellite imagery
- ISM/IoT device signal inspection
- Ham radio monitoring

*Designed and manufactured by Nooelec (USA/Canada).*


## Software Setup

### TL;DR Summary of Tech Stack

| Layer             | Tool / Package                               | Why                                    |
|-------------------|----------------------------------------------|----------------------------------------|
| **Driver**        | `rtl-sdr` (librtlsdr)                        | The foundation for all RTL-based SDRs. |
| **GUI**           | `SDR++`                                      | Active, fast, modern.                  |
| **CLI utilities** | `rtl_test`, `rtl_fm`, `rtl_power`, `rtl_tcp` | Still canonical low-level tools.       |
| **DSP framework** | `GNU Radio` (optional)                       | Standard for custom signal processing. |
| **Python**        | `pyrtlsdr`                                   | Best way to start custom scripts.      |
| **Decoders**      | `dump1090`, `satdump`, `noaa-apt`, etc.      | Each for a specific signal domain.     |


### Driver Layer (hardware access)

These are fundamental; everything else builds on top of them.

| Package     | Description                                                                                     | Status (2025)                            |
|-------------|-------------------------------------------------------------------------------------------------|------------------------------------------|
| `librtlsdr` | Core open-source driver for RTL2832U-based SDRs. Provides `rtl_*` command-line tools.           | ✅ Actively maintained (osmocom project). |
| `rtl-sdr`   | Ubuntu/Debian package bundling `librtlsdr` + utilities (`rtl_test`, `rtl_fm`, `rtl_tcp`, etc.). | ✅ Current and standard.                  |
| `rtl_biast` | Small utility to toggle bias-tee (bundled by Nooelec or newer `rtl-sdr` versions).              | ✅ Standard for bias-tee models.          |

> 📘 What Is RTL-SDR?
>
> **RTL-SDR** stands for *Realtek Software Defined Radio*.
It refers to a family of inexpensive USB TV tuners based on the **RTL2832U** demodulator chip that, through open-source drivers, can expose *raw I/Q samples* (complex baseband radio data) to the computer instead of decoding TV signals.
>
> This discovery (by Antti Palosaari, Eric Fry, and Osmocom developers) effectively turned a $20 TV dongle into a **wideband radio receiver**.
> All “RTL-SDR” compatible devices, including your **NESDR SMArt v5**, follow this **de facto protocol** implemented by the **`librtlsdr`** driver.
>
> In practice:
> - The **RTL2832U** handles digitization and USB data streaming.
> - The **R820T2 tuner** selects the frequency and gain.
> - The **driver** (via USB) streams I/Q samples to your computer for demodulation and visualization.
>
> There is no separate “protocol” in the network sense — the term *RTL-SDR protocol* simply refers to the standardized USB communication interface used by `librtlsdr`.

#### 🧩 Conceptual Overview

When you run tools like `rtl_fm` or `SDR++`, they talk to the RTL2832U through `librtlsdr`.
This communication controls:

- **Tuning frequency** (via tuner chip)
- **Sampling rate** (ADC and USB transfer)
- **Gain** (RF amplification level)
- **Data streaming** (continuous I/Q samples over USB)

Those raw I/Q streams represent the **complex envelope** of the received signal — the foundation for all SDR processing.
Demodulators, decoders, and visualizers all operate on these samples.


### GUI Spectrum Viewers

To visually explore spectra and tune frequencies.

| Tool         | Description                                                                  | Maintenance / Modernity                          |
|--------------|------------------------------------------------------------------------------|--------------------------------------------------|
| **GQRX**     | Qt-based receiver built on GNU Radio + gr-osmosdr. Lightweight, widely used. | ⚙️ Stable, still maintained but minimal updates. |
| **CubicSDR** | Cross-platform GUI (wxWidgets).                                              | ⚙️ Works, but *aging* (development slowed).      |
| **SDR++**    | Modern, C++17/ImGui-based, plugin-capable, efficient and cross-platform.     | 🚀 **Active and currently the best GUI choice.** |

### Digital Signal Processing Frameworks

To decode, demodulate, or build custom pipelines.

| Framework                       | Use case                                                                 | Notes                                                          |
|---------------------------------|--------------------------------------------------------------------------|----------------------------------------------------------------|
| **GNU Radio**                   | Graph-based signal flow programming, block libraries, visual flowgraphs. | Mature, but heavy. Industry standard for custom SDR pipelines. |
| **SoapySDR + CubicSDR / SDR++** | Generic device abstraction layer (can unify multiple SDRs).              | Very useful for multi-device environments.                     |
| **gr-osmosdr**                  | GNU Radio source/sink for RTL-SDR and friends.                           | Standard integration layer.                                    |

### Decoders & Specialized Software

Each protocol or signal type has its own ecosystem. Examples:

| Domain                        | Tools                                                     |
|-------------------------------|-----------------------------------------------------------|
| **ADS-B (aircraft)**          | `dump1090`, `readsb`, `tar1090`                           |
| **NOAA weather satellites**   | `noaa-apt`, `wxtoimg`, `satdump`                          |
| **Digital voice / ham radio** | `gnuradio + op25`, `DSDPlus` (Windows), `SDRTrunk` (Java) |
| **AIS / marine**              | `aisdecoder`                                              |
| **APRS / pager / telemetry**  | `multimon-ng`                                             |

### Programmatic Access (Python, C++)

| Library                           | Language                     | Status                     |
|-----------------------------------|------------------------------|----------------------------|
| `pyrtlsdr`                        | Python wrapper for librtlsdr | ✅ Stable, simple           |
| `SoapySDR` Python bindings        | Python                       | ✅ More general (multi-SDR) |
| `gnuradio` (with Python bindings) | Python                       | ✅ Complex but powerful     |
