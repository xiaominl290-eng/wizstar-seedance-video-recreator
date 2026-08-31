# Seedance reference-to-video prompting

Use one role per reference and name it explicitly.

```text
Create a {duration}-second, {aspect-ratio}, {resolution}, photorealistic {genre} video.

Reference roles:
- @视频1: timing, framing, camera motion, edit rhythm, and color only.
- @视频2: authentic {event/product/location} appearance and physical details.
- @视频3: optional identity/wardrobe reference supplied and authorized by the user.

Timeline:
0-{t1}s: {shot}
{t1}-{t2}s: {shot}
...

Style: {camera/lens/light/edit/motion descriptors}.
Audio: {natural effects / no dialogue / authorized narration requirements}.
Leave clean top, center, subtitle, and bottom-safe areas for post-production.

Do not generate unreadable text, extra logos, watermarks, wrong object classes,
deformed hands/faces/vehicles, floating parts, duplicate crowds, object swaps,
camera discontinuities, or unrequested dialogue.
```

## Reliability rules

- Prefer several 3–8 second references over one long, overloaded reference.
- Keep the prompt chronological and measurable.
- For real events, describe physical invariants such as vehicle class, wheel count, body proportions, track type, and safety equipment.
- Ask for no generated text when exact copy is required; add text later.
- Avoid a real public person's name when only the action/role matters. Use an authorized visual reference when identity is necessary.
- On failure, shorten references, remove conflicting instructions, remove public-person names, and retry once after verifying refund state.
