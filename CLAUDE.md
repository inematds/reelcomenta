# reelcomenta

Link de reel de terceiro → reel 9:16 com o avatar do Nei comentando, números com fonte e fecho nos cursos grátis do inema.club.
Fluxo completo em `skill/SKILL.md` (ligado em `~/.claude/skills/reelcomenta`). Código: `reelcomenta.py`.

- Autor dos commits: `inematds <inematds@gmail.com>`. Push do workflow do Pages via SSH (`git@github.com:inematds/reelcomenta.git`).
- Mídia (reel, avatar, build, vídeos) fica fora do git (`.gitignore`); só `roteiro.yaml`, prévias leves e o código entram.
- Avatar: estúdio do HeyGen pela assinatura (`explicavideos/engine/heygen-studio.mjs`), nunca API de geração; precisa de `avatar/APROVADO_HEYGEN`.
- Depende de: cardshorts (transcrição/norm/envio Telegram), explicavideos (estúdio HeyGen + leitura de status), inemavox (download), ffmpeg, Pillow, OpenCV, PyYAML.

## Self-learning

When I correct you, or you catch yourself making a mistake: before continuing, add the lesson as a one-line rule under ## Lessons, so it never happens again.

## Lessons

- O enquadramento do TEMPLATE-AVATAR16 muda de um vídeo para outro (alerta-sul 900:1020:510:0, robô 954:1080:653:0): o recorte do rosto é automático (OpenCV); se a conferência mostrar a cabeça cortada, fixe `recorte_avatar: "w:h:x:y"` no roteiro. (09/10/2026)
