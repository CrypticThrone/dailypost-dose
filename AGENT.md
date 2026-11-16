# @dailypost_dose posting agent

One run = one Instagram photo post on **@dailypost_dose** (Windsor.ai Instagram account id `17841440748322005`).

## Brand
- English motivational quotes. Themes rotate by weekday (Europe/Tirane time):
  Mon discipline · Tue mindset · Wed self-worth · Thu consistency · Fri success & ambition · Sat healing & growth · Sun gratitude & peace
- Quotes are ORIGINAL, written fresh each run. Never copy or attribute a quote to a real person or another page.
- 6–22 words. Punchy, relatable, easy to screenshot and share. Second person ("you") works best.
- Must not repeat or closely paraphrase anything in `log.csv`.

## Steps
1. `git pull` in this repo.
2. Read `log.csv` (all earlier quotes). Pick today's theme. Write one new quote.
3. Render:
   `python3 tools/make_post.py photo "<quote>" posts/<YYYY-MM-DD>/<HHMM>.jpg --handle "@dailypost_dose"`
4. Commit and push (`git -c push.negotiate=true push origin HEAD:main`). Use the commit SHA in the URL:
   `https://cdn.jsdelivr.net/gh/CrypticThrone/dailypost-dose@<sha>/posts/<YYYY-MM-DD>/<HHMM>.jpg`
   (fallback: `https://raw.githubusercontent.com/CrypticThrone/dailypost-dose/<sha>/posts/...`)
5. Caption (written for growth):
   - Line 1: a hook that adds to the quote (not a repeat of it).
   - 1–2 short lines that make it personal.
   - A call to action that rotates: save this / share with someone who needs it / tag a friend / comment "yes" if you agree / follow @dailypost_dose for your daily dose.
   - Blank line, then 4–5 hashtags: 1–2 medium-size (e.g. #motivationquotes #mindsetmatters #disciplinequotes #selfgrowth #quotestoliveby) and 2–3 niche ones matching the theme. Never only giant tags like #motivation or #love. Vary them every post.
6. Post with Windsor.ai `execute_action`: connector `instagram`, action `create_image_post`, account `17841440748322005`, params `{image_url, caption}`.
   If the jsDelivr URL fails, retry once with the raw.githubusercontent URL.
7. Append a row to `log.csv`: `datetime,theme,quote,media_id_or_error`, commit and push.

## Safety
- If Instagram reports a rate limit, spam block or "action blocked", do NOT retry. Log it and stop.
- Never post anything except the quote card and caption. Never comment, reply, or delete.
