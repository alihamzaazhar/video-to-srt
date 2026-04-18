# video-to-srt

Generate `.srt` subtitle files from video/audio locally (no API key) using OpenAI’s open-source Whisper.

## What model does it use?

The script uses `openai-whisper` (default model: `medium`, selectable via `--model`).

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

## Notes

- Input formats: `.mp4`, `.mkv`, `.mov`, `.mp3`, `.wav`, `.m4a`, and more (see `VIDEO_EXTENSIONS` in the scripts).
- First run can take time because models may download weights the first time.
