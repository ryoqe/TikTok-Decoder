# 🚀 TikTok Decoder v1.2.0 — Release Notes

We are excited to announce **TikTok Decoder v1.2.0**, bringing a modern desktop graphical user interface (GUI), hardware GPU encoding acceleration, and automatic repair for TikTok encoder exploits and glitch videos!

---

## 🌟 What's New in v1.2.0

### 🖥️ Modern Desktop GUI (`gui.py`)
- Dark-themed desktop user interface with file queue management.
- Live progress bars and status indicators.
- One-click "Play Output" button to preview repaired videos.
- Manual algorithm selector dropdown (Method 1–5 override).

### ⚡ Hardware Acceleration (HW Accel)
- Automatic detection of hardware video encoders:
  - **NVIDIA NVENC** (`h264_nvenc`)
  - **Intel QuickSync** (`h264_qsv`)
  - **AMD AMF** (`h264_amf`)
  - **Windows MediaFoundation** (`h264_mf`)

### 🧵 Multithreaded Batch Processing
- Parallel video processing engine (`-j / --jobs`).
- Asynchronous execution so GUI never freezes.

### 🔊 LUFS Audio Normalization
- Optional broadcast audio level normalization (`-af loudnorm`).

---

## 📌 Exploit Repair Matrix

| Repair Method | Exploits / Hacks | Symptoms | Solution |
| :--- | :--- | :--- | :--- |
| **Method 1** | `ut0ku` PTS Scaling (`-itsscale`) | stuttering, 120 FPS timeline desync | Rescales PTS timestamps & stabilizes frame rate. |
| **Method 2** | `LuisAlves10` NAL Dummy Padding | Player hangs at 14s or silences audio | Trims corrupted NAL packet tail while preserving audio. |
| **Method 3** | `EditingSource` 30 FPS Header Hacking | 2x speed playback / cut off audio | Rescales video and audio PTS to 1.0x natural speed. |
| **Method 4** | `NoBlur` Timestamp Jitter (VFR) | Frame drops in Premiere / CapCut | Re-encodes to strict Constant Frame Rate (CFR). |
| **Method 5** | Standard MP4 | Normal video | Normalizes to standard clean H.264 MP4. |

---

## 📦 Downloads & Installation

### Option 1: Standalone Windows Package (No Python needed!)
1. Download **`TikTok-Decoder-v1.2.0-Windows-x64.zip`** from Assets below.
2. Unzip into any directory.
3. Drag and drop your video file onto **`run.bat`** (or double-click `run.bat` to launch GUI).

### Option 2: Python / Git Clone
```bash
git clone https://github.com/ryoqe/TikTok-Decoder.git
cd TikTok-Decoder
pip install -r requirements.txt
python gui.py
```

---

## ⚡ Requirements
- **Windows / Linux / macOS**
- **[FFmpeg](https://ffmpeg.org/)** installed and added to `PATH` (on Windows: `winget install ffmpeg`).
