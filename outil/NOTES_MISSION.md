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
- 16:35 UTC Avis utilisateur : 15/15 « pas bon » (F5 au vol ×5, XTTS au vol ×10) —
  ni intonation, ni accent, ni rythme. Le clonage au vol est écarté.
  Génération XTTS au vol arrêtée pour laisser tout le processeur à l'entraînement.
- 16:30 UTC Entraînement XTTS (ft1) : 15 époques, lr 1e-5, lot de 3, ≈ 47 s/pas
  (22 pas/époque) → ≈ 3 à 4 h.
- 16:39 UTC Entraînement ft1 relancé (lot 2, accumulation 2, 33 pas/époque, ≈ 12 min/époque),
  sauvegardes aux époques 1, 5, 10, 15 (rappel de fin d'époque). Perte mel sur
  phrases de test : 3,81 (ép. 1) → 3,64 (ép. 2).
- Ensuite : pipe/apres_ft.sh (base vs époques 5/10/15 sur 5 phrases de test :
  ressemblance + exactitude), puis série Comparer avec la meilleure époque.
- App : note de 1 à 5 après « Bon » (avis.etoiles), à publier avec la série.
- 18:16 UTC Perte de test : 3,50 (ép. 5) puis 3,55 / 3,56 / 3,64 (ép. 6-8) → surapprentissage.
  Entraînement arrêté ; l'époque 5 (sauvegardée) est la meilleure. Évaluation base vs ép. 5.
