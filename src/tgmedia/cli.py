"""Command line entry point: `tgmedia transcribe FILE` and `tgmedia frames FILE OUT_DIR`."""

from __future__ import annotations

import argparse
import sys

from tgmedia.audio import transcribe
from tgmedia.video import extract_frames


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tgmedia", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    t = sub.add_parser("transcribe", help="transcribe an audio or video file")
    t.add_argument("file")
    t.add_argument("--model", default="small", help="faster-whisper model (default: small)")
    t.add_argument("--language", help="force a language code, e.g. es")

    f = sub.add_parser("frames", help="extract JPEG frames from a video")
    f.add_argument("file")
    f.add_argument("out_dir")
    f.add_argument("--every", type=float, default=3.0, help="seconds between frames")
    f.add_argument("--max-frames", type=int, default=8)

    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        if args.command == "transcribe":
            result = transcribe(args.file, args.model, args.language)
            print(f"[{result.language}] {result.text}")
        else:
            for frame in extract_frames(args.file, args.out_dir, args.every, args.max_frames):
                print(frame)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
