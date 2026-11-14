# Daily Instagram run – @naturaldye.sbpl (Sodhani Biotech)

Runs every day at 10:45 AM IST. Everything goes live around 11:00 AM IST.

## Sources
- **Content calendar (Claude Sheet):** https://claude.ai/artifact/HTdVQ7A7B3nFEagTpuqBGm
  (artifact id `854a0b4a-e650-44b5-a82e-42fdb42b9d1a`, sheet `Calendar`).
  Columns: A Date, B Day, C Feed post topic, D Reel (Mon/Wed/Fri), E Story, F Caption, G Hashtags, H Post time, I Status.
- **Instagram:** Windsor.ai for Social Media connector, connector `instagram`, account `17841468411588839`.
- **Media hosting:** this repo. Public URL pattern:
  `https://raw.githubusercontent.com/organic-ctrl/naturaldyes-social/main/<path>`

## Steps
1. Find today's row (IST date) in the Calendar sheet. If Status is already `Posted`, stop.
2. **Feed post:** `python3 tools/make_media.py post posts/YYYY-MM-DD.jpg "<kicker>" "<short title>" "<1–2 sentence body>"`.
   Kicker = the part of the topic before ":" (or "Natural dyes"); title = the short headline (max ~8 words); body = a short version of the caption.
3. **Story:** `python3 tools/make_media.py story stories/YYYY-MM-DD.jpg "<kicker>" "<question or fact>" "<short line>"`.
   The API can't add poll, quiz or question stickers, so write the story as a question card ("Reply in DMs / comment on today's post").
4. **Reel (Mon/Wed/Fri only, when column D has text):**
   `python3 tools/make_media.py reel reels/YYYY-MM-DD.mp4 "<hook>" "<point 1>" "<point 2>" "<CTA>"`.
   Write a reel caption: 1–2 lines plus the same hashtags.
5. Look at each image (and a frame of the reel). Check that the text fits and nothing is cut off.
6. `git add`, commit, and push to `main` (use `git -c push.negotiate=true push origin HEAD`).
   Wait ~30 s, then check that each raw URL returns HTTP 200.
7. Publish with Windsor `execute_action`:
   - `create_image_post` {image_url, caption = column F + blank line + column G}
   - `create_story` {image_url}
   - reel days: `create_video_post` {video_url, caption, share_to_feed: true}
8. Set Status (column I) to `Posted`, or to `Skipped` with the reason if something failed.
9. If no row exists for today (after 15 Dec 2026), write a new row in the same style (rotate: dye spotlight,
   education, myth vs fact, sustainability, customer inspiration, behind the scenes, fun fact) and append it to the sheet first.

## Special cases (one-off, launch weekend)
- **15 Nov 2026:** there is no row. The 16 Nov feed post went live early, at 00:30 on 15 Nov, as a test.
  Post only a story today, using the 16 Nov row's story idea. Do not post a feed image and do not add a row.
- **16 Nov 2026:** the feed post is already live (Status says `Ready`). Post only the reel and a story,
  and write a fresh story question in the same style instead of repeating yesterday's. Then set Status to `Posted`.

## Rules
- Only make claims that are already in the calendar or that are well established about natural dyes. No prices, no certifications.
- Never put price lists, customer names or files in this repo: it is public.
- If posting fails twice, stop and report the error. Don't keep retrying.
