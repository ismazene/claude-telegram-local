# tgmedia

Transcripción local de audio y extracción de fotogramas de vídeo para agentes por chat. Pensado para que [Claude Code](https://claude.com/claude-code) entienda notas de voz, imágenes y vídeos enviados por Telegram, en un portátil con Windows que sigue encendido con la tapa cerrada. [English](README.md)

- **Privado:** la transcripción se ejecuta en tu CPU con [faster-whisper](https://github.com/SYSTRAN/faster-whisper). El audio no sale de tu PC.
- **Sin claves en la nube:** la única herramienta externa es `ffmpeg`.
- **Pequeño:** unas 100 líneas de Python, con CI en Ubuntu y Windows.

## Instalación

Requiere Python 3.10+ y `ffmpeg` en el `PATH`.

```bash
pip install git+https://github.com/ismazene/claude-telegram-local
```

## Uso

```bash
tgmedia transcribe voz.ogg                    # -> [es] hola mundo
tgmedia transcribe charla.mp4 --model medium  # modelo mayor, más precisión
tgmedia frames clip.mp4 salida/ --every 3 --max-frames 8
```

La primera transcripción descarga el modelo (`small` pesa unos 460 MB).

## Claude Code desde el móvil (Windows)

1. Instala el plugin oficial de Telegram y empareja tu cuenta (`/telegram:configure`, `/telegram:access pair <código>`).
2. Restringe el bot a ti: `/telegram:access policy allowlist`.
3. Arranque automático: `Win+R`, `shell:startup`, y añade un acceso directo a [`scripts/start-telegram-claude.bat`](scripts/start-telegram-claude.bat). Relanza Claude Code 10 segundos después de cerrarse.
4. Portátil encendido con la tapa cerrada: `powershell -File scripts/set-lid-action.ps1` (se deshace con `-Restore`).
5. Indica al agente que use `tgmedia` con los adjuntos que lleguen.

## Seguridad

El bot controla tu ordenador. Usa `allowlist`, activa la verificación en dos pasos de Telegram y nunca subas el token (`.env`) ni `access.json`. Si el token se filtra, revócalo con `/revoke` en BotFather.

## Limitaciones

- El PC debe estar encendido, con sesión iniciada, con internet y con Claude Code abierto.
- Los bots de Telegram solo descargan archivos de hasta 20 MB.
- Con modo de espera moderno (S0), Windows puede limitar procesos con la tapa cerrada.
- Una sesión sin supervisión se detiene cuando una acción pide confirmación.

## Licencia

MIT
