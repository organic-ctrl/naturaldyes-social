# Daily Instagram run – @naturaldye.sbpl (Sodhani Biotech)

Runs every day at 10:45 AM IST. Everything goes live around 11:00 AM IST.

## Sources
- **Content calendar (Claude Sheet):** https://claude.ai/artifact/HTdVQ7A7B3nFEagTpuqBGm
  (artifact id `854a0b4a-e650-44b5-a82e-42fdb42b9d1a`, sheet `Calendar`).
  Columns: A Date, B Day, C Feed post topic, D Reel (Mon/Wed/Fri), E Story, F Caption, G Hashtags, H Post time, I Status.
- **Instagram:** Windsor.ai for Social Media connector, connector `instagram`, account `17841468411588839`.
- **Media hosting:** this repo. Public URL pattern:
  `https://raw.githubusercontent.com/organic-ctrl/naturaldyes-social/main/<path>`

## Style references (added 26 Nov at the user's request)
The user wants future carousels and reels to take their style from these Instagram profiles:
- https://www.instagram.com/florilegiumparis
- https://www.instagram.com/the_sustainable_artist
Instagram blocks automated viewing, so the runs can't open them. Use them as STYLE reference only (look, layout,
pacing, hooks, text style). Never copy their photos, videos, captions or music. Write the concrete style notes
below once the user sends screenshots or screen recordings, and follow them in steps 2 and 4.
Style notes (from 2 reference reels the user sent on 27 Nov; written from the videos, nothing copied):
- **Real material first, words second.** Reel A (~30 s) is plain handheld process footage, shot from above in daylight:
  dry dye material in a steel pot → the bath boiling → white cloth dipped and lifted out coloured → the finished
  fabric held in a hand. Then the same arc again for a second dye. There's no title card, no end card and no
  big text. The only on-screen text is one tiny white italic label per ingredient ("English name / local name"),
  centred, shown for 2–3 s.
- **Pacing:** one shot every ~2.5–5 s, hard cuts, 20–30 s in all. The colour change (white cloth → coloured) is the hero moment.
- **Reel B (~7 s), a collage build:** a photo of a bare tree against a blue sky. Fabric swatches cut into leaf-like
  pieces pop in one by one until the branches are covered in naturally dyed cloth. One short line of white caps
  text sits in the centre for the first half. Ends on a calm brand card: logo on textured off-white paper with a few
  hand-drawn flowers.
- **What this means for us:**
  1. Text on screen: max ~6 words at a time, small and elegant. Put the facts (Latin name, grades, source) in the CAPTION, not on screen.
  2. Prefer showing a transformation (raw material → bath → cloth) over talking about it.
  3. Real photos/clips from `photos/` beat generated swatches every time. We have none yet, so this is the biggest gap (see the summary under "Needs Aman").
  4. Short collage/build reels (7–12 s, our shades as cut fabric pieces filling a shape) are a good alternate format.
  5. End card: quiet and branded (off-white paper, logo or name, one CTA), not a busy info card.
  6. Carousels: same rules. Fewer words per slide, more full-bleed colour/fabric, facts in the caption.

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
3b. **Second story: a different TYPE every day** (added 25 Nov at the user's request: "daily different type of story
   on Instagram related to natural dye, natural food colors news"). Post it right after the calendar story.
   Write `stories/specs/YYYY-MM-DD-b.json` and run `python3 tools/stories.py stories/specs/YYYY-MM-DD-b.json stories/YYYY-MM-DD-b.jpg`.
   Types, fields and examples: docstring of `tools/stories.py` and `tools/examples/stories/`. Rotation by weekday (IST):
   - Mon `news` topic `dye`: natural dyes / plant-based colour / sustainable textiles / dyeing pollution
   - Tue `didyouknow`: one fact from data/products.json (company facts, a product's source or Latin name)
   - Wed `news` topic `food`: natural food colours (synthetic dye phase-outs, new plant colourants, market news)
   - Thu `mythfact`: one natural-dye myth vs fact
   - Fri `news` topic `dye`
   - Sat `spotlight` (one extract, its `shade` hex, source, Latin name; rotate, don't repeat a recent one) or `thisorthat` (two of our shades)
   - Sun `news` topic `food`, or `stat` (one company number) if no good food-colour news
   News rules: search the web for a REAL item from the last ~14 days (max 30) from a reputable outlet; read the article;
   paraphrase (headline ≤ 12 words, summary ≤ 30 words); `source` = "Outlet · D Mon YYYY"; never invent news;
   don't reuse a story already used (check `stories/specs/`). If nothing suitable, use `didyouknow` instead.
   Food-colour news: we make TEXTILE dyes. Never say or imply our products are food colours, food-grade or edible.
   Use the `ask` line to bridge to textiles or ask a question (e.g. "Food is going natural. Should textiles be next?").
   Publish with `create_story` {image_url} (raw URL of stories/YYYY-MM-DD-b.jpg). If it fails, the day still counts as Posted;
   note the failure in the summary.
4. **Reel (Mon/Wed/Fri only, when column D has text):** column D starts with the style in brackets,
   e.g. `[quiz] Guess the plant…`. Write `reels/YYYY-MM-DD.json` for that style, then run
   `python3 tools/reels.py reels/YYYY-MM-DD.json reels/YYYY-MM-DD.mp4`.
   Styles and their JSON fields are in the docstring of `tools/reels.py`; working examples are in `tools/examples/`.
   - **`collage` is now the DEFAULT reel style (user, 27 Nov: "make them like these reference reels, but a different
     concept every day – not a tree every day").** Run `python3 tools/collage.py reels/YYYY-MM-DD.json reels/YYYY-MM-DD.mp4`.
     Spec: docstring of `tools/collage.py`; examples in `tools/examples/collage/`. Keep the TOPIC from column D, but tell it
     as a collage: our product shades as cut fabric pieces filling a shape, 1–3 short caps lines, tiny colour labels, calm end card.
     **Every reel needs a NEW concept** = a new shape + background + idea that fits the topic. Shapes: tree, leaf, kurta, pot,
     lotus, drop, heart, mandala, sun, butterfly, or `word` (any 1–2 short words, e.g. JAIPUR, LAC, INDIGO, WASTE→COLOUR, 2027).
     Never use the same shape two reels in a row, never the same shape+idea twice, and rotate backgrounds
     (sky, paper, dusk, wall, indigo, sand). Ideas: the shape should mean something for the topic (a drop for wastewater,
     a pot for the dye bath, a kurta for "wear it", the product name as a `word`, a leaf for plant sources, a heart for "thank you").
     Pick colours from data/products.json `shade` hexes, 3–6 per reel, with name labels like "Wine Red 3001 · lac".
     If a shape that fits the idea doesn't exist yet, add it to `tools/collage.py` (a mask function in SHAPES) and test it.
     Add the concept to "Collage concepts used" below.
   - When real process clips/photos exist in `photos/`, use `photostory` (or a cut of the real clips) for process topics
     (raw material → bath → coloured cloth), as in the user's sappanwood reference reel.
   - **`photostory`** (the user's earlier favourite) (modelled on a reference reel they sent):
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
   - If D has no style tag (e.g. after 15 Dec): use `collage` (new concept) on Mondays and Fridays; on Wednesdays use one of the
     other styles, whichever was used least recently. Pick a fresh topic each time:
     dyeing process, mini workshops, natural vs synthetic, dye extracts, benefits, mordants, colour sources, or news.
   Write a reel caption: 1–2 hooky lines, a question or CTA, then the same hashtags as the day's post.
5. Look at each image (and 3–4 frames of the reel, grabbed with ffmpeg). Check that the text fits and nothing is cut off.
6. `git add`, commit, and push to `main` (use `git -c push.negotiate=true push origin HEAD`).
   Wait ~30 s, then check that each raw URL returns HTTP 200.
7. Publish with Windsor `execute_action`:
   - `create_carousel_post` {image_urls, caption} (see step 2)
   - `create_story` {image_url}
   - second story: `create_story` {image_url} (step 3b)
   - reel days: `create_video_post` {video_url, caption, share_to_feed: true}
8. Set Status (column I) to `Posted`, or to `Skipped` with the reason if something failed.
9. If no row exists for today (after 15 Dec 2026), write a new row in the same style (rotate: dye spotlight,
   education, myth vs fact, sustainability, customer inspiration, behind the scenes, fun fact) and append it to the sheet first.

## Special cases (one-off, launch weekend)
- **15 Nov 2026:** there is no row. The 16 Nov feed post went live early, at 00:30 on 15 Nov, as a test.
  Post only a story today, using the 16 Nov row's story idea. Do not post a feed image and do not add a row.
- **16 Nov 2026:** the feed post AND the reel are already live (both posted as tests on 15 Nov). Post only a story:
  write a fresh story question in the same style instead of repeating yesterday's. Then set Status to `Posted`.

## Comments & leads (do this every run, after publishing)
1. Read comments from the last 3 days with Windsor `get_data` (connector `instagram`, fields
   `comment_id, comment_text, comment_username, comment_timestamp, comment_parent_id, comment_reply_count, media_id, media_permalink`,
   `date_preset: "last_7d"`). Skip comments that already have a reply from @naturaldye.sbpl (comment_reply_count > 0
   or our reply in the thread) and comments written by @naturaldye.sbpl itself.
2. Reply with `reply_to_comment` {comment_id, message}:
   - Questions about price, MOQ, samples, shade card, export, bulk: thank them, give a one-line useful answer from
     data/products.json if it's there, and invite them to DM us or visit naturaldyes.io. NEVER quote prices, MOQs,
     delivery times or certifications.
   - Product questions: answer only from data/products.json (source, Latin name, grades, antibacterial flag).
   - Praise or emojis: a short, warm thank-you (vary the wording; never copy-paste the same reply).
   - Reply in the language of the comment (Hindi/Hinglish → Hinglish; English → English).
   - Keep replies under 200 characters, friendly and professional, max 1 emoji. Sign nothing.
3. Spam, scams, abuse, "promote your page", crypto, adult content: `hide_comment` (never delete).
4. Unsure or sensitive (complaints, quality issues, payment, legal, competitors)? Do NOT reply. List it under
   "Needs Aman" in the run summary.
5. Leads: anyone asking about price, samples, MOQ, bulk, export, distributorship or "interested". List each one in the
   run summary as: @username · what they asked · post link. Also append it as a new row to the ONE master leads
   sheet, the Claude Sheet "India Leads – Sodhani Biotech" https://claude.ai/artifact/PNVtQLx478Wcg5jePp8c3M
   (sheet "Leads", columns A–X): A next S.No, B today, C best-fit product line, D @username, E "Instagram comment",
   L post link, M what they asked, O Status "New", Q the comment text; leave unknown columns blank. Skip it if that
   @username is already in column D. (User, 28 Nov: never make a new Excel/file for leads – always add to this one sheet.)

## Lead-friendly content rules
- Every caption ends with ONE clear call to action: "DM us for samples", "Comment SHADE for the shade card",
  "Save this for your next batch" or a question. Rotate them.
- Once a week (Thursdays) the carousel's last slide uses the CTA "Comment SAMPLE and we'll DM you".
- Hashtags: 8–12 per post, mixing broad (#naturaldyes #sustainablefashion), industry (#textiledyeing #dyehouse
  #textilemanufacturing) and local (#jaipur #madeinindia #rajasthan). Vary them; never post the exact same set twice in a row.

## Reel concepts must never repeat
Every reel has a different concept, as the user asked. Before writing a reel, list the concepts already used:
reel JSON files in `reels/` plus column D of the calendar. Don't repeat a concept, and don't reuse the same hook
line or chapter words. Concepts used so far:
plant waste to colour (text cards, 16 Nov) · onion peel: kitchen waste to yellow (photostory, posted 15 Nov) · fibre test · shibori story · indigo leaf to blue · natural vs synthetic ·
dye-source tour · mordants · news · plant waste to colour (photostory) · mini workshop: using an extract ·
over-dyeing quiz · wedding-season palette · year in colour 2026 ·
three oranges, one seed: annatto grades (pour, 18 Nov) · pomegranate peel to Mallow Gold (photostory, 20 Nov) · Esstebio Indigo: leaf to blue (photostory, 23 Nov) · wastewater numbers BOD/COD/SS: natural vs synthetic (compare, 25 Nov) · lac: resin & waste water to Wine Red (photostory, 27 Nov).
Fresh ideas for after 15 Dec: myth vs fact, top 3 benefits, the science of colour fastness, water & ETP savings,
farmers behind the dyes, extracts vs raw powders, block printing with natural dyes, colour of the month,
dyeing at home vs at mill scale, how to store dye extracts, eco-printing with leaves, indigo vat chemistry made
simple, Holi/festival colours, customer creations.

## Collage concepts used (never repeat a shape+idea; never the same shape twice in a row)
(none yet – first collage reel is due Mon 30 Nov. tools/examples/collage/ holds test examples only: tree/waste colours,
word JAIPUR, lotus pinks – those three ideas count as used, so don't post them as they are)

## Rules
- Only make claims that are already in the calendar or that are well established about natural dyes. No prices, no certifications.
- Never put price lists, customer names or files in this repo: it is public.
- If posting fails twice, stop and report the error. Don't keep retrying.
