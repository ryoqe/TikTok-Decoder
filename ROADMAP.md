# 🛣️ TikTok Decoder Project Roadmap

## 🎯 Project Overview
**TikTok Decoder** aims to be the definitive open-source toolkit for analyzing, fixing, and normalizing videos created using TikTok encoder exploits (PTS scaling, `-itsscale`, atom padding, VFR hacks, audio timebase glitches).

---

## 📌 Phase 1: Core Engine & Automatic Exploit Classification (v1.0.0 - ✅ COMPLETED)

- [x] **Exploit Detection Matrix**:
  - [x] `METHOD_1_ITSSCALE_PTS`: Automatic PTS scaling detection (`ut0ku/120fps-method`).
  - [x] `METHOD_2_DUMMY_PADDING`: Detection of corrupted trailing NAL packets / atom duration hacks (`LuisAlves10/TikTok-FPS-Compression-Bypasser`).
  - [x] `METHOD_3_CONTAINER_DOUBLED`: Detection of 30fps header hacks with 60fps frame count (`EditingSource/EN-TikTok-60FPS`).
  - [x] `METHOD_4_VFR_NOBLUR`: Detection of VFR timestamp jitter and sample table density hacks (`irgifebry/NoBlur`).
  - [x] `METHOD_STANDARD`: Standard compliant pass-through.
- [x] **Error Tolerance**: Implemented `-err_detect ignore_err` and `-max_error_rate 1.0` for full compatibility with FFmpeg 8.x.
- [x] **Windows Launcher**: `run.bat` with interactive CLI menu and instant Drag-and-Drop support.
- [x] **Batch Processing**: Automatic discovery of video files in `input/` and export to `output/`.

---

## 🚀 Phase 2: Hardware Acceleration & Performance Scaling (v1.1.0 - ✅ COMPLETED)

- [x] **GPU Acceleration Auto-Detection**:
  - [x] NVIDIA NVENC (`h264_nvenc`) & Windows MediaFoundation (`h264_mf`) auto-detection.
  - [x] Intel QuickSync (QSV) & AMD AMF hardware encoder fallback.
- [x] **Multi-Threaded Parallel Batch Engine**:
  - [x] Concurrent multi-file processing using Python `concurrent.futures.ThreadPoolExecutor`.
  - [x] Configurable worker count (`-j / --jobs`).
- [x] **Audio & Quality Enhancements**:
  - [x] Integrated LUFS loudness normalization (`-af loudnorm`).
  - [x] Quality preset selection (UHQ CRF 16, HQ CRF 18, Balanced CRF 23).

---

## 🎨 Phase 3: Modern Desktop GUI & Visual Interface (v1.2.0 - ✅ COMPLETED)

- [x] **Desktop GUI Application (`gui.py` / `src/gui_app.py`)**:
  - [x] Dark-themed modern interface with live queue table and status indicators.
  - [x] File and folder drag-and-drop / add queue buttons.
  - [x] Settings control panel (60/120 FPS target, CRF quality, GPU HW accel toggle, LUFS audio toggle, Worker thread selector).
  - [x] Background asynchronous repair engine so GUI never freezes.
  - [x] Built-in video player launcher ("Play Selected Output").
- [x] **Windows Launcher**: `run.bat` updated with option `[1] Launch Desktop GUI App`.
- [x] **CLI `--gui` Flag**: `python main.py --gui` launches GUI directly.

---

## 🌐 Phase 4: Web Browser Version & Cloud Ecosystem (v2.0.0 - ⏱️ 2027)

- [ ] **FFmpeg.wasm Web App**:
  - [ ] Client-side browser version running directly on GitHub Pages.
- [ ] **Browser Extension (Chrome / Firefox)**:
  - [ ] One-click download & repair button integrated into TikTok web interface.
