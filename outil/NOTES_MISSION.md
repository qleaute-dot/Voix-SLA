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
- 00:06 UTC La machine a redémarré vers 23:40 (tout arrêté, fichiers conservés). Applio
  relancé de zéro via pipe/relance.sh (idempotent, reprend aux sauvegardes). Gardes
  programmées 01:15, 02:30, 03:30, 04:30 ; bilan 05:15 UTC.
- 00:24 UTC 2e redémarrage (machine récupérée quand la session est inactive sans tâche
  suivie). Parade : Applio lancé par relance.sh + une tâche d'attente suivie (≤ 1 h 55)
  réarmée à chaque fin, pour garder la session active.
- 01:50 UTC Conversion Applio réparée (onnxruntime manquant ; sorties relatives allaient
  dans /root/applio). Époque 10 — timbre moyen : clone XTTS + Applio 74, Qwen + Applio 72,
  voix du fils + Applio 56 (fils brut 33 ; phrases communes ≈ 63). Panel époque 10 publié.
- 03:30 UTC Disque plein (48 Mo) : Applio garde chaque G/D (≈ 1,3 Go). Anciennes
  sauvegardes supprimées, menage.sh ne garde que la dernière. Époques 10/20/30 converties.
- 05:30 UTC Bilan de nuit. Timbre moyen par époque Applio (sim XTTS ×100, papa réel ≈ 79) :
  fils 64 / 71,5 / 67,5 / 66 ; Qwen 72 / 72,5 / 71 / 72 ; clone XTTS 74 / 77 / 73 / 74
  (époques 10/20/30/40). Meilleure : époque 20. Panel publié avec l'époque 20 :
  clone XTTS + Applio (19 phrases, 77), Qwen + Applio (5, 73), voix du fils + Applio (6, 66).
  Applio continue (≈ époque 50) ; Seed-VC écarté ; plusieurs redémarrages de la machine.
- 06:30 UTC Avis panel époque 20 : clone XTTS + Applio 6/19 « bon » (2-3/5) ; timbre
  signalé 4/19, accent 2/19 seulement (contre 55 et 60/71 avant) ; restent intonation 12,
  rythme 8. Qwen + Applio 0/5, voix du fils + Applio 0/6 → abandonnés.
  Applio arrêté (meilleur : époque 20). XTTS réentraîné (ft2, sauvegardes ép. 3 et 5 ;
  l'ancien ft1 avait été effacé pour le disque). Variantes de diction (pipe/variantes.sh) :
  A ép.5 réf. courtes t0,65 ; B ép.3 ; C réf. longue 30 s t0,7 ; D t0,85 ; E vitesse 0,92 ;
  12 phrases, meilleure de 2 prises, puis Applio ép. 20 → pipe/panel_var.py.
- 08:45 UTC Panel des 5 dictions publié (12 phrases × 5, Applio ép. 20) : timbre moyen
  A 76, B 77, C 76, D 76, E 76. À départager à l'oreille (intonation, rythme).
  Remote Control : aucun dossier visible depuis le cloud ; proposé une session locale
  sur le PC de l'utilisateur (carte graphique) — en attente de son retour.
- 09:20 UTC Avis 5 dictions : A 10/12 bon (moy 3,2), E 8/12 (moy 3,5, trois 5/5), C 7/12,
  B 6/12, D 5/12. Lancé : 20 phrases inventées « à la manière de papa » (pipe/nouvelles.json)
  en dictions A, E et A+E (vitesse 0,93), meilleure de 2 prises, Applio ép. 20.
- 09:25 UTC Panel « phrases nouvelles » publié (20 × A, E, A+E). Mots mal dits (Whisper) :
  A 3/20, E 7/20, A+E 7/20.
- 11:00 UTC Avis phrases inventées : A 11/20 (moy 2,7), A+E 9/20, E 8/20 ; intonation = défaut n°1.
  Grésillement : panel anti-grésillement publié (8 phrases × 4 : actuel ; Applio doux
  index 0,3 protect 0,5 ; + nettoyage Applio « light » ; + ffmpeg highpass/afftdn/deesser/lowpass).
  Plancher de bruit : -37,7 / -37,9 / -39,1 / -45,5 dB.
  Cycle guidé : 60 phrases inventées × 3 prises (A, t 0,7) → Applio doux + débruitage
  (pipe/p60.sh). App : section « Choisir la meilleure prise » (db prises/<id> : choix, etoiles).
- 12:50 UTC Avis anti-grésillement : traitements 3 et 4 (Applio doux + nettoyage / + débruitage)
  = 0 signalement de son métallique (contre 3 au réglage actuel). « Choisir la meilleure prise »
  publié avec 2 prises sur 60 phrases (3e prise en cours). Limite de 512 fichiers par version
  de l'artefact atteinte : anciens panels notés retirés (154 fichiers).
- 13:00 UTC 3e prise publiée (60 × 3). Préparé pipe/ds_guide.py (vraies phrases + prises
  choisies notées ≥ 4, les 5/5 comptées deux fois → ds/train_guide.csv) et TRAIN_CSV dans
  train_xtts.py. Après les choix : ArtifactData list prises → /root/voix/avis_pr, puis
  ds_guide.py, puis entraînement ft3, puis panel de phrases inédites ancien vs nouveau.
- 14:40 UTC Choix des prises (41/60) : 30 choisies (notes 1×11, 2×14, 3×5), 11 « aucune »,
  aucun 4 ni 5 → pas d'entraînement guidé sur ces prises. Les « aucune » sont surtout des
  questions et exclamations. Mesure de mélodie (pipe/f0stats.py, Praat) : papa termine ses
  phrases à plat (fin −0,0 demi-ton par rapport à sa médiane), le clone remonte (+1 à +2 dt) ;
  prises notées 3 : +1,1 contre +2,1 pour les notées 1. Correction (pipe/melodie.py) : fin de
  phrase abaissée en douceur (Praat PSOLA) avant Applio, phrases affirmatives seulement.
  Après Applio : fin +0,8 (contre +1,9). Test publié en tête de « Choisir la meilleure prise »
  (version 25) : 23 phrases « (Test mélodie) », 2 prises au hasard ; correspondance dans
  /root/voix/mel/ordre.json (actuelle / melodie).
- 15:40 UTC Avis test mélodie : actuelle 10, corrigée 6, aucune 7 → correction abandonnée.
  Bilan 60 phrases : 20 « aucune », notes surtout 1-2, un seul 4 → plafond XTTS + Applio.
  Feu vert utilisateur : tester F5-TTS (français, au vol) + Applio, « pousser un peu plus ».
  Ménage disque (seedvc, ft2 ép. 3, rvcout, qz, cache uv). Env f5 (torch partagé avec rvc via .pth).
  Test : 14 phrases (4 vraies c001/c024/c038/c054 + 10 « aucune » dont 4 questions), 3 prises,
  chaque prise = autre extrait de référence (c021, c058, c039 question / c056) → pipe/gen_f5b.py,
  puis pipe/f5_post.sh (choix mots+timbre, Applio doux + débruitage, version actuelle en face).
- 16:00 UTC Utilisateur : « ne cherche pas à t'économiser ». Préparé l'entraînement F5 sur
  66 extraits (c000 adresse exclu) : f5/lib/python3.11/data/papa_custom, pipe/ft_f5.sh
  (lr 1e-5, lots de 3000 trames, sauvegarde model_last toutes les 60 mises à jour),
  lancé automatiquement après le test. Swap supprimé (place disque pour les sauvegardes).
- 17:00 UTC Test F5 au vol + Applio publié (version 26) en tête de Comparer : 14 phrases,
  « Essai A » = F5 + Applio, « Essai B » = actuelle (XTTS ép. 5 + Applio doux + débruitage).
  Timbre mesuré après Applio : F5 60, actuelle 69 (papa réel ≈ 79) ; mots : 3 phrases
  avec une faute (p05, p22, c054). Entraînement F5 démarré (15 mises à jour par époque).
- 17:00 UTC Entraînement F5 tué (mémoire) au 1er lancement. Corrigé : 0 processus de chargement,
  lots de 2000 trames, swap 6 Go recréé, sauvegarde « poids seuls » (patch trainer.py, sans
  optimiseur, 1,35 Go, clé EMA pour l'inférence). ≈ 7,5 s/màj, 26 màj/époque (≈ 3,3 min).
  pipe/f5_snap.sh copie model_last toutes les 300 màj dans /root/voix/f5snap (2 gardées).
- 18:45 UTC Vidéo de 800 Mo (33 min) : envoi bloqué par le quota de 1 Go des pièces jointes
  (base64 = +33 %). Envoi partiel (63 morceaux) supprimé avec l'accord de l'utilisateur.
  App : vidéos envoyées en morceaux bruts de 16 Mo (type video/mp4, testé côté serveur),
  envois/<id> enregistré après chaque morceau (champ fin = true à la fin, codage brut/base64).
- 18:50 UTC Go vidéo. Entraînement F5 arrêté (sauvegarde gardée : /root/voix/f5snap/u960.pt).
  Vidéo reçue complète (envois/e1794595165048, 52 morceaux bruts, 865 Mo, 33 min 53 s) →
  son seul /root/voix/video/son24.wav (vidéo effacée localement). Transcription Whisper
  large-v3-turbo (pipe/transcrire_video.py), découpe 2-12 s (pipe/decoupe_video.py : écarte
  adresse/infos privées, doublons de l'ancien extrait et phrases test), filtre de voix
  (pipe/filtre_voix.py : seuil = 5e centile de ses vrais extraits − 0,03).
- 19:20 UTC Vidéo = interview de famille (plusieurs voix). Découpe phrase par phrase
  (pipe/tours_video.py), voix comparée au centre de SA voix dans la vidéo (76 phrases déjà
  connues : sim p10 0,58, médiane 0,70). Nouvelles phrases ≥ 0,55 → 57 extraits, 3,1 min
  (pipe/ds_video.py → ds/train_v.csv, 124 extraits). Vérification publiée (version 28) :
  Comparer, version « vid », « Bon » = c'est bien lui. Séries nA/nE/nAE/b2/b3 retirées (notées).
  Entraînement XTTS ft3 (5 époques, sauvegarde ép. 5) puis pipe/nuit_ft3.sh : 20 phrases neuves
  (pipe/n3_items.json, dont 9 questions/exclamations), ft2 vs ft3, meilleure de 3, Applio doux.
- 19:45 UTC Utilisateur : « je ne veux pas que l'apprentissage se fasse sur des morceaux de voix
  qui ne sont pas les siens ». Entraînement ft3 arrêté. Tri strict par fenêtres de 2 s
  (pipe/strict2_video.py) → 55 extraits w000-w054 (2,8 min), publiés (version 29) à vérifier ;
  l'encodeur n'est pas fiable sur de courts morceaux, donc SEULS les extraits confirmés « Bon »
  entreront dans l'entraînement (pipe/ds_valide.py → ds/train_ok.csv). En attendant, le
  processeur sert à l'entraînement F5 sur les extraits d'origine (sûrs).
- 19:25 UTC Vérification utilisateur : 54 « c'est bien lui, seul », 1 « autre voix ou doute ».
  F5 arrêté (sauvegarde effacée faute de place). ds/train_ok.csv = 66 + 1 (c000) + 54 extraits
  vidéo confirmés (+2,7 min). ft3 relancé (5 époques, sauvegarde ép. 5) → pipe/nuit_ft3.sh.
- 19:45 UTC Utilisateur : des voix se superposent parfois. Entraînement mis en pause, nouvelle
  vérification : 44 « lui seul », 11 écartés. ds/train_ok.csv = 67 + 44 extraits (+2,3 min).
  ft3 relancé puis pipe/nuit_ft3.sh (20 phrases neuves ft2 vs ft3) → panel à publier au matin.
