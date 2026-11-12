"""Reconstitue un enregistrement envoyé depuis l'application « Voix de Papa ».

L'application découpe chaque fichier en morceaux de 12 Mo, encodés en base64
(texte), et les dépose dans l'espace privé de l'artefact. Le document
`envois/<id>` liste, pour chaque fichier, ses morceaux dans l'ordre.

    python recevoir_envoi.py envoi.json dossier_morceaux/ sortie/
"""
import base64
import json
import sys
from pathlib import Path


def reconstituer(envoi: dict, morceaux: Path, sortie: Path) -> list[Path]:
    sortie.mkdir(parents=True, exist_ok=True)
    faits = []
    for i, f in enumerate(envoi["fichiers"], 1):
        nom = Path(f["nom"]).name or f"enregistrement_{i}"
        data = b"".join(base64.b64decode((morceaux / f"{pid}.txt").read_text().strip())
                        for pid in f["parts"])
        if len(data) != f["taille"]:
            raise ValueError(f"{nom} : {len(data)} octets reçus au lieu de {f['taille']}")
        p = sortie / nom
        p.write_bytes(data)
        faits.append(p)
    return faits


if __name__ == "__main__":
    envoi = json.loads(Path(sys.argv[1]).read_text())
    envoi = envoi.get("data", envoi)
    for p in reconstituer(envoi, Path(sys.argv[2]), Path(sys.argv[3])):
        print(p, p.stat().st_size)
