---
name: reelcomenta
description: >-
  Link de reel/TikTok/Short de terceiro → reel 9:16 do Nei comentando: o vídeo original passa com a
  música dele baixa, o avatar do Nei (HeyGen estúdio) fala no canto, números com fonte entram num
  painel, vem a pergunta "vai esperar ou vai se qualificar?" e o fecho com os cursos grátis do
  inema.club; entrega no bot v3. Gatilho: "/reelcomenta <link>", "pega este reel e comenta",
  "faz o reel comentado deste vídeo", ou um link de reel com pedido de avatar comentando.
---

# reelcomenta — link de reel vira o reel comentado do Nei

Repo: `~/projetos/reelcomenta` (inematds/reelcomenta). Tudo roda por `reelcomenta.py`.
O Nei autorizou (09/10/2026): **quando ele mandar o link, fazer o vídeo inteiro e entregar no bot v3**.
O avatar é pelo **estúdio do HeyGen pela assinatura** (sem API de geração, sem custo de crédito);
o pedido com o link é a aprovação — grave-a em `avatar/APROVADO_HEYGEN` com a frase dele e a data.

## Passo a passo

1. **Baixar e olhar.**
   `cd ~/projetos/reelcomenta && python3 reelcomenta.py novo "<link>" --id <assunto-curto>`
   Abra `edicoes/<data>-<id>/ref/folha.jpg` (12 quadros), `ref/transcricao.txt` e `ref/descricao.txt`.
   Entenda o que o vídeo mostra e qual ligação com trabalho/IA/carreira o Nei pediu.
2. **Pesquisar os números (3 a 4).** Fonte primária ou reconhecida (WEF, OIT, IBGE, McKinsey,
   Gartner, IFR, Goldman Sachs…), com ano. Projeção é projeção: escreva "prevê", "calcula".
   Anote as fontes no fim do `roteiro.yaml` em comentário. Número sem fonte não entra.
3. **Escrever o `roteiro.yaml`** (o `novo` já deixa o modelo; o exemplo completo é
   `edicoes/2026-10-09-robo-trabalho/roteiro.yaml`):
   - `fala`: 550–750 caracteres (≈35–45 s no avatar). Tom do Nei: direto, "tu", começa pelo que se vê
     ("Olha isso."), números, a pergunta ("tu acha que…? vai ficar esperando ou vai se qualificar?") e o
     fecho "No inema ponto club tem mais de trezentos cursos gratuitos… Começa hoje."
     **Ano e número por extenso na fala** (a voz erra algarismo); "inema ponto club".
   - `abertura` (quadro 0, com a data dd/mm/aaaa automática), `manchete_numeros`, `cartoes`
     (cada um com `ancora` = palavra da fala que faz o cartão entrar, `numero` com `{}` para contar até
     `conta`, `rotulo` em até 3 linhas curtas, `fonte`), `pergunta` (`ancora`, `virada`), `cta`, `final`.
   - `lento`: o melhor trecho do reel (segundos) para repetir em câmera lenta enquanto os números passam.
   - `{cursos_100}` vira o total de cursos do portal arredondado (ex.: 300).
4. **Prévia sem avatar:** `python3 reelcomenta.py previa edicoes/<pasta>` → `previa.jpg`. Olhe:
   texto cortado, cartão saindo da caixa, manchete longa. Ajuste e repita.
5. **Avatar:** grave `avatar/APROVADO_HEYGEN` e rode `python3 reelcomenta.py avatar edicoes/<pasta>`
   (com `run_in_background`; o estúdio leva de 30 min a 1 h na fila). Se o estúdio acusar
   "modal sem Enviar", o vídeo pode ter entrado: o comando confere o status antes de desistir.
6. **Montar e conferir:** `python3 reelcomenta.py montar edicoes/<pasta>` (para se a fala ouvida
   divergir < 85% do roteiro) e `python3 reelcomenta.py conferir edicoes/<pasta>` → olhe
   `conferencia.jpg` (10 quadros: rosto inteiro na caixa, número dentro do painel, legenda legível).
7. **Entregar:** `python3 reelcomenta.py enviar edicoes/<pasta> "<legenda curta>"` (bot v3).
   YouTube só se o Nei pedir (yt-pubx, canal que ele disser; short não leva thumb).

## Regras

- Quadro 0 cheio: data + manchete forte + o reel já rodando. Nada de abrir em tela vazia.
- Não escrever "Fonte: @perfil" do vídeo original na tela; o crédito dos números vai no cartão.
- Não usar voz/imagem gerada de candidato ou político.
- Falhou? Linha no `FALHAS.md` do repo (data | o que quebrou | menor correção | prompt/infra).
