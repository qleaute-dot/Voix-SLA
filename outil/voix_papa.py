"""Voix de Papa : cloner une voix à partir d'un enregistrement, puis générer
les phrases de l'application « Voix de Papa » avec cette voix.

Moteur : XTTS-v2 (Coqui, open source, français natif). Il imite une voix à
partir de quelques extraits de référence, sans entraînement. Licence du modèle :
Coqui Public Model License (usage non commercial, ce qui couvre un usage
familial).

Étapes :
  1. preparer : nettoie l'enregistrement, le découpe et choisit les meilleurs
     extraits de référence (voix claire, volume régulier, pas de saturation).
  2. Voix.creer : calcule l'empreinte de la voix à partir de ces extraits.
  3. generer_pack : prononce chaque phrase et produit voix-de-papa.zip,
     à importer dans l'application (onglet Voix).

Utilisable dans le notebook Colab (gratuit, avec GPU) ou en ligne de commande :
  python voix_papa.py preparer enregistrement.m4a
  python voix_papa.py essai "Bonjour, c'est moi."
  python voix_papa.py generer --phrases phrases-voix-de-papa.json
  python voix_papa.py interface        # page web pour taper une phrase libre
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unicodedata
import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 24000  # fréquence de travail (celle de la sortie XTTS)
DOSSIER = Path(os.environ.get("VOIX_PAPA_DOSSIER", "voix_papa_travail"))
LANGUE = "fr"


# --------------------------------------------------------------------------
# Clé de phrase : doit rester identique à cle() dans l'application.
# --------------------------------------------------------------------------
def cle(texte: str) -> str:
    t = unicodedata.normalize("NFC", texte)
    t = t.replace("’", "'").replace("‘", "'").replace(" ", " ")
    return " ".join(t.split()).lower()


def nom_fichier(texte: str) -> str:
    return hashlib.sha1(cle(texte).encode("utf-8")).hexdigest()[:16] + ".mp3"


# --------------------------------------------------------------------------
# 1. Préparation de l'enregistrement
# --------------------------------------------------------------------------
def _ffmpeg(*args: str) -> None:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg a échoué : " + r.stderr.strip())


def charger_audio(chemin: str | Path) -> np.ndarray:
    """Lit n'importe quel format (m4a, mp3, wav, qta…) en mono 24 kHz,
    filtre les graves parasites et égalise le volume."""
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "a.wav"
        _ffmpeg("-i", str(chemin), "-ac", "1", "-ar", str(SR),
                "-af", "highpass=f=70,loudnorm=I=-20:TP=-2:LRA=11", str(wav))
        audio, _ = sf.read(wav, dtype="float32")
    return audio


@dataclass
class Extrait:
    debut: float
    fin: float
    score: float

    @property
    def duree(self) -> float:
        return self.fin - self.debut


def _segments_parole(audio: np.ndarray, trame: float = 0.03) -> list[tuple[int, int]]:
    """Repère les passages parlés à partir de l'énergie (sans dépendance lourde)."""
    n = int(SR * trame)
    nb = len(audio) // n
    if nb == 0:
        return []
    e = np.sqrt((audio[: nb * n].reshape(nb, n) ** 2).mean(axis=1) + 1e-10)
    db = 20 * np.log10(e)
    plancher = np.percentile(db, 15)
    seuil = max(plancher + 12, np.percentile(db, 90) - 30)
    parle = db > seuil
    # combler les petits trous (< 0,35 s) entre syllabes et mots
    trou = int(0.35 / trame)
    i = 0
    while i < nb:
        if not parle[i]:
            j = i
            while j < nb and not parle[j]:
                j += 1
            if 0 < i and j < nb and j - i <= trou:
                parle[i:j] = True
            i = j
        else:
            i += 1
    segs, i = [], 0
    while i < nb:
        if parle[i]:
            j = i
            while j < nb and parle[j]:
                j += 1
            segs.append((i * n, j * n))
            i = j
        else:
            i += 1
    return segs


def _decouper(audio: np.ndarray, mini: float = 4.0, maxi: float = 11.0) -> list[tuple[int, int]]:
    """Regroupe les passages parlés en extraits de 4 à 11 secondes."""
    extraits, cur = [], None
    for a, b in _segments_parole(audio):
        if cur is None:
            cur = [a, b]
        elif (b - cur[0]) / SR <= maxi and (a - cur[1]) / SR < 0.8:
            cur[1] = b
        else:
            if (cur[1] - cur[0]) / SR >= mini:
                extraits.append(tuple(cur))
            cur = [a, b]
        while cur and (cur[1] - cur[0]) / SR > maxi:
            fin = cur[0] + int(maxi * SR)
            extraits.append((cur[0], fin))
            cur = [fin, cur[1]] if (cur[1] - fin) / SR >= 0.5 else None
    if cur and (cur[1] - cur[0]) / SR >= mini:
        extraits.append(tuple(cur))
    return extraits


def _score(x: np.ndarray) -> float:
    """Note un extrait : voix continue, volume régulier, pas de saturation."""
    n = int(SR * 0.03)
    nb = len(x) // n
    e = np.sqrt((x[: nb * n].reshape(nb, n) ** 2).mean(axis=1) + 1e-10)
    db = 20 * np.log10(e)
    actif = db > np.percentile(db, 95) - 25
    part_parole = actif.mean()                        # proche de 1 : peu de blancs
    regularite = 1.0 / (1.0 + np.std(db[actif]) / 6)  # volume stable
    sature = (np.abs(x) > 0.98).mean()
    bruit = np.percentile(db, 10) - np.percentile(db, 95)  # écart fond / voix (négatif)
    rapport = min(1.0, -bruit / 35)
    return float(part_parole * 0.4 + regularite * 0.3 + rapport * 0.3 - sature * 50)


def preparer(fichiers: list[str | Path], dossier: Path = DOSSIER,
             nb_refs: int = 8, duree_refs: float = 75.0) -> dict:
    """Prépare les extraits de référence. Renvoie un résumé lisible."""
    dossier = Path(dossier)
    refs_dir = dossier / "references"
    if refs_dir.exists():
        shutil.rmtree(refs_dir)
    refs_dir.mkdir(parents=True)

    morceaux = [charger_audio(f) for f in fichiers]
    pause = np.zeros(int(SR * 0.6), dtype="float32")
    audio = np.concatenate([m for f in morceaux for m in (f, pause)])
    sf.write(dossier / "enregistrement_nettoye.wav", audio, SR)

    candidats = []
    for a, b in _decouper(audio):
        x = audio[a:b]
        candidats.append(Extrait(a / SR, b / SR, _score(x)))
    if not candidats:
        raise ValueError("Aucun passage parlé détecté. L'enregistrement est-il vide ou très bruité ?")
    duree_parole = sum(c.duree for c in candidats)

    # meilleurs extraits, en évitant de prendre tout au même endroit
    choisis, total = [], 0.0
    for c in sorted(candidats, key=lambda c: c.score, reverse=True):
        if len(choisis) >= nb_refs or total >= duree_refs:
            break
        if any(abs(c.debut - d.debut) < 20 for d in choisis) and len(candidats) > nb_refs * 3:
            continue
        choisis.append(c)
        total += c.duree
    choisis.sort(key=lambda c: c.debut)

    chemins = []
    for i, c in enumerate(choisis, 1):
        x = audio[int(c.debut * SR): int(c.fin * SR)]
        fondu = int(SR * 0.02)
        x = x.copy()
        x[:fondu] *= np.linspace(0, 1, fondu)
        x[-fondu:] *= np.linspace(1, 0, fondu)
        p = refs_dir / f"ref_{i:02d}.wav"
        sf.write(p, x, SR)
        chemins.append(str(p))

    resume = {
        "duree_totale_s": round(len(audio) / SR, 1),
        "duree_parole_s": round(duree_parole, 1),
        "extraits_candidats": len(candidats),
        "references": [{"fichier": p, "debut_s": round(c.debut, 1), "duree_s": round(c.duree, 1),
                        "score": round(c.score, 3)} for p, c in zip(chemins, choisis)],
    }
    (dossier / "preparation.json").write_text(json.dumps(resume, ensure_ascii=False, indent=2))
    return resume


def references(dossier: Path = DOSSIER) -> list[str]:
    return sorted(str(p) for p in (Path(dossier) / "references").glob("ref_*.wav"))


# --------------------------------------------------------------------------
# 2. La voix (XTTS-v2)
# --------------------------------------------------------------------------
class Voix:
    """Charge XTTS-v2 et l'empreinte de la voix (calculée une fois, puis réutilisée)."""

    def __init__(self, gpt_latent, speaker_emb, modele):
        self.gpt_latent = gpt_latent
        self.speaker_emb = speaker_emb
        self.modele = modele

    @staticmethod
    def _modele():
        os.environ.setdefault("COQUI_TOS_AGREED", "1")
        import torch
        from TTS.api import TTS
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cpu":
            print("Attention : pas de carte graphique, la génération sera lente (≈ 10 à 30 s par phrase).")
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        return tts.synthesizer.tts_model

    @classmethod
    def creer(cls, refs: list[str] | None = None, dossier: Path = DOSSIER) -> "Voix":
        import torch
        refs = refs or references(dossier)
        if not refs:
            raise ValueError("Pas d'extrait de référence : lancez d'abord preparer().")
        modele = cls._modele()
        gpt, spk = modele.get_conditioning_latents(
            audio_path=refs, gpt_cond_len=30, gpt_cond_chunk_len=6, max_ref_length=30)
        torch.save({"gpt": gpt.cpu(), "spk": spk.cpu()}, Path(dossier) / "empreinte_voix_papa.pth")
        return cls(gpt, spk, modele)

    @classmethod
    def charger(cls, dossier: Path = DOSSIER) -> "Voix":
        import torch
        modele = cls._modele()
        d = torch.load(Path(dossier) / "empreinte_voix_papa.pth")
        dev = next(modele.parameters()).device
        return cls(d["gpt"].to(dev), d["spk"].to(dev), modele)

    def dire(self, texte: str, temperature: float = 0.65, vitesse: float = 1.0) -> np.ndarray:
        kw = dict(temperature=temperature, repetition_penalty=5.0, top_p=0.85, speed=vitesse)
        try:
            out = self.modele.inference(texte, LANGUE, self.gpt_latent, self.speaker_emb,
                                        enable_text_splitting=len(texte) > 250, **kw)
        except ImportError:  # découpage en phrases indisponible (spacy absent)
            out = self.modele.inference(texte, LANGUE, self.gpt_latent, self.speaker_emb,
                                        enable_text_splitting=False, **kw)
        wav = np.asarray(out["wav"], dtype="float32")
        pic = np.abs(wav).max() or 1.0
        return wav / pic * 0.89

    def dire_fichier(self, texte: str, chemin: str | Path, **kw) -> Path:
        chemin = Path(chemin)
        wav = self.dire(texte, **kw)
        if chemin.suffix == ".mp3":
            with tempfile.TemporaryDirectory() as tmp:
                t = Path(tmp) / "a.wav"
                sf.write(t, wav, SR)
                _ffmpeg("-i", str(t), "-ac", "1", "-b:a", "64k", str(chemin))
        else:
            sf.write(chemin, wav, SR)
        return chemin


# --------------------------------------------------------------------------
# 3. Les phrases et le pack pour l'application
# --------------------------------------------------------------------------
def charger_phrases(source: str | Path | None) -> list[str]:
    """Accepte l'export de l'application (phrases-voix-de-papa.json),
    une liste JSON, ou un fichier texte (une phrase par ligne)."""
    if source is None:
        return []
    p = Path(source)
    if p.suffix.lower() == ".txt":
        brut = p.read_text(encoding="utf-8").splitlines()
    else:
        d = json.loads(p.read_text(encoding="utf-8"))
        brut = d if isinstance(d, list) else d.get("textes") or []
    vus, out = set(), []
    for t in brut:
        t = (t or "").strip()
        if t and cle(t) not in vus:
            vus.add(cle(t))
            out.append(t)
    return out


def generer_pack(voix: Voix, phrases: list[str], sortie: str | Path = "voix-de-papa.zip",
                 ancien_pack: str | Path | None = None, **kw) -> Path:
    """Prononce chaque phrase et écrit le pack pour l'application.
    Si ancien_pack est fourni, les phrases déjà présentes ne sont pas refaites."""
    sortie = Path(sortie)
    deja: dict[str, bytes] = {}
    if ancien_pack and Path(ancien_pack).exists():
        with zipfile.ZipFile(ancien_pack) as z:
            man = json.loads(z.read("manifest.json"))
            for e in man["phrases"]:
                deja[e["cle"]] = z.read(e["fichier"])

    entrees = []
    with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(sortie, "w", zipfile.ZIP_STORED) as z:
        for i, texte in enumerate(phrases, 1):
            k, nom = cle(texte), nom_fichier(texte)
            if k in deja:
                z.writestr(nom, deja[k])
                etat = "repris"
            else:
                f = voix.dire_fichier(texte, Path(tmp) / nom, **kw)
                z.write(f, nom)
                etat = "généré"
            entrees.append({"texte": texte, "cle": k, "fichier": nom})
            print(f"[{i}/{len(phrases)}] {etat} : {texte}")
        z.writestr("manifest.json", json.dumps(
            {"format": "voix-de-papa", "version": 1, "phrases": entrees}, ensure_ascii=False, indent=1))
    return sortie


# --------------------------------------------------------------------------
# Interface web (phrase libre, pendant que l'ordinateur ou Colab tourne)
# --------------------------------------------------------------------------
def interface(voix: Voix, partager: bool = True):
    import gradio as gr

    def parler(texte, vitesse):
        if not texte or not texte.strip():
            return None
        return SR, voix.dire(texte.strip(), vitesse=vitesse)

    with gr.Blocks(title="Voix de Papa") as page:
        gr.Markdown("## Voix de Papa\nÉcrivez une phrase, elle sera dite avec la voix de papa.")
        texte = gr.Textbox(label="Phrase", lines=2, placeholder="Je suis content de vous voir.")
        vitesse = gr.Slider(0.7, 1.3, value=1.0, step=0.05, label="Vitesse")
        bouton = gr.Button("Dire", variant="primary")
        son = gr.Audio(label="Voix de papa", autoplay=True)
        bouton.click(parler, [texte, vitesse], son)
        texte.submit(parler, [texte, vitesse], son)
    page.launch(share=partager)


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Voix de Papa : clonage de voix et génération des phrases")
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("preparer", help="préparer les extraits de référence")
    a.add_argument("fichiers", nargs="+")
    a = sp.add_parser("essai", help="dire une phrase de test")
    a.add_argument("texte")
    a.add_argument("--sortie", default="essai.wav")
    a = sp.add_parser("generer", help="générer le pack pour l'application")
    a.add_argument("--phrases", required=True)
    a.add_argument("--sortie", default="voix-de-papa.zip")
    a.add_argument("--ancien-pack")
    sp.add_parser("interface", help="page web pour les phrases libres")
    args = ap.parse_args()

    if args.cmd == "preparer":
        print(json.dumps(preparer(args.fichiers), ensure_ascii=False, indent=2))
        return
    emp = DOSSIER / "empreinte_voix_papa.pth"
    voix = Voix.charger() if emp.exists() else Voix.creer()
    if args.cmd == "essai":
        print(voix.dire_fichier(args.texte, args.sortie))
    elif args.cmd == "generer":
        phrases = charger_phrases(args.phrases)
        print(generer_pack(voix, phrases, args.sortie, args.ancien_pack))
    elif args.cmd == "interface":
        interface(voix)


if __name__ == "__main__":
    main()
