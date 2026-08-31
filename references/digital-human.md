# Digital-human voiceover package

Create these outputs from the source video:

- `{name}_口播文案.txt`: punctuation normalized for speech; include pronunciation/emphasis notes separately.
- `{name}_原始混音.mp3`: faithful audio mix.
- `{name}_人声增强.mp3`: mono, speech-band filtered, denoised, compressed, and normalized.
- `{name}_字幕.srt`: entries ending no later than the actual audio duration.
- Optional ZIP containing the package.

Use `scripts/prepare_video_assets.py` for the two audio files and contact sheet. Transcribe the speech separately, then verify names, numbers, prices, dates, and venue terms against visible text or authoritative sources.

## Avatar-video requirements

- One stable, authorized person facing the camera.
- Mouth, jawline, and eyes unobstructed.
- Natural blinking and small head movement; no fast cuts.
- Even lighting and consistent identity/wardrobe.
- MP4/MOV within the target platform's displayed duration, size, and resolution limits.

Do not claim that an event montage supplies an avatar video when it lacks a continuous frontal face. Ask for a portrait clip or generate a clearly fictional/authorized avatar.
