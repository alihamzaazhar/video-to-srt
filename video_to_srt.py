"""
Video to SRT Subtitle Generator (Local Whisper - FREE)
=======================================================
Uses OpenAI's open-source Whisper model locally. No API key needed.
Optimized for Apple Silicon (MPS acceleration on M1/M2/M3/M4).

Folder structure:
    video-to-srt/
    ├── Videos/            ← Drop your video files here
    ├── SRT Files/         ← Generated .srt files appear here
    └── video_to_srt.py    ← This script

Usage:
    python video_to_srt.py                    # Interactive: lists videos, you pick one
    python video_to_srt.py --model large      # Use large model
    python video_to_srt.py --language ur       # Force Urdu

Requirements:
    pip install openai-whisper
    brew install ffmpeg
"""

import argparse
import os
import sys

import whisper

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEOS_DIR = os.path.join(SCRIPT_DIR, "Videos")
SRT_DIR = os.path.join(SCRIPT_DIR, "SRT Files")

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".wmv", ".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}


def format_timestamp(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    s, ms = divmod(millis, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def segments_to_srt(segments) -> str:
    srt_blocks = []
    for i, seg in enumerate(segments, start=1):
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        text = seg["text"].strip()
        if text:
            srt_blocks.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(srt_blocks)


def get_device(forced_device=None):
    if forced_device:
        return forced_device
    import torch
    if torch.backends.mps.is_available():
        print("Detected Apple Silicon — using MPS acceleration.")
        return "mps"
    elif torch.cuda.is_available():
        print("Detected NVIDIA GPU — using CUDA acceleration.")
        return "cuda"
    else:
        print("No GPU detected — using CPU.")
        return "cpu"


def list_videos():
    """Return list of video files with their SRT status."""
    if not os.path.isdir(VIDEOS_DIR):
        return []

    existing_srts = set()
    if os.path.isdir(SRT_DIR):
        existing_srts = {os.path.splitext(f)[0] for f in os.listdir(SRT_DIR) if f.endswith(".srt")}

    videos = []
    for f in sorted(os.listdir(VIDEOS_DIR)):
        if os.path.splitext(f)[1].lower() in VIDEO_EXTENSIONS:
            has_srt = os.path.splitext(f)[0] in existing_srts
            size_mb = os.path.getsize(os.path.join(VIDEOS_DIR, f)) / (1024 * 1024)
            videos.append({"name": f, "has_srt": has_srt, "size_mb": size_mb})
    return videos


def pick_video(videos):
    """Display numbered list and let user pick a video."""
    print("\n  #  | Status | Size     | File")
    print("  ---|--------|----------|" + "-" * 40)

    for i, v in enumerate(videos, start=1):
        status = "✅ done" if v["has_srt"] else "⏳ new "
        print(f"  {i:<2} | {status} | {v['size_mb']:>6.1f} MB | {v['name']}")

    print()
    while True:
        try:
            choice = input("Enter number (or 'q' to quit): ").strip()
            if choice.lower() == "q":
                sys.exit(0)
            idx = int(choice) - 1
            if 0 <= idx < len(videos):
                selected = videos[idx]
                if selected["has_srt"]:
                    redo = input(f"'{selected['name']}' already has an SRT. Redo? (y/n): ").strip().lower()
                    if redo != "y":
                        return pick_video(videos)
                return selected["name"]
            else:
                print(f"  Pick a number between 1 and {len(videos)}")
        except ValueError:
            print("  Enter a valid number")


def main():
    parser = argparse.ArgumentParser(
        description="Generate .srt subtitles from videos in the Videos/ folder."
    )
    parser.add_argument("--model", "-m", default="medium",
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper model size (default: medium)")
    parser.add_argument("--language", "-l", default=None,
                        help="Language code e.g. 'en', 'ur', 'es' (auto-detected if omitted)")
    parser.add_argument("--device", "-d", default=None,
                        choices=["cpu", "cuda", "mps"],
                        help="Force a specific device")
    args = parser.parse_args()

    os.makedirs(VIDEOS_DIR, exist_ok=True)
    os.makedirs(SRT_DIR, exist_ok=True)

    videos = list_videos()

    if not videos:
        print(f"No video/audio files found. Drop them in:\n  {VIDEOS_DIR}")
        sys.exit(0)

    print(f"\nFound {len(videos)} file(s) in Videos/")
    filename = pick_video(videos)

    video_path = os.path.join(VIDEOS_DIR, filename)
    srt_name = os.path.splitext(filename)[0] + ".srt"
    srt_path = os.path.join(SRT_DIR, srt_name)

    device = get_device(args.device)
    print(f"\nLoading '{args.model}' model on '{device}'...")
    model = whisper.load_model(args.model, device=device)

    print(f"Transcribing: {filename}")
    opts = {"verbose": True}
    if args.language:
        opts["language"] = args.language
    if device == "mps":
        opts["fp16"] = False

    try:
        result = model.transcribe(video_path, **opts)
        print(f"Detected language: {result.get('language', 'unknown')}")

        srt_content = segments_to_srt(result["segments"])
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content)

        print(f"\nDone! Saved: SRT Files/{srt_name} ({len(result['segments'])} segments)")

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()