"""
transcribe.py <video> <workdir>
Кросс-платформенный транскрипт через faster-whisper (пословные тайминги).
Пишет <workdir>/words.json {words:[{s,e,t}], text}.
Модель: env WHISPER_MODEL (по умолч. large-v3-turbo), качается автоматически в кэш HF.
Язык: env WHISPER_LANG (по умолч. ru; 'auto' — автоопределение).
"""
import sys, os, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env import FFMPEG

def main(video, wd):
    os.makedirs(wd, exist_ok=True)
    wav=os.path.join(wd,"a16k.wav")
    subprocess.run([FFMPEG,"-y","-hide_banner","-loglevel","error","-i",video,
                    "-ac","1","-ar","16000","-vn",wav],check=True)
    from faster_whisper import WhisperModel
    name=os.environ.get("WHISPER_MODEL","large-v3-turbo")
    lang=os.environ.get("WHISPER_LANG","ru"); lang=None if lang=="auto" else lang
    ct=os.environ.get("WHISPER_COMPUTE","int8")
    model=WhisperModel(name, device="cpu", compute_type=ct)
    segs,info=model.transcribe(wav, language=lang, word_timestamps=True, vad_filter=False)
    words=[]
    for s in segs:
        for w in (s.words or []):
            t=w.word.strip()
            if t: words.append({"s":round(float(w.start),3),"e":round(float(w.end),3),"t":t})
    text=" ".join(w["t"] for w in words)
    json.dump({"words":words,"text":text}, open(os.path.join(wd,"words.json"),"w"), ensure_ascii=False)
    print("WORDS", len(words), "lang", info.language)
    print("TRANSCRIPT:\n"+text)
if __name__=="__main__":
    main(sys.argv[1], sys.argv[2])
