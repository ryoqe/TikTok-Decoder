# 🎬 TikTok Decoder & Repair Tool (v1.2.0)

[![CI Build](https://github.com/ryoqe/TikTok-Decoder/actions/workflows/ci.yml/badge.svg)](https://github.com/ryoqe/TikTok-Decoder/actions)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![FFmpeg Required](https://img.shields.io/badge/FFmpeg-Required-green.svg)](https://ffmpeg.org/)
[![GPU Accelerated](https://img.shields.io/badge/GPU-NVENC%20%7C%20QSV%20%7C%20AMF%20%7C%20MF-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**TikTok Decoder** — мощный инструмент с графическим интерфейсом (GUI) и консольной утилитой (CLI) для автоматического анализа и полного восстановления видеофайлов, созданных с использованием обходов кодировщика TikTok («ломание кодировщика», 120 FPS glitch, PTS scaling, `-itsscale`, подмена метаданных MP4, NAL dummy padding).

---

## 🌟 Главные возможности

- 🖥️ **Графический интерфейс (GUI)**: Тёмный десктопный интерфейс с очередью видео, прогресс-барами, выбором режимов и кнопкой встроенного плеера.
- ⚡ **Аппаратное GPU-ускорение (HW Accel)**: Авто-определение NVIDIA NVENC (`h264_nvenc`), Intel QSV (`h264_qsv`), AMD AMF (`h264_amf`) и Windows MediaFoundation (`h264_mf`).
- 🧵 **Многопоточная пакетная обработка**: Параллельное восстановление нескольких файлов одновременно (`-j / --jobs`).
- 🔊 **Нормализация звука LUFS**: Автоматическое выравнивание громкости аудио под стандарты вещания (`--lufs`).
- 🛠️ **Гибкая настройка**: Поддержка целевого FPS (60 / 120 FPS) и регулировка качества H.264 (CRF 16–28).

---

## 🚀 Быстрый запуск (Quick Start)

### Способ 1: Drag-and-Drop (Самый простой)
Просто **перетащите мышкой** любой видеофайл или папку с видео прямо на файл **`run.bat`** в проводнике Windows. Процесс ремонта запустится автоматически!

---

### Способ 2: Десктопный графический интерфейс (GUI)
1. Дважды кликните по **`run.bat`** и выберите пункт `[1]`.
2. Или запустите через консоль:
   ```bash
   python gui.py
   ```

---

### Способ 3: Консольный режим (CLI)
* **Авто-ремонт файлов из папки `input/`**:
  ```bash
  python main.py -i input -o output --gpu
  ```
* **Ремонт с целевым FPS 120 и качеством CRF 16**:
  ```bash
  python main.py -i my_video.mp4 -o output -fps 120 -crf 16 --gpu
  ```
* **Принудительный запуск конкретного метода (напр. Method 3)**:
  ```bash
  python main.py -i input -o output -m method3 --gpu
  ```

---

## 📌 Матрица поддерживаемых эксплоитов TikTok

| Режим ремонта | Название хака / Авторы | Симптомы в медиаплеере / редакторе | Алгоритм восстановления |
| :--- | :--- | :--- | :--- |
| **Method 1: ut0ku** | Подмена `stts` и `-itsscale` PTS | Видео воспроизводится рывками или лагает в VLC/Premiere. | Масштабирование PTS и выравнивание таймлайна в 60/120 FPS. |
| **Method 2: LuisAlves10** | Дописывание битых NAL-пакетов | Плеер зависает на 14-й секунде или тушит звук до 80 сек. | Точное отсечение битого мусора с сохранением исходного аудио. |
| **Method 3: EditingSource** | 60 FPS кадры в 30 FPS MP4 контейнере | Ускоренное видео (2x) или обрыв речи на 24-й секунде. | Синхронная компрессия PTS видео и звука в 1.0x нормальный темп. |
| **Method 4: NoBlur** | Джиттер таймштампов VFR | Пропуски кадров и фризы в CapCut / Premiere / Vegas. | Перекодирование в строгий Constant Frame Rate (CFR). |
| **Method 5: Standard** | Стандартный MP4 файл | Воспроизводится нормально. | Чистая нормализация в стандартный H.264 MP4. |

---

## 🛠️ Установка и требования

### 1. Системные требования
- **Python**: версии 3.8 или выше.
- **FFmpeg**: обязательный системный компонент (должен быть доступен в `PATH`).

### 2. Установка FFmpeg

* **Windows**:
  ```powershell
  winget install FFmpeg
  ```
  *(Или через Chocolatey: `choco install ffmpeg`)*

* **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt update && sudo apt install -y ffmpeg
  ```

* **macOS**:
  ```bash
  brew install ffmpeg
  ```

### 3. Клонирование репозитория и установка зависимостей
```bash
# 1. Клонируйте репозиторий
git clone https://github.com/ryoqe/TikTok-Decoder.git
cd TikTok-Decoder

# 2. Установите зависимости Python
pip install -r requirements.txt
```

---

## 📂 Структура проекта

```
TikTok-Decoder/
├── .github/
│   ├── ISSUE_TEMPLATE/    # Шаблоны багрепортов и фич для GitHub
│   └── workflows/         # Автоматические CI-тесты GitHub Actions
├── input/                 # Папка для исходных видеофайлов (.gitkeep)
├── output/                # Папка для отремонтированных MP4 (.gitkeep)
├── src/
│   ├── __init__.py
│   ├── analyzer.py        # Анализатор эксплоитов через FFprobe
│   ├── converter.py       # Движок восстановления видео через FFmpeg
│   ├── hwaccel.py         # Детектор GPU-ускорения (NVENC / QSV / AMF / MF)
│   ├── batch.py           # Многопоточный движок обработки
│   ├── gui_app.py         # Десктопный интерфейс Tkinter
│   └── utils.py           # Вспомогательные утилиты
├── gui.py                 # Точка входа в GUI интерфейс
├── main.py                # Точка входа в CLI интерфейс
├── run.bat                # Windows лаунчер (GUI / CLI / Drag&Drop)
├── requirements.txt       # Зависимости Python
├── .gitignore             # Правила исключений Git
├── CONTRIBUTING.md        # Инструкция для контрибьюторов
├── LICENSE                # Лицензия MIT
├── ROADMAP.md             # Дорожная карта проекта
└── README.md              # Документация проекта
```

---

## 🤝 Вклад в проект (Contributing)

Приветствуются пулл-реквесты, багрепорты и новые идее! Пожалуйста, ознакомьтесь с [CONTRIBUTING.md](CONTRIBUTING.md) перед созданием PR.

---

## 📜 Лицензия

Проект распространяется под открытой лицензией [MIT](LICENSE).
