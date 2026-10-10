# reelcomenta

[![reelcomenta](guia/assets/banner-en.jpg)](https://inematds.github.io/reelcomenta/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## What it is

reelcomenta is a command-line tool that takes the link of someone else's reel, TikTok or Short and builds a vertical video of your own commenting on that topic. The original video keeps playing, with its music turned down. Your HeyGen avatar speaks in a corner of the screen, the numbers from your research appear in a panel with their source, and the video ends with a question and a call to the free courses at inema.club. It is for people who produce content and want to ride a video that is already circulating, without recording anything. It needs Python, ffmpeg, a HeyGen account with your avatar, and the cardshorts and explicavideos projects.

## 📖 User guide

Full guide (landing + step by step): **https://inematds.github.io/reelcomenta/guia/en/**

## The format

| Time | On screen | Audio |
|---|---|---|
| Frame 0 | date dd/mm/yyyy + headline + the reel already running | reel music, low |
| Numbers | panel with counter and source, on the exact word of the speech; the best excerpt of the reel in slow motion | avatar speaks, music lowers by itself |
| Question | "ESPERAR" struck through → "OU SE QUALIFICAR" | "will you keep waiting or will you get qualified?" |
| Closing | mosaic of the real course covers + INEMA.CLUB card | "+300 free courses… start today" |

The avatar sits at the bottom right (400×453, amber frame and name), automatically cropped to the face (OpenCV). Captions come word by word, from the transcription of the avatar's own speech.

## Usage

```bash
python3 reelcomenta.py novo "<link>" --id assunto      # downloads, transcribes, frame sheet, roteiro.yaml
# write edicoes/<date>-assunto/roteiro.yaml (speech + cards with source)
python3 reelcomenta.py previa  edicoes/<pasta>          # previa.jpg with estimated timing
echo "aprovado" > edicoes/<pasta>/avatar/APROVADO_HEYGEN
python3 reelcomenta.py avatar  edicoes/<pasta>          # HeyGen studio, waits and downloads
python3 reelcomenta.py montar  edicoes/<pasta>          # video.mp4
python3 reelcomenta.py conferir edicoes/<pasta>         # conferencia.jpg + volume
python3 reelcomenta.py enviar  edicoes/<pasta> "texto"  # Telegram bot
```

Full example: [`edicoes/2026-10-09-robo-trabalho/roteiro.yaml`](edicoes/2026-10-09-robo-trabalho/roteiro.yaml).

For Claude Code or Codex, the skill is at [`skill/SKILL.md`](skill/SKILL.md): with it, you just send the link.

## Dependencies

- Python 3 with Pillow, PyYAML and OpenCV; ffmpeg; yt-dlp.
- [cardshorts](https://github.com/inematds/cardshorts): local transcription with per-word timing and delivery to Telegram.
- [explicavideos](https://github.com/inematds/explicavideos): HeyGen studio through the browser (no generation API) and status reader.
- Paths via variables: `RC_CARDSHORTS`, `RC_EXPLICAVIDEOS`, `RC_PERFIL_HEYGEN`, `RC_TEMPLATE_HEYGEN`, `RC_PORTAL_DADOS`, `RC_CAPAS`, `RC_MUSICA`, `RC_DISPLAY`.

## Editions

| Date | Edition | What it shows |
|---|---|---|
| 10/09/2026 | `edicoes/2026-10-09-robo-trabalho` | robot dancing on stage → 92 million jobs (World Economic Forum), 41% of companies, 1 in 5 cutting middle management (Gartner), 542 thousand robots (IFR) |

MIT license. The third-party video used in each edition remains its author's; the numbers follow the cited sources.
