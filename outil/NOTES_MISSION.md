# Mission : voix de papa au plus près (accent nantais/vendéen)

Notes de travail de Claude, pour reprendre si la session s'interrompt.
L'audio de papa n'est jamais versé dans ce dépôt : il est dans l'espace
privé de l'artefact (document `envois/e1794495491336`, asset `510a5f38…`).

## Constat (12/11)
- Essais « au vol » (XTTS-v2, Chatterbox) : timbre approchant mais **accent faux**
  selon l'utilisateur. Aucune version retenue.
- Enregistrement : 9 min 38 s, ≈ 6 min 40 s de parole, une seule voix, voix
  non encore touchée par la maladie. Papa raconte sa vie (logement, Saint-Lazare,
  service militaire, son couple…).

## Plan
1. Transcription complète (faster-whisper large-v3) + découpage en phrases.
2. Mettre de côté quelques phrases réelles (test) : le clone doit redire
   exactement ces phrases → comparaison « vraie voix / clone ».
3. F5-TTS français (RASPIAUDIO/F5-French-MixedSpeakers-reduced, CC-BY-NC) en
   clonage au vol : il prolonge l'extrait de référence, souvent meilleur pour l'accent.
4. Entraînement XTTS-v2 (partie GPT) sur ses phrases transcrites (CPU).
5. Entraînement F5-TTS sur ses phrases si 3 est prometteur.
6. Mesures : exactitude des mots (Whisper), ressemblance du timbre (encodeur
   XTTS) sur les phrases de test ; écoute finale par l'utilisateur.
7. Publication des essais dans l'app (section Essais).

## Journal
- 15:50 UTC transcription lancée.
- Demande ajoutée : après validation de la voix principale, essayer une voix
  légère (Piper / sherpa-onnx en WASM) entraînée sur papa, pour la phrase libre
  en temps réel dans l'iPad.
