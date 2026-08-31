# Wizstar browser workflow

1. Read and follow the available Chrome/Browser control skill before browser actions.
2. Reuse the user's signed-in Wizstar tab or open the official AI video generator.
3. Select Reference-to-Video and the requested Seedance model.
4. Set duration, resolution, aspect ratio, and output count before uploading.
5. Upload only the prepared references. Confirm outbound uploads when required.
6. Enter the chronological prompt and verify every `@视频N` maps to the intended asset.
7. Read the visible credit cost and submit once within the user's authorization.
8. If reCAPTCHA appears, stop and ask whether the user wants it solved. Continue only after confirmation.
9. Open History and poll every 30–60 seconds. Report only meaningful state changes.
10. Treat “已退还” as a refunded failure, not completion. Modify the likely cause before one retry.
11. On completion, verify model, duration, resolution, and playable media duration.

## Export recovery order

1. Call the media locator's download method.
2. Wrap the visible download button click in a page download-event wait.
3. Inventory page assets and bundle the exact completed media asset.
4. Use the direct media URL only if ordinary network access succeeds.
5. If CDN content type or client blocking prevents export, preserve the completed history item, give a precise manual-download handoff, and continue with any separately authorized fallback edit. Label the fallback honestly.

Never state that a locally delivered file is the Seedance output unless that exact generated asset was exported and verified.
