---
name: wizstar-seedance-video-recreator
description: Analyze a reference video or Douyin link, break down its shots, narration, overlays, audio, pacing, and story, then use the user's signed-in Wizstar Seedance model to generate a reproducible recreation and post-process deliverables. Use when the user asks to “复刻这个视频”, “调用我的 Wizstar/Seedance”, analyze a short-video reference, find authentic event footage, reproduce text/audio, or extract a digital-human talking-head package containing script, enhanced voice audio, original mix, and subtitles.
---

# Wizstar Seedance Video Recreator

Turn a reference short video into an auditable analysis, a Wizstar Seedance generation job, a finished vertical video, and optional digital-human voiceover assets.

## Start

1. Identify the source URL/file, desired duration, aspect ratio, model, fidelity, required identity/voice, and deliverables.
2. Treat “一模一样” as a request for measurable fidelity: timeline, story, framing, pacing, text, and mix. Do not promise identical stochastic generation.
3. Separate three authorizations:
   - Analyze/download the supplied reference.
   - Upload references and spend Wizstar credits.
   - Reuse identifiable faces, voices, logos, music, or copyrighted footage.
4. If the user explicitly asked to generate with their Wizstar account, proceed within that scope while following browser confirmation rules. Ask before each CAPTCHA. Never bypass browser safety interstitials.

## Workspace Layout

Create task-local folders rather than writing into the skill:

```text
work/source/       downloaded references
work/analysis/     metadata, contact sheets, transcript, timeline
work/references/   short upload clips
work/generated/    downloaded model outputs
outputs/           final user-facing files only
```

## Workflow

### 1. Acquire and inspect the source

- For a URL, use the available Browser/Chrome skill and web tools. Prefer the source page's rendered media or page-assets export over guessed endpoints.
- Preserve the original source URL and creator/title in the analysis notes.
- For a local file, inspect video dimensions, codec, frame rate, duration, and audio streams.
- Run `scripts/prepare_video_assets.py` to create a contact sheet, original mix, enhanced mono voice track, and metadata.
- Never claim the source was downloaded if only a page preview or task history is available.

### 2. Build the reconstruction specification

Read [references/analysis-schema.md](references/analysis-schema.md). Produce:

- Global visual style and color palette.
- Second-by-second shot table with subject, framing, movement, transition, and source.
- Exact or best-effort narration transcript.
- Persistent and timed text overlays, logos, dates, prices, and calls to action.
- Music, speech, effects, and ambience notes.
- A list of elements that must be post-produced because video models render text/logos unreliably.

Use OCR/transcription confidence labels. Do not silently invent unreadable words.

### 3. Source authentic supplemental footage

When the user requests real event/product/location footage:

- Search current official sites, organizers, manufacturers, archives, and permissively licensed media.
- Prefer first-party or clearly licensed sources. Record the URL and license/usage note.
- Do not download unrelated footage merely because it looks similar.
- Cut short, semantically distinct references with `scripts/cut_reference_clips.py`.

### 4. Prepare Seedance references and prompt

Read [references/seedance-prompting.md](references/seedance-prompting.md).

- Keep each reference short enough for reliable upload and clearly assign its role: style/timing, authentic subject, identity, location, or audio.
- Use `@视频1`, `@视频2`, and so on explicitly in the prompt.
- Ask Seedance to leave text-safe areas. Generate typography, prices, dates, and dense schedules in post-production.
- Describe negative constraints: deformation, object swaps, wrong vehicle class, duplicate crowds, bad fingers, unreadable text, unwanted dialogue, and watermarks.
- If a real identifiable person or cloned voice is requested, reuse only user-provided/authorized media. Otherwise keep the person fictional or non-identifiable.

### 5. Operate Wizstar

Read [references/wizstar-browser-workflow.md](references/wizstar-browser-workflow.md) before interacting with Wizstar.

- Use the existing signed-in Chrome session when available.
- Select the requested Seedance model, duration, resolution, ratio, and output count.
- Upload only the prepared references needed for the prompt.
- Confirm the visible credit cost before generating when the browser policy requires it.
- Submit once, then poll History at sensible intervals. Distinguish queued, creating, failed/refunded, and completed states.
- Do not retry a charged failure repeatedly without checking refund state and modifying the likely failure cause.

### 6. Export and post-produce

Try export methods in this order:

1. Media locator download API.
2. Site download button wrapped in a download-event wait.
3. Page-assets bundling for the exact completed video asset.
4. Direct asset URL only when it is accessible and authorized.
5. If the CDN blocks automated export, keep the completed Wizstar history item and state that a manual download/handoff is required. Do not replace it silently with the original video.

After export:

- Trim to target duration and normalize to H.264, AAC, `yuv420p`, and fast-start MP4.
- Add exact text, logos, schedules, and subtitles in post.
- Mix authorized original narration or generated voice at the requested level.
- Keep a clean version and a packaged version when useful.

### 7. Create digital-human voiceover assets

Read [references/digital-human.md](references/digital-human.md) when the user asks for 数字人口播, 对口型, 口播素材, or a voiceover pack.

- Extract a plain-text script, original mix, enhanced mono speech track, and SRT.
- Explain that the enhanced track may retain music if the source contains a mastered mix; do not call it isolated dry voice unless source separation was actually performed.
- A montage/event video without a stable frontal face cannot supply the avatar video. Request or create a separate authorized frontal portrait clip.

## Quality Checks

Before delivery, verify:

- Correct duration, aspect ratio, dimensions, video/audio codecs, and nonzero file size.
- Opening, midpoint, overlay-card, and final frames through a contact sheet.
- Spoken copy and SRT end within the actual audio duration.
- No missing source-attribution notes for supplemental footage.
- The final answer distinguishes generated output, original reference, fallback edit, and digital-human assets.

Deliver only user-facing artifacts from the task's `outputs/` folder.
