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
- 19:45 UTC Mesures sur 5 phrases jamais entendues : base sim 68 / mots faux 23 % ;
  ft ép. 5 sim 73 / mots faux 7 % (sa vraie voix ≈ 79). Série Comparer « ft5 » publiée :
  71 phrases (5 jamais entendues en tête), meilleure de 2 prises par phrase.
- 20:20 UTC Avis sur ft5 : 68/71 « pas bon » (accent 60, timbre 55, intonation 54).
  Fine-tuning XTTS écarté. Nouveau plan (sans ElevenLabs en attendant) :
  « Ses vraies paroles » (publié, 49 passages, adresse exclue), « Ses sons »,
  conversion de timbre RVC (Applio, autorisé par l'utilisateur) entraînée sur papa,
  puis conversion de la voix du fils (même accent régional) → timbre de papa.
- 21:00 UTC « Ses sons » publié (catégorie dans Parler) : 2 rires, 3 soupirs, raclement,
  « Voilà / Bon / Oui / Non » (AST AudioSet + mots Whisper). Validation : db sons/<id>.retire.
  RVC (Applio) : extraction finie, entraînement 300 époques en cours (CPU).
  Qwen3-TTS 0.6B Base (clonage) : c001 sans faute de mots, mais ≈ 20 min/phrase sur CPU partagé.
- 21:15 UTC RVC : 1er lancement tué (mémoire, -9) ; relancé seul, lot 4, 59 pas/époque,
  ≈ 4,6 min/époque, sauvegarde toutes les 25 époques. Index papa.index créé.
  Qwen3-TTS au vol, 5 phrases test : mots ≈ parfaits (WER moy. 6 %), timbre faible (sim 0,56).
  Publié dans Comparer (version « qz ») pour jugement de l'accent.
  Suite : à chaque sauvegarde RVC, convertir Qwen + ft5 (pipe/rvc_conv.py) et mesurer.
- 22:35 UTC Voix du fils reçue (6 phrases, 28 s ; 3 identiques à des phrases de papa).
  F0 médiane : papa 127 Hz, fils 133 Hz (−1 demi-ton), Qwen 146 Hz (−2).
  Seed-VC installé (autorisé par l'utilisateur), référence papa 25 s (seed_ref.wav).
  Chaîne de nuit : pipe/nuit_queue.sh (Seed-VC fils → Seed-VC Qwen → Qwen +14 phrases →
  Seed-VC), pipe/rvc_watch.sh (à chaque sauvegarde Applio : rvc_test.sh → rvcout/eNN).
  Matin : pipe/panel.py (mesure toutes les variantes, construit Comparer, meilleures en tête).
- 23:00 UTC Applio ralenti ×8 par Seed-VC (processeur partagé) : Seed-VC passé à 1 fil
  et priorité basse (nice 15), Qwen à 2 fils. Aperçu publié : « ta voix + Seed-VC »
  (4 phrases) à côté de « ta voix telle quelle » et de la vraie voix.
- 23:10 UTC Avis : Seed-VC au vol 4/4 « pas bon » (accent « anglais », timbre faux) → abandonné.
  Tout le processeur à Applio ; Qwen +14 phrases en priorité basse (pour Qwen + Applio).
- 23:30 UTC Pause d'Applio pour Qwen : manque de mémoire, les deux tués (-9), aucune
  sauvegarde Applio perdue (aucune encore). Relancé seul (rvc3.log), sauvegarde toutes les
  10 époques, ≈ 4,5 min/époque ; swap 5 Go. rvc_watch.sh convertit à chaque sauvegarde.
  Leçon : ne rien faire tourner en parallèle d'Applio sur cette machine.
