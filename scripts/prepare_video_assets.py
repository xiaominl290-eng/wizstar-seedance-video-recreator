#!/usr/bin/env python3
"""Extract reusable analysis and digital-human assets from a source video."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess


def find_ffmpeg(explicit: str | None) -> str:
    if explicit:
        return explicit
    env = os.environ.get("FFMPEG_BIN")
    if env:
        return env
    system = shutil.which("ffmpeg")
    if system:
        return system
    try:
        import imageio_ffmpeg  # type: ignore

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:  # pragma: no cover - environment dependent
        raise SystemExit("ffmpeg not found; pass --ffmpeg or set FFMPEG_BIN") from exc


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def probe(ffmpeg: str, source: Path) -> dict[str, object]:
    result = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(source)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    text = result.stderr
    duration_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", text)
    video_match = re.search(r"Video:.*?\b(\d{2,5})x(\d{2,5})\b.*?([0-9.]+) fps", text)
    audio_match = re.search(r"Audio:\s*([^,]+),\s*(\d+) Hz,\s*([^,]+)", text)
    duration = None
    if duration_match:
        duration = (
            int(duration_match.group(1)) * 3600
            + int(duration_match.group(2)) * 60
            + float(duration_match.group(3))
        )
    return {
        "source": str(source.resolve()),
        "duration_seconds": duration,
        "width": int(video_match.group(1)) if video_match else None,
        "height": int(video_match.group(2)) if video_match else None,
        "fps": float(video_match.group(3)) if video_match else None,
        "audio_codec": audio_match.group(1).strip() if audio_match else None,
        "audio_hz": int(audio_match.group(2)) if audio_match else None,
        "audio_layout": audio_match.group(3).strip() if audio_match else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--prefix", default="source")
    parser.add_argument("--ffmpeg")
    parser.add_argument("--sheet-interval", type=float, default=3.0)
    args = parser.parse_args()

    if not args.source.is_file():
        raise SystemExit(f"source video not found: {args.source}")

    ffmpeg = find_ffmpeg(args.ffmpeg)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    base = args.output_dir / args.prefix

    metadata_path = base.with_name(base.name + "_metadata.json")
    metadata_path.write_text(
        json.dumps(probe(ffmpeg, args.source), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    original_mix = base.with_name(base.name + "_original_mix.mp3")
    enhanced = base.with_name(base.name + "_enhanced_voice.mp3")
    contact_sheet = base.with_name(base.name + "_contact_sheet.jpg")

    run([
        ffmpeg, "-y", "-i", str(args.source), "-vn", "-map", "0:a:0",
        "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "44100", str(original_mix),
    ])
    run([
        ffmpeg, "-y", "-i", str(args.source), "-vn", "-map", "0:a:0", "-af",
        "pan=mono|c0=0.5*c0+0.5*c1,highpass=f=90,lowpass=f=14000,"
        "afftdn=nf=-25,acompressor=threshold=0.12:ratio=3:attack=5:release=120:makeup=2,"
        "loudnorm=I=-16:LRA=7:TP=-1.5",
        "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "44100", str(enhanced),
    ])
    run([
        ffmpeg, "-y", "-i", str(args.source), "-vf",
        f"fps=1/{args.sheet_interval},scale=270:-2,tile=4x3:padding=4:margin=4",
        "-frames:v", "1", str(contact_sheet),
    ])

    print(json.dumps({
        "metadata": str(metadata_path),
        "original_mix": str(original_mix),
        "enhanced_voice": str(enhanced),
        "contact_sheet": str(contact_sheet),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
