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

## 🚀 Phase 2: Hardware Acceleration & Performance Scaling (v1.1.0 - ⏱️ Q3 2026)

- [ ] **GPU Acceleration Auto-Detection**:
  - [ ] NVIDIA NVENC (`-c:v h264_nvenc`) support.
  - [ ] Intel QuickSync (QSV) & AMD AMF hardware encoder fallback.
- [ ] **Multi-Threaded Parallel Batch Engine**:
  - [ ] Concurrent multi-file processing using Python `concurrent.futures`.
  - [ ] Memory-efficient queuing for large batch folders (100+ videos).
- [ ] **Audio & Quality Enhancements**:
  - [ ] Integrated LUFS loudness normalization (`-af loudnorm`).
  - [ ] Custom CRF/Bitrate tuning sliders.

---

## 🎨 Phase 3: Modern Desktop GUI (v1.2.0 - ⏱️ Q4 2026)

- [ ] **Cross-Platform GUI (PyQt6 / CustomTkinter)**:
  - [ ] Clean dark-mode interface with drag-and-drop zone.
  - [ ] Side-by-side video player preview (Original vs Repaired).
  - [ ] Real-time progress indicators and video thumbnail generation.
- [ ] **Standalone Portable Executable**:
  - [ ] PyInstaller single `.exe` bundle for Windows (no Python installation required).

---

## 🌐 Phase 4: Web Browser Version & Cloud Ecosystem (v2.0.0 - ⏱️ 2027)

- [ ] **FFmpeg.wasm Web App**:
  - [ ] Client-side browser version running directly on GitHub Pages.
- [ ] **Browser Extension (Chrome / Firefox)**:
  - [ ] One-click download & repair button integrated into TikTok web interface.
