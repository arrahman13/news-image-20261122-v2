# The World in One Day — Sunday 22 November 2026

[![Competition](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![Rank](https://make.fun/badge/news-image-20261122/arrahman13/news-image-20261122-v2/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![Reward](https://make.fun/badge/news-image-20261122/arrahman13/news-image-20261122-v2/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A one-page broadsheet that sums up the world news of **Sunday 22 November
2026** in a single 1024×1024 image: **37 stories** — 3 illustrated leads,
13 illustrated cards and 21 briefs — across 7 regions, with a stat strip,
a UTC timeline, a region tally, a world map whose numbered pins match the
story numbers, and a date-check box listing the stories deliberately left
out as other days' news.

Certainty discipline: every lead carries a tag — **REPORTED** (carried by
the day's wires), **CLAIM** (one side's account) or **FORECAST** (still to
happen) — and the briefs use the same labels.

Every story names its outlet (Reuters, BBC, Al Jazeera, AP, The Guardian,
info.gov.hk, ESPNcricinfo, Formula1.com, RFE/RL and others). All pictures
and the map are original, drawn in code — no photos, no downloads.

## Run it

```sh
python3 build_image.py     # renders entry.png (needs Python 3 + Pillow)
python3 main.py            # copies entry.png into ./output/
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
```

Deterministic: two runs of build_image.py produce byte-identical PNGs.
No network, no randomness, no timestamps. main.py uses only the
standard library and verifies the copied page by SHA-256.

Entry for the make.fun bounty
[news-image-20261122](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122).
