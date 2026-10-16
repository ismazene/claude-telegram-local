"""Local audio transcription and video frame extraction for chat-bot agents."""

from tgmedia.audio import decode_audio, transcribe
from tgmedia.video import extract_frames

__all__ = ["decode_audio", "extract_frames", "transcribe"]
__version__ = "0.1.0"
