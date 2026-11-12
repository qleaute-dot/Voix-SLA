"""Construit Voix_de_Papa.ipynb (Google Colab) en y intégrant voix_papa.py.
Relancer après toute modification de voix_papa.py :
    python outil/construire_notebook.py
"""
import json
from pathlib import Path

ICI = Path(__file__).parent
module = (ICI / "voix_papa.py").read_text(encoding="utf-8")


def md(s):
    return {"cell_type": "markdown", "metadata": {}, "source": s.strip("\n")}


def code(s):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": s.strip("\n")}


cellules = [
    md("""
# Voix de Papa : cloner la voix

Ce carnet crée la voix de papa à partir de son enregistrement, puis prononce toutes les phrases de l'application **Voix de Papa** avec cette voix.

**Avant de commencer :** menu *Exécution* → *Modifier le type d'exécution* → choisir **GPU T4** (gratuit). Ensuite, lancez les cellules une par une avec le bouton ▶, dans l'ordre.

Le modèle utilisé, XTTS-v2, est open source et gratuit pour un usage non commercial (Coqui Public Model License). L'enregistrement reste dans votre session Colab et sur votre Google Drive. Il n'est envoyé à aucun service de clonage.
"""),
    md("## 1. Installer l'outil (≈ 3 min, une fois par session)"),
    code("""
!nvidia-smi --query-gpu=name --format=csv,noheader || echo "⚠️ Pas de GPU : menu Exécution → Modifier le type d'exécution → GPU T4"
!pip install -q "coqui-tts>=0.27,<0.29" gradio soundfile
import os
os.environ["COQUI_TOS_AGREED"] = "1"  # accepte la licence non commerciale du modèle XTTS-v2
"""),
    code("%%writefile voix_papa.py\n" + module),
    md("""
## 2. Garder le travail sur Google Drive (conseillé)

Ainsi, l'empreinte de la voix et le pack sont conservés : la prochaine fois, il suffira de passer directement à l'étape 5.
"""),
    code("""
from google.colab import drive
drive.mount('/content/drive')
os.environ["VOIX_PAPA_DOSSIER"] = "/content/drive/MyDrive/Voix de Papa"
os.makedirs(os.environ["VOIX_PAPA_DOSSIER"], exist_ok=True)
print("Dossier de travail :", os.environ["VOIX_PAPA_DOSSIER"])
"""),
    md("## 3. Envoyer l'enregistrement de papa\nUn ou plusieurs fichiers : m4a, mp3, wav, qta… Les 10 minutes d'il y a un an conviennent."),
    code("""
import importlib, voix_papa as vp
importlib.reload(vp)
from google.colab import files
envoyes = files.upload()
resume = vp.preparer(list(envoyes))
print(f"Durée totale : {resume['duree_totale_s']/60:.1f} min, dont {resume['duree_parole_s']/60:.1f} min de parole.")
print(f"{len(resume['references'])} extraits de référence choisis.")
"""),
    md("""
### Écouter les extraits choisis

Ils servent de modèle à la voix. S'il y en a un où l'on entend quelqu'un d'autre, de la musique ou un bruit fort, notez son numéro dans la cellule suivante pour l'écarter.
"""),
    code("""
from IPython.display import Audio, display
for i, r in enumerate(resume["references"], 1):
    print(f"Extrait {i} : à {r['debut_s']:.0f} s, {r['duree_s']:.1f} s")
    display(Audio(r["fichier"]))
"""),
    code("""
a_ecarter = []   # par exemple [3, 6]
for n in a_ecarter:
    os.remove(resume["references"][n-1]["fichier"])
print("Extraits gardés :", len(vp.references()))
"""),
    md("## 4. Créer la voix de papa et l'essayer"),
    code("""
voix = vp.Voix.creer()
essais = ["Bonjour ! Je suis content de vous voir.",
          "J'ai un peu mal au dos aujourd'hui, pouvez-vous m'aider à m'asseoir ?",
          "Je vous aime, merci d'être là."]
for t in essais:
    print(t)
    display(Audio(voix.dire(t), rate=vp.SR))
"""),
    md("""
**Réglages si le rendu ne convient pas :**
- voix trop monotone ou trop « lisse » : monter `temperature` (0,75) ;
- voix instable, accent qui dérape : la baisser (0,5) ;
- trop rapide : `vitesse=0.9`.

Essayez ici, puis reportez les valeurs à l'étape 5.
"""),
    code("""
texte = "Mon plus beau voyage, c'était en famille."
display(Audio(voix.dire(texte, temperature=0.65, vitesse=1.0), rate=vp.SR))
"""),
    md("""
## 5. Générer toutes les phrases pour l'iPad

Dans l'application, onglet **Voix**, touchez **Exporter mes phrases**. Envoyez ici le fichier `phrases-voix-de-papa.json`. Le carnet prononce chaque phrase et vous donne `voix-de-papa.zip`, à importer dans l'application.

Quand vous ajoutez des phrases plus tard, refaites seulement cette étape : les phrases déjà faites sont reprises du pack précédent.
"""),
    code("""
import importlib, voix_papa as vp
from pathlib import Path
from google.colab import files
if "voix" not in globals():
    voix = vp.Voix.charger()   # reprend l'empreinte enregistrée sur le Drive
envoye = files.upload()
phrases = vp.charger_phrases(next(iter(envoye)))
print(len(phrases), "phrases")
dossier = Path(os.environ.get("VOIX_PAPA_DOSSIER", "voix_papa_travail"))
ancien = dossier / "voix-de-papa.zip"
pack = vp.generer_pack(voix, phrases, "voix-de-papa.zip", ancien_pack=ancien,
                       temperature=0.65, vitesse=1.0)
import shutil; shutil.copy(pack, ancien)
files.download(str(pack))
"""),
    md("""
## 6. (Facultatif) Phrase libre avec la voix de papa

Cette cellule ouvre une page web, avec un lien en `gradio.live`, utilisable depuis l'iPad ou un téléphone tant que Colab tourne. On tape n'importe quelle phrase, elle est dite avec la voix de papa en quelques secondes. Le lien expire à la fermeture de Colab.
"""),
    code("""
if "voix" not in globals():
    voix = vp.Voix.charger()
vp.interface(voix)
"""),
]

nb = {
    "nbformat": 4, "nbformat_minor": 5,
    "metadata": {"accelerator": "GPU", "colab": {"provenance": [], "gpuType": "T4"},
                 "kernelspec": {"name": "python3", "display_name": "Python 3"},
                 "language_info": {"name": "python"}},
    "cells": cellules,
}
(ICI / "Voix_de_Papa.ipynb").write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print("Voix_de_Papa.ipynb écrit")
