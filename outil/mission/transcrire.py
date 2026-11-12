import json, time
from faster_whisper import WhisperModel
t=time.time()
m = WhisperModel("large-v3", device="cpu", compute_type="int8", cpu_threads=4)
segs, info = m.transcribe("/root/voix/travail/enregistrement_nettoye.wav", language="fr", beam_size=5, word_timestamps=True, vad_filter=True, condition_on_previous_text=False)
out=[]
for s in segs:
    out.append({"start":s.start,"end":s.end,"text":s.text.strip(),"avg_logprob":s.avg_logprob,"no_speech":s.no_speech_prob,
                "words":[{"w":w.word,"s":w.start,"e":w.end,"p":w.probability} for w in (s.words or [])]})
    print(round(s.start,1), s.text.strip(), flush=True)
json.dump(out, open("/root/voix/travail/transcription.json","w"), ensure_ascii=False, indent=1)
print("FINI", round(time.time()-t), "s")
