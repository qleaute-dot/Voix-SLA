# Voix-SLA

Application de communication pour un père atteint de SLA qui perd sa voix. Elle prononce ses phrases avec **sa propre voix**, clonée à partir d'un enregistrement de 10 minutes.

## Contenu

| Dossier | Rôle |
| --- | --- |
| `app/voix-de-papa.html` | L'application iPad (artefact claude.ai « Voix de Papa ») : tuiles de phrases, conversation, « Ma vie », réglages de la voix. |
| `outil/voix_papa.py` | L'outil de clonage : préparation de l'enregistrement, création de la voix, génération des phrases. |
| `outil/Voix_de_Papa.ipynb` | Le même outil sous forme de carnet Google Colab, pas à pas et gratuit. |
| `outil/construire_notebook.py` | Reconstruit le carnet après une modification de `voix_papa.py`. |

## Comment ça marche

1. **Application → Voix → Exporter mes phrases** donne `phrases-voix-de-papa.json` : toutes les tuiles, les souvenirs et les réponses rapides.
2. Sur un ordinateur, ouvrir `outil/Voix_de_Papa.ipynb` dans [Google Colab](https://colab.research.google.com) (Fichier → Importer le notebook), choisir le GPU T4 gratuit et suivre les cellules :
   - envoyer l'enregistrement : il est nettoyé et découpé, et les 8 meilleurs extraits (≈ 1 min de voix claire) sont retenus, avec possibilité d'en écarter ;
   - créer la voix et l'écouter sur des phrases d'essai ;
   - envoyer le fichier des phrases : chaque phrase est prononcée et le carnet rend `voix-de-papa.zip`.
3. **Application → Voix → Importer voix-de-papa.zip**. Les phrases sont alors dites avec la voix de papa, instantanément et hors ligne. Les fichiers restent dans le stockage de l'iPad.

Une phrase absente du pack, comme la phrase libre, est dite par la voix de l'iPad. Le bandeau « Papa dit » indique quelle voix a parlé. Pour la phrase libre avec la voix de papa, la dernière cellule du carnet ouvre une page web temporaire (lien `gradio.live`) utilisable tant que Colab tourne.

Après avoir ajouté des phrases, on refait l'export et l'étape 5 du carnet. Seules les nouvelles phrases sont générées : les autres sont reprises du pack enregistré sur Google Drive.

## Moteur

[XTTS-v2](https://huggingface.co/coqui/XTTS-v2) (Coqui), utilisé via le paquet `coqui-tts`. Il parle français nativement et clone une voix sans entraînement, à partir d'extraits de référence. Sa licence (Coqui Public Model License) autorise un usage non commercial, ce qui couvre l'usage familial. L'enregistrement n'est envoyé à aucun service de clonage : il reste dans la session Colab et sur le Google Drive de l'utilisateur.

## En ligne de commande (ordinateur avec carte NVIDIA)

```bash
pip install "coqui-tts>=0.27,<0.29" soundfile gradio   # et ffmpeg
python outil/voix_papa.py preparer enregistrement.m4a
python outil/voix_papa.py essai "Bonjour, c'est moi."
python outil/voix_papa.py generer --phrases phrases-voix-de-papa.json
python outil/voix_papa.py interface
```
