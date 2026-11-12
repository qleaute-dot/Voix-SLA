import sys, json, re, unicodedata
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
def norm(s):
    s = unicodedata.normalize("NFD", s.lower()); s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]", " ", s.replace("'", " ")).split()
def wer(r, h):
    d = list(range(len(h)+1))
    for i in range(1, len(r)+1):
        p, d[0] = d[0], i
        for j in range(1, len(h)+1):
            p, d[j] = d[j], min(d[j]+1, d[j-1]+1, p + (r[i-1] != h[j-1]))
    return d[len(h)] / max(1, len(r))
items = json.load(open(sys.argv[1]))  # [[fichier, texte], ...]
out = []
for f, t in items:
    segs, _ = m.transcribe(f, language="fr", beam_size=3)
    h = " ".join(s.text for s in segs).strip()
    out.append({"fichier": f, "attendu": t, "entendu": h, "wer": round(wer(norm(t), norm(h)), 3)})
    print(json.dumps(out[-1], ensure_ascii=False), flush=True)
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
