# @dailypost_dose comic agent

One run = one comic strip photo post on **@dailypost_dose** (Windsor.ai Instagram account id `17841440748322005`). English, original jokes only.

## Cast (drawn by tools/characters.py — do not invent new looks)
- **Benny** – teal shirt, glasses, hair tuft. The overthinker. Has a plan B for his plan B.
- **Lula** – yellow dress, bun with pink bow. Sassy, always right (ask her).
- **Uncle Gjon** – red shirt, blue cap, mustache. King of dad jokes nobody asked for.
- **Mimi** – purple shirt, pink headphones, ponytail. Professional napper, allergic to Mondays.
- **Tito** – green shirt, sprout on his head. The relentless optimist.
Keep personalities consistent so followers get attached. Rotate who stars; use 2 characters per strip (sometimes 3).

## Jokes
- Relatable everyday humour: work, Mondays, coffee, sleep, gym, diets, texting, family, adulting, money, weekends, holidays/seasons (check today's date in Europe/Tirane).
- Clean and kind: no politics, religion, race, body shaming, real people, brands, or other comics' characters or jokes. Write every joke fresh.
- Setup → build → punchline in the LAST panel. Short lines (max ~10 words per bubble, max 2 bubbles per panel).
- Must not repeat a joke or premise already in `comics_log.csv`.

## Steps
1. `git pull`. Read `comics_log.csv`.
2. Write a script JSON (format in the docstring of `tools/comic.py`): 3 panels (stacked) or 4 panels (2x2). Optional short title (2–4 words). Pick poses/faces that sell the joke (shock/facepalm on the punchline works well). Keep speakers at x≈0.33 and 0.67.
3. Render: `cd tools && python3 comic.py ../comics/<YYYY-MM-DD>/<HHMM>.json ../comics/<YYYY-MM-DD>/<HHMM>.jpg`
   Then LOOK at the image (Read it). If any bubble covers a face, text runs off the panel, or bubbles overlap, fix the script (shorter lines, move x) and re-render.
4. Commit + push (`git -c push.negotiate=true push origin HEAD:main`). Image URL:
   `https://cdn.jsdelivr.net/gh/CrypticThrone/dailypost-dose@<sha>/comics/<YYYY-MM-DD>/<HHMM>.jpg`
   (fallback `https://raw.githubusercontent.com/CrypticThrone/dailypost-dose/<sha>/comics/...`)
5. Caption for growth: a one-line hook ("Who else is a Mimi on Mondays? 🙋"), a question that invites comments, a rotating call to action (tag the friend who's a Benny / share with your work bestie / follow @dailypost_dose for daily laughs), blank line, 4–5 varied hashtags (e.g. #relatablecomics #funnycomics #webcomic #comicstrip #relatablememes #mondaymood — mix medium + niche, vary every post).
6. Post: Windsor.ai `execute_action`, connector `instagram`, action `create_image_post`, account `17841440748322005`, params `{image_url, caption}`.
7. Append to `comics_log.csv`: `datetime,characters,premise,media_id_or_error`, commit, push.

## Safety
- Rate limit / spam warning / "action blocked" → do not retry; log it and stop.
- Only post the comic. Never comment, reply, or delete.
