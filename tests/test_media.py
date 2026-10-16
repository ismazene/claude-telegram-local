import shutil
import subprocess
import types

import numpy as np
import pytest

from tgmedia import audio, cli, extract_frames

pytestmark = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")


def _ffmpeg(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


@pytest.fixture
def tone(tmp_path):
    path = tmp_path / "tone.ogg"
    _ffmpeg("-f", "lavfi", "-i", "sine=frequency=440:duration=2", str(path))
    return str(path)


@pytest.fixture
def video(tmp_path):
    path = tmp_path / "clip.mp4"
    _ffmpeg("-f", "lavfi", "-i", "testsrc=duration=10:size=160x120:rate=10", str(path))
    return str(path)


def test_decode_audio_is_mono_16k_float(tone):
    pcm = audio.decode_audio(tone)
    assert pcm.dtype == np.float32
    assert 1.9 * audio.SAMPLE_RATE < len(pcm) < 2.2 * audio.SAMPLE_RATE
    assert np.abs(pcm).max() <= 1.0


def test_decode_audio_rejects_garbage(tmp_path):
    bad = tmp_path / "bad.ogg"
    bad.write_bytes(b"not audio")
    with pytest.raises(RuntimeError):
        audio.decode_audio(str(bad))


def test_transcribe_joins_segments(tone, monkeypatch):
    class FakeModel:
        def transcribe(self, pcm, language=None, vad_filter=False):
            assert pcm.dtype == np.float32 and vad_filter
            return [types.SimpleNamespace(text=" hola "), types.SimpleNamespace(text="mundo")], types.SimpleNamespace(language="es")

    monkeypatch.setattr(audio, "_load_model", lambda name: FakeModel())
    result = audio.transcribe(tone)
    assert (result.language, result.text) == ("es", "hola mundo")


def test_extract_frames_respects_limits(video, tmp_path):
    frames = extract_frames(video, str(tmp_path / "out"), every=2, max_frames=3)
    assert len(frames) == 3
    assert all(f.suffix == ".jpg" and f.stat().st_size > 0 for f in frames)


@pytest.mark.parametrize("every,max_frames", [(0, 5), (1, 0), (-1, 5)])
def test_extract_frames_validates_arguments(video, tmp_path, every, max_frames):
    with pytest.raises(ValueError):
        extract_frames(video, str(tmp_path), every, max_frames)


def test_cli_reports_errors_without_traceback(tmp_path, capsys):
    assert cli.main(["transcribe", str(tmp_path / "missing.ogg")]) == 1
    assert "error:" in capsys.readouterr().err


def test_warm_server_roundtrip_and_fallback(tone, monkeypatch):
    import threading
    from http.server import HTTPServer

    from tgmedia import server

    monkeypatch.setattr(audio, "transcribe", lambda p, m, l: audio.Transcript("es", f"ok {m}"))
    assert server.remote_transcribe(tone, "small", None, port=8799) is None  # nothing listening yet
    httpd = HTTPServer((server.HOST, 8799), server._Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        assert server.remote_transcribe(tone, "base", None, port=8799) == audio.Transcript("es", "ok base")
        with pytest.raises(RuntimeError):
            server.remote_transcribe(tone + ".missing", "base", None, port=8799)
    finally:
        httpd.shutdown()
