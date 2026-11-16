# @dailypost_dose posting agent — "Did you know?" world curiosities

One run = one Instagram photo post on **@dailypost_dose** (Windsor.ai Instagram account id `17841440748322005`).
Photo posts only. No reels, no music.

## Brand
- "Did you know?" facts: surprising, true curiosities from all over the world.
- Categories rotate by weekday (Europe/Tirane time):
  Mon animals & nature · Tue human body & science · Wed history · Thu space & planet Earth ·
  Fri countries & cultures · Sat geography & world records · Sun food, language & inventions
- Mix countries and continents. Don't post only US/UK facts.
- Card text: 15–40 words, plain English, one clear fact plus (optionally) the "why" behind it.
- Must not repeat or closely restate any fact in `facts.csv`.

## Accuracy rule (most important)
Every fact must be 100% verified before it is posted. If any doubt remains, drop it and pick another fact.
1. Use WebSearch / WebFetch to confirm the fact in **at least 2 independent, reliable sources**:
   encyclopedias (Britannica), science/government bodies (NASA, NOAA, NIH, USGS, national museums, UNESCO),
   universities, peer-reviewed journals, established news outlets (BBC, Reuters, AP, National Geographic, Smithsonian).
   Never count Wikipedia alone, content farms, "fun facts" listicles, social posts or AI-written pages as sources.
2. Avoid known myths and "too good to be true" facts (e.g. Great Wall visible from space, goldfish 3-second memory,
   humans use 10% of the brain, Napoleon was short). If a fact is widely disputed or "debunked" anywhere reputable, skip it.
3. Numbers, dates and names must match the sources exactly. Prefer stable facts over ones that change (records, populations, "largest/tallest" claims need a current source).
4. Word the card no stronger than the sources do ("about", "up to", "scientists believe" where the sources hedge).
5. Put the primary source's short name on the card (`--source`) and both source URLs in `facts.csv`.

## Steps
1. `git pull` in this repo.
2. Read `facts.csv` (all earlier facts). Pick today's category. Find and verify one new fact (Accuracy rule).
3. Render:
   `python3 tools/make_post.py fact "<fact>" posts/<YYYY-MM-DD>/<HHMM>.jpg --handle "@dailypost_dose" --category "<Category>" --source "<Source name>"`
   Look at the image before posting: text fully visible, nothing cut off.
4. Commit and push (`git -c push.negotiate=true push origin HEAD:main`). Use the commit SHA in the URL:
   `https://cdn.jsdelivr.net/gh/CrypticThrone/dailypost-dose@<sha>/posts/<YYYY-MM-DD>/<HHMM>.jpg`
   (fallback: `https://raw.githubusercontent.com/CrypticThrone/dailypost-dose/<sha>/posts/...`)
5. Caption (written for growth):
   - Line 1: a curiosity hook that doesn't just repeat the card (e.g. "This one sounds fake, but it isn't 👀").
   - 1–3 short lines with one extra verified detail or context.
   - `Source: <name>` line.
   - A call to action that rotates: "Did you know this? Comment YES or NO" / save it for your next trivia night /
     send this to someone who loves random facts / follow @dailypost_dose for a new fact every day.
   - Blank line, then 4–5 hashtags: 1–2 medium (e.g. #didyouknow #funfacts #factsdaily #learnsomethingnew #triviatime)
     and 2–3 niche tags for the topic (e.g. #oceanlife #spacefacts #historybuff #worldcultures). Vary them every post.
6. Post with Windsor.ai `execute_action`: connector `instagram`, action `create_image_post`, account `17841440748322005`,
   params `{image_url, caption}`. If the jsDelivr URL fails, retry once with the raw.githubusercontent URL.
7. Append a row to `facts.csv`: `datetime,category,fact,source_urls,media_id_or_error`
   (source_urls separated by ` | `), commit and push.

## Safety
- If Instagram reports a rate limit, spam block or "action blocked", do NOT retry. Log it and stop.
- Never post anything except the fact card and caption. Never comment, reply, or delete.
- No politics, religion-bashing, tragedies used as "fun facts", medical advice, or facts about living private people.
