# reelcomenta

[![reelcomenta](guia/assets/banner.jpg)](https://inematds.github.io/reelcomenta/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## O que é

O reelcomenta é uma ferramenta de linha de comando que pega o link de um reel, TikTok ou Short de outra pessoa e monta um vídeo vertical seu comentando aquele assunto. O vídeo original continua passando, com a música dele baixa. O seu avatar do HeyGen fala num canto da tela, os números da sua pesquisa aparecem num painel com a fonte, e o vídeo termina com uma pergunta e a chamada para os cursos gratuitos do inema.club. É para quem produz conteúdo e quer surfar num vídeo que já está circulando, sem gravar nada. Precisa de Python, ffmpeg, uma conta HeyGen com o seu avatar e dos projetos cardshorts e explicavideos.

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/reelcomenta/guia/**

## O formato

| Tempo | Na tela | Áudio |
|---|---|---|
| Quadro 0 | data dd/mm/aaaa + manchete + o reel já rodando | música do reel, baixa |
| Números | painel com contador e fonte, na palavra exata da fala; o melhor trecho do reel em câmera lenta | avatar fala, música abaixa sozinha |
| Pergunta | "ESPERAR" riscado → "OU SE QUALIFICAR" | "vai ficar esperando ou vai se qualificar?" |
| Fecho | mosaico das capas reais dos cursos + cartão INEMA.CLUB | "+300 cursos gratuitos… começa hoje" |

O avatar fica embaixo à direita (400×453, moldura âmbar e nome), recortado no rosto automaticamente (OpenCV). A legenda vem palavra a palavra, a partir da transcrição da própria fala do avatar.

## Uso

```bash
python3 reelcomenta.py novo "<link>" --id assunto      # baixa, transcreve, folha de quadros, roteiro.yaml
# escreva edicoes/<data>-assunto/roteiro.yaml (fala + cartões com fonte)
python3 reelcomenta.py previa  edicoes/<pasta>          # previa.jpg com tempo estimado
echo "aprovado" > edicoes/<pasta>/avatar/APROVADO_HEYGEN
python3 reelcomenta.py avatar  edicoes/<pasta>          # estúdio do HeyGen, espera e baixa
python3 reelcomenta.py montar  edicoes/<pasta>          # video.mp4
python3 reelcomenta.py conferir edicoes/<pasta>         # conferencia.jpg + volume
python3 reelcomenta.py enviar  edicoes/<pasta> "texto"  # bot do Telegram
```

Exemplo completo: [`edicoes/2026-10-09-robo-trabalho/roteiro.yaml`](edicoes/2026-10-09-robo-trabalho/roteiro.yaml).

Para o Claude Code ou o Codex, a skill está em [`skill/SKILL.md`](skill/SKILL.md): com ela, basta mandar o link.

## Dependências

- Python 3 com Pillow, PyYAML e OpenCV; ffmpeg; yt-dlp.
- [cardshorts](https://github.com/inematds/cardshorts): transcrição local com tempo por palavra e envio para o Telegram.
- [explicavideos](https://github.com/inematds/explicavideos): estúdio do HeyGen pelo navegador (sem API de geração) e leitura de status.
- Caminhos por variável: `RC_CARDSHORTS`, `RC_EXPLICAVIDEOS`, `RC_PERFIL_HEYGEN`, `RC_TEMPLATE_HEYGEN`, `RC_PORTAL_DADOS`, `RC_CAPAS`, `RC_MUSICA`, `RC_DISPLAY`.

## Edições

| Data | Edição | O que mostra |
|---|---|---|
| 09/10/2026 | `edicoes/2026-10-09-robo-trabalho` | robô dançando no palco → 92 milhões de empregos (Fórum Econômico Mundial), 41% das empresas, 1 em 5 cortando gerência média (Gartner), 542 mil robôs (IFR) |

Licença MIT. O vídeo de terceiro usado em cada edição continua sendo do seu autor; os números seguem as fontes citadas.
