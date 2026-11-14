# Daily Instagram run – @naturaldye.sbpl (Sodhani Biotech)

Runs every day at 10:45 AM IST. Everything goes live around 11:00 AM IST.

## Sources
- **Content calendar (Claude Sheet):** https://claude.ai/artifact/HTdVQ7A7B3nFEagTpuqBGm
  (artifact id `854a0b4a-e650-44b5-a82e-42fdb42b9d1a`, sheet `Calendar`).
  Columns: A Date, B Day, C Feed post topic, D Reel (Mon/Wed/Fri), E Story, F Caption, G Hashtags, H Post time, I Status.
- **Instagram:** Windsor.ai for Social Media connector, connector `instagram`, account `17841468411588839`.
- **Media hosting:** this repo. Public URL pattern:
  `https://raw.githubusercontent.com/organic-ctrl/naturaldyes-social/main/<path>`

## Product knowledge (READ FIRST)
`data/products.json` is the single source of truth: 27 extract products (source, Latin name, part used,
fresh/waste, antibacterial flag, shade hex), 29 natural dyes, 11 mordants and the company facts (40% lower carbon footprint,
80% lesser ETP cost, wastewater BOD/COD/SS figures, 100% bio-based carbon (C-14), 30% from plant waste, 95% solvent recovery,
locations). `data/company-factsheet.jpg` is the original fact sheet.
- Every post and reel is about OUR products or OUR facts. Use exact product names (e.g. "Mallow Gold Extract", "Wine Red Extract 3001").
- Use each product's `shade` hex for swatches, fabric scenes and colour blocks so the colours match the real product.
- Never invent products, grades, prices, MOQs, certifications, fastness ratings or test results.
- Lac (Wine Red) and Cochineal are from insects: call them "natural", never "plant-based".
- Only the products flagged `antibacterial: true` may be called antibacterial.
- After 15 Dec, keep rotating through products that haven't had a spotlight yet (e.g. Michigan Brown, Garnet Brown,
  Bark Brown, Nut Brown, Onion Peel, Cedar Grey, Cochineal, Barn Red, Wisdom Orange, Crafty Brown, Heena, Kamala, Safflower,
  Primrose Yellow, Jonquil Yellow, Silver Oak/Jamun, Eupatorium) and company facts not yet covered.

## Steps
1. Find today's row (IST date) in the Calendar sheet. If Status is already `Posted`, stop.
2. **Feed post = a CAROUSEL** (the user's chosen format, from the reference posts they sent).
   Column C starts with e.g. `[carousel 7 slides · cover: question]`: make exactly that many slides (5, 7 or 10;
   Instagram's API allows 10 at most) with that cover type. Write `posts/YYYY-MM-DD/spec.json` and run
   `python3 tools/carousel.py posts/YYYY-MM-DD/spec.json posts/YYYY-MM-DD`. Slide types and fields: docstring of
   `tools/carousel.py`; full example: `tools/examples/carousel.json`.
   - Slide 1 = the cover type from column C (series / question / education / statement / boxed).
   - Middle slides tell the topic step by step: mix `point` slides (numbered facts) with `spotlight`
     (a dye or ingredient: English name, Hindi/local name, Latin name), `labels` (fibre, mordant or depth comparisons)
     and `statement` / `boxed`. Never two identical layouts in a row.
   - Last slide is always `end` with a CTA.
   - Text stays short: titles ≤ 6 words, bodies ≤ 25 words. Every slide must add something new.
   - Images: real photos from `photos/` first; otherwise generated scenes (`fabric`, `stack`, `powder`, `ecoprint`,
     `liquid`) or swatches. Use colours that match the dye being discussed, and a different seed on every slide.
   - Caption: column F plus "Swipe ➡️ to see all N" plus column G's hashtags. If the topic in C no longer matches F,
     write a fresh caption in the same voice.
   - Publish with `create_carousel_post` {image_urls: [all slide URLs in order], caption}.
   - Rows with no tag (after 15 Dec): keep cycling 5 → 7 → 10 slides and the 5 cover types, with fresh topics that
     haven't been used (check `posts/` for past spec.json titles).
3. **Story:** `python3 tools/make_media.py story stories/YYYY-MM-DD.jpg "<kicker>" "<question or fact>" "<short line>"`.
   The API can't add poll, quiz or question stickers, so write the story as a question card ("Reply in DMs / comment on today's post").
4. **Reel (Mon/Wed/Fri only, when column D has text):** column D starts with the style in brackets,
   e.g. `[quiz] Guess the plant…`. Write `reels/YYYY-MM-DD.json` for that style, then run
   `python3 tools/reels.py reels/YYYY-MM-DD.json reels/YYYY-MM-DD.mp4`.
   Styles and their JSON fields are in the docstring of `tools/reels.py`; working examples are in `tools/examples/`.
   - **`photostory` is the user's favourite style and the default** (modelled on a reference reel they sent):
     run `python3 tools/photostory.py reels/YYYY-MM-DD.json reels/YYYY-MM-DD.mp4` instead of reels.py.
     Spec format: docstring of `tools/photostory.py`, example `tools/examples/photostory.json`.
     Hook = 2 short lines + a question; title card = two big words + an italic line; 5–7 chapters, each ONE word with
     a full stop ("Fold.", "Soak.", "Extract.") plus a ≤7-word gold sub-line; end card = two-line slogan + CTA.
     Images: use real photos from `photos/` whenever there are any that fit (vary them; don't reuse the same photo
     two reels in a row). Otherwise use generated swatches `{"swatch": ..., "color": ..., "seed": N}` with a
     different seed each time and colours that match the dye being talked about.
     Music is generated inside the tool (original, no licensing).
   - `pour`: colour flowing over white fabric. Use realistic dye colours (indigo #1f3a68, madder #a8322d, pomegranate #c99a2e, catechu #6b4a2b, marigold #d9a21b).
   - `quiz`: guess the plant or colour. End the caption with "Comment your answer before you watch the end! 👇".
   - `mythfact`: 2–3 myth/fact pairs.
   - `top3`: three short items (max ~6 words each).
   - `compare`: 3–5 rows. Natural vs synthetic, or extracts vs raw powders.
   - `steps`: a mini workshop / dyeing process in 3–5 short steps.
   - `news`: search the web for a REAL recent (last ~30 days) news item about natural dyes, plant-based colour,
     textile dyeing pollution or sustainable textiles, from a reputable outlet. Paraphrase it in your own words
     (headline ≤ 12 words, summary ≤ 30 words) and put the outlet and date in `source`. Name the source in the caption too.
     Never invent news. If nothing suitable is found, use a `top3` about the benefits of natural dyes instead.
   - If D has no style tag (e.g. after 15 Dec): use `photostory` on Mondays and Fridays; on Wednesdays use one of the
     other styles, whichever was used least recently. Pick a fresh topic each time:
     dyeing process, mini workshops, natural vs synthetic, dye extracts, benefits, mordants, colour sources, or news.
   Write a reel caption: 1–2 hooky lines, a question or CTA, then the same hashtags as the day's post.
5. Look at each image (and 3–4 frames of the reel, grabbed with ffmpeg). Check that the text fits and nothing is cut off.
6. `git add`, commit, and push to `main` (use `git -c push.negotiate=true push origin HEAD`).
   Wait ~30 s, then check that each raw URL returns HTTP 200.
7. Publish with Windsor `execute_action`:
   - `create_carousel_post` {image_urls, caption} (see step 2)
   - `create_story` {image_url}
   - reel days: `create_video_post` {video_url, caption, share_to_feed: true}
8. Set Status (column I) to `Posted`, or to `Skipped` with the reason if something failed.
9. If no row exists for today (after 15 Dec 2026), write a new row in the same style (rotate: dye spotlight,
   education, myth vs fact, sustainability, customer inspiration, behind the scenes, fun fact) and append it to the sheet first.

## Special cases (one-off, launch weekend)
- **15 Nov 2026:** there is no row. The 16 Nov feed post went live early, at 00:30 on 15 Nov, as a test.
  Post only a story today, using the 16 Nov row's story idea. Do not post a feed image and do not add a row.
- **16 Nov 2026:** the feed post AND the reel are already live (both posted as tests on 15 Nov). Post only a story:
  write a fresh story question in the same style instead of repeating yesterday's. Then set Status to `Posted`.

## Reel concepts must never repeat
Every reel has a different concept, as the user asked. Before writing a reel, list the concepts already used:
reel JSON files in `reels/` plus column D of the calendar. Don't repeat a concept, and don't reuse the same hook
line or chapter words. Concepts used so far:
plant waste to colour (text cards, 16 Nov) · onion peel: kitchen waste to yellow (photostory, posted 15 Nov) · fibre test · shibori story · indigo leaf to blue · natural vs synthetic ·
dye-source tour · mordants · news · plant waste to colour (photostory) · mini workshop: using an extract ·
over-dyeing quiz · wedding-season palette · year in colour 2026.
Fresh ideas for after 15 Dec: myth vs fact, top 3 benefits, the science of colour fastness, water & ETP savings,
farmers behind the dyes, extracts vs raw powders, block printing with natural dyes, colour of the month,
dyeing at home vs at mill scale, how to store dye extracts, eco-printing with leaves, indigo vat chemistry made
simple, Holi/festival colours, customer creations.

## Rules
- Only make claims that are already in the calendar or that are well established about natural dyes. No prices, no certifications.
- Never put price lists, customer names or files in this repo: it is public.
- If posting fails twice, stop and report the error. Don't keep retrying.
