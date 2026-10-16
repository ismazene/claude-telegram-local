"""Audio decoding (ffmpeg) and local speech-to-text (faster-whisper)."""

from __future__ import annotations

import subprocess
import sys
import types
from dataclasses import dataclass

import numpy as np

SAMPLE_RATE = 16_000


@dataclass(frozen=True)
class Transcript:
    language: str
    text: str


def decode_audio(path: str) -> np.ndarray:
    """Decode any ffmpeg-readable file to mono float32 PCM at 16 kHz.

    Raises FileNotFoundError if ffmpeg is missing and RuntimeError if decoding fails.
    """
    try:
        proc = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", str(SAMPLE_RATE), "-"],
            capture_output=True,
            check=True,
        )
    except FileNotFoundError as exc:
        raise FileNotFoundError("ffmpeg not found in PATH") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"ffmpeg could not decode {path!r}: {exc.stderr.decode(errors='replace')}") from exc
    return np.frombuffer(proc.stdout, np.int16).astype(np.float32) / 32768.0


def _load_model(name: str):
    # faster-whisper imports PyAV, whose DLL can be blocked by Windows App Control.
    # We decode with ffmpeg ourselves, so a stub is enough when PyAV is unusable.
    try:
        import av  # noqa: F401
    except ImportError:
        sys.modules["av"] = types.ModuleType("av")
    from faster_whisper import WhisperModel

    return WhisperModel(name, device="cpu", compute_type="int8")


def transcribe(path: str, model: str = "small", language: str | None = None) -> Transcript:
    """Transcribe an audio or video file locally; nothing leaves the machine."""
    audio = decode_audio(path)
    segments, info = _load_model(model).transcribe(audio, language=language, vad_filter=True)
    return Transcript(info.language, " ".join(s.text.strip() for s in segments))
