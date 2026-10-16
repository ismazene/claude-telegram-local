"""Video frame extraction (ffmpeg)."""

from __future__ import annotations

import subprocess
from pathlib import Path


def extract_frames(path: str, out_dir: str, every: float = 3.0, max_frames: int = 8) -> list[Path]:
    """Save one JPEG every `every` seconds, at most `max_frames`, and return their paths."""
    if every <= 0 or max_frames <= 0:
        raise ValueError("every and max_frames must be positive")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            [
                "ffmpeg", "-v", "error", "-y", "-i", path,
                "-vf", f"fps=1/{every}", "-frames:v", str(max_frames),
                str(out / "frame_%02d.jpg"),
            ],
            capture_output=True,
            check=True,
        )
    except FileNotFoundError as exc:
        raise FileNotFoundError("ffmpeg not found in PATH") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"ffmpeg could not read {path!r}: {exc.stderr.decode(errors='replace')}") from exc
    return sorted(out.glob("frame_*.jpg"))
