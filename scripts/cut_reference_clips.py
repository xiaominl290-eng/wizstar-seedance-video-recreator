#!/usr/bin/env python3
"""Create short H.264 reference clips for multimodal video generation."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

from prepare_video_assets import find_ffmpeg


def parse_range(value: str) -> tuple[float, float]:
    try:
        start_text, end_text = value.split(":", 1)
        start, end = float(start_text), float(end_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("range must be START:END in seconds") from exc
    if start < 0 or end <= start:
        raise argparse.ArgumentTypeError("range must satisfy 0 <= START < END")
    return start, end


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--range", dest="ranges", action="append", type=parse_range, required=True)
    parser.add_argument("--prefix", default="reference")
    parser.add_argument("--ffmpeg")
    args = parser.parse_args()

    if not args.source.is_file():
        raise SystemExit(f"source video not found: {args.source}")
    ffmpeg = find_ffmpeg(args.ffmpeg)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for index, (start, end) in enumerate(args.ranges, 1):
        output = args.output_dir / f"{args.prefix}_{index:02d}_{start:g}-{end:g}s.mp4"
        subprocess.run([
            ffmpeg, "-y", "-ss", str(start), "-to", str(end), "-i", str(args.source),
            "-vf", "scale=720:-2,fps=30", "-an", "-c:v", "libx264", "-preset", "fast",
            "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output),
        ], check=True)
        print(output)


if __name__ == "__main__":
    main()
