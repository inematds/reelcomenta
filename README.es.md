# reelcomenta

[![reelcomenta](guia/assets/banner-es.jpg)](https://inematds.github.io/reelcomenta/guia/es/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## Qué es

reelcomenta es una herramienta de línea de comandos que toma el enlace de un reel, TikTok o Short de otra persona y arma un video vertical tuyo comentando ese tema. El video original sigue pasando, con su música baja. Tu avatar de HeyGen habla en una esquina de la pantalla, las cifras de tu investigación aparecen en un panel con su fuente, y el video termina con una pregunta y la invitación a los cursos gratuitos de inema.club. Es para quien produce contenido y quiere subirse a un video que ya está circulando, sin grabar nada. Necesita Python, ffmpeg, una cuenta de HeyGen con tu avatar y los proyectos cardshorts y explicavideos.

## 📖 Guía de uso

Guía completa (landing + paso a paso): **https://inematds.github.io/reelcomenta/guia/es/**

## El formato

| Tiempo | En pantalla | Audio |
|---|---|---|
| Cuadro 0 | fecha dd/mm/aaaa + titular + el reel ya corriendo | música del reel, baja |
| Cifras | panel con contador y fuente, en la palabra exacta del habla; el mejor fragmento del reel en cámara lenta | el avatar habla, la música baja sola |
| Pregunta | "ESPERAR" tachado → "O SI TE CAPACITAS" | "¿vas a quedarte esperando o vas a capacitarte?" |
| Cierre | mosaico de las portadas reales de los cursos + tarjeta INEMA.CLUB | "+300 cursos gratuitos… empieza hoy" |

El avatar queda abajo a la derecha (400×453, marco ámbar y nombre), recortado en el rostro automáticamente (OpenCV). El subtítulo va palabra por palabra, a partir de la transcripción del habla del propio avatar.

## Uso

```bash
python3 reelcomenta.py novo "<enlace>" --id tema      # descarga, transcribe, hoja de cuadros, roteiro.yaml
# escribe edicoes/<fecha>-tema/roteiro.yaml (habla + tarjetas con fuente)
python3 reelcomenta.py previa  edicoes/<carpeta>          # previa.jpg con tiempo estimado
echo "aprobado" > edicoes/<carpeta>/avatar/APROVADO_HEYGEN
python3 reelcomenta.py avatar  edicoes/<carpeta>          # estudio de HeyGen, espera y descarga
python3 reelcomenta.py montar  edicoes/<carpeta>          # video.mp4
python3 reelcomenta.py conferir edicoes/<carpeta>         # conferencia.jpg + volumen
python3 reelcomenta.py enviar  edicoes/<carpeta> "texto"  # bot de Telegram
```

Ejemplo completo: [`edicoes/2026-10-09-robo-trabalho/roteiro.yaml`](edicoes/2026-10-09-robo-trabalho/roteiro.yaml).

Para Claude Code o Codex, la skill está en [`skill/SKILL.md`](skill/SKILL.md): con ella, basta enviar el enlace.

## Dependencias

- Python 3 con Pillow, PyYAML y OpenCV; ffmpeg; yt-dlp.
- [cardshorts](https://github.com/inematds/cardshorts): transcripción local con tiempo por palabra y envío a Telegram.
- [explicavideos](https://github.com/inematds/explicavideos): estudio de HeyGen por el navegador (sin API de generación) y lectura de estado.
- Rutas por variable: `RC_CARDSHORTS`, `RC_EXPLICAVIDEOS`, `RC_PERFIL_HEYGEN`, `RC_TEMPLATE_HEYGEN`, `RC_PORTAL_DADOS`, `RC_CAPAS`, `RC_MUSICA`, `RC_DISPLAY`.

## Ediciones

| Fecha | Edición | Qué muestra |
|---|---|---|
| 09/10/2026 | `edicoes/2026-10-09-robo-trabalho` | robot bailando en el escenario → 92 millones de empleos (Foro Económico Mundial), 41% de las empresas, 1 de cada 5 recortando gerencia media (Gartner), 542 mil robots (IFR) |

Licencia MIT. El video de terceros usado en cada edición sigue siendo de su autor; las cifras siguen las fuentes citadas.
