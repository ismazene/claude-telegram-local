# tgmedia

[![CI](https://github.com/ismazene/claude-telegram-local/actions/workflows/ci.yml/badge.svg)](https://github.com/ismazene/claude-telegram-local/actions/workflows/ci.yml)

Local audio transcription and video frame extraction for chat-bot agents. Built to let [Claude Code](https://claude.com/claude-code) understand voice notes, images and videos sent over Telegram, on a Windows laptop that stays on with the lid closed. [Español](README.es.md)

- **Private:** speech-to-text runs on your CPU with [faster-whisper](https://github.com/SYSTRAN/faster-whisper). Audio never leaves the machine.
- **No cloud keys:** the only external tool is `ffmpeg`.
- **Small:** about 100 lines of Python, with a CI matrix on Ubuntu and Windows.

## Install

Requires Python 3.10+ and `ffmpeg` in `PATH`.

```bash
pip install git+https://github.com/ismazene/claude-telegram-local
```

## Use

```bash
tgmedia transcribe voice.ogg                  # -> [es] hola mundo
tgmedia transcribe talk.mp4 --model medium    # larger model, better accuracy
tgmedia frames clip.mp4 out/ --every 3 --max-frames 8
```

As a library:

```python
from tgmedia import transcribe, extract_frames

result = transcribe("voice.ogg")        # Transcript(language="es", text="...")
frames = extract_frames("clip.mp4", "out")   # list of JPEG paths
```

The first transcription downloads the model (`small` is about 460 MB).

## Running Claude Code from your phone (Windows)

1. Install the official Telegram plugin and pair your account (`/telegram:configure`, `/telegram:access pair <code>`).
2. Lock the bot to you: `/telegram:access policy allowlist`.
3. Auto-start on login: press `Win+R`, run `shell:startup`, and put a shortcut to [`scripts/start-telegram-claude.bat`](scripts/start-telegram-claude.bat) there. It relaunches Claude Code 10 seconds after it exits.
4. Keep the laptop awake with the lid closed: `powershell -File scripts/set-lid-action.ps1` (undo with `-Restore`).
5. Tell the agent to call `tgmedia` on incoming attachments.

## Design notes

- **PyAV workaround.** `faster-whisper` imports PyAV, whose DLL can be blocked by Windows App Control ("DLL load failed"). Decoding is done with `ffmpeg` instead, and PyAV is stubbed only when it cannot be imported (`audio._load_model`).
- **Input contract.** Audio is decoded to mono 16 kHz float32 before reaching the model, so any container `ffmpeg` reads works. Failures raise `RuntimeError` with ffmpeg's message; the CLI turns them into exit code 1.
- **Tests** mock the Whisper model and generate real audio and video with `ffmpeg`, so CI stays fast and downloads no models.

## Security

The bot controls your computer, so protect it accordingly.

- Use the `allowlist` policy and Telegram two-step verification: whoever controls your account controls your PC.
- Never commit the bot token (`.env`) or `access.json`. If a token leaks, revoke it with `/revoke` in BotFather.
- Telegram bots are not end-to-end encrypted.

## Limitations

- The PC must be on, logged in, online and running Claude Code.
- Telegram bots can download files up to 20 MB.
- With Modern Standby (S0) Windows may throttle background processes with the lid closed.
- An unattended session pauses when an action needs a permission confirmation.
- CPU transcription of long audio is slow with larger models.

## Development

```bash
pip install -e ".[dev]"
ruff check . && pytest
```

## License

MIT
