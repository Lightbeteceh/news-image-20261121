# news-image-20261121 — The World in One Day

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Lightbeteceh/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Lightbeteceh/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

An entry for the [make.fun news-image-20261121 bounty](https://make.fun/bounty/news-image-20261121)
("Sum up 21 November's world news in one image", $100 USDC, 50 places paid).

It sums up the world news of **Saturday 21 November 2026** in a single
picture: 45 stories from 6 continents, led by Russia's biggest air raid
of the year on Kyiv.

## How it works

The picture is a "Zenith" front page, drawn by `render.py` (Python 3 +
Pillow, offline) from the headlines in `stories.json`:

- a dark navy masthead with the date and the story count;
- a red ticker tape carrying the day's market numbers (Friday closes);
- a circular world globe with ten numbered pins on the places that
  mattered most (Kyiv, Poland, Antalya, Gaza, Gopalpur, Shenzhen,
  Tokyo, New York, Lima, Cook Islands), facing a large lead hero
  with the day's biggest story and three key facts;
- six tall continent columns running down the page, each with its
  own coloured header and its headlines stacked vertically.

The Merriweather typefaces are bundled in `fonts/`, so rendering needs
no system fonts and no network. `main.py` then copies `entry.png` to
`/output/entry.png` byte-for-byte.

```sh
python3 render.py   # rebuild entry.png from stories.json (offline)
python3 main.py     # write /output/entry.png (deterministic, no network)
```

## Rules compliance

- Image: PNG, 1024×1024, well under 1 MiB.
- No network at run time (`main.py` only copies a local file).
- Deterministic: two runs of `render.py` and two runs of `main.py`
  produce identical bytes (verified by sha256). If a headline ever
  overflows its column, `render.py` fails loudly instead of clipping text.

## Status

DRAFT (21 Nov 2026, ~16:45 WIB): repo and pipeline are ready; the draft
image uses headlines from the morning of 21 Nov, while the news day is
still running. The final image — full-day headlines, re-verified — is
rendered on 22 Nov 2026. Deadline: 23 Nov 2026, 07:00 WIB.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
