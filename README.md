# video-to-srt

Generate `.srt` subtitle files from video/audio locally (no API key) using Whisper.

## What model does it use?

This repo includes two options:

- `video_to_srt.py`: OpenAI open-source Whisper via `openai-whisper` (default model: `medium`, selectable via `--model`).
- `video_to_srt_mlx.py`: MLX Whisper (Apple Silicon) using `mlx-community/whisper-large-v3-turbo`.

## Folder structure

The script expects (and will auto-create) these folders:

- `Videos/` — put your input video/audio files here
- `SRT Files/` — generated `.srt` files are written here

These folders are intentionally ignored by git (see `.gitignore`) so you don’t accidentally push personal media/subtitles.

## Requirements

- Python 3.9+
- `ffmpeg`
  - macOS (Homebrew): `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt-get update && sudo apt-get install -y ffmpeg`

## Setup (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run (OpenAI Whisper / PyTorch)

```bash
python video_to_srt.py
```

Common options:

```bash
python video_to_srt.py --model large
python video_to_srt.py --language en
python video_to_srt.py --device mps   # Apple Silicon
python video_to_srt.py --device cuda  # NVIDIA
python video_to_srt.py --device cpu
```

## Run (Apple Silicon fast path: MLX Whisper)

MLX Whisper is best on Apple Silicon (M1/M2/M3/M4).

```bash
pip install -r requirements-mlx.txt
python video_to_srt_mlx.py
```

## Notes

- Input formats: `.mp4`, `.mkv`, `.mov`, `.mp3`, `.wav`, `.m4a`, and more (see `VIDEO_EXTENSIONS` in the scripts).
- First run can take time because models may download weights the first time.

