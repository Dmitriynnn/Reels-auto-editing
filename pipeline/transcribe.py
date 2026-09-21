"""
transcribe.py <video> <workdir>
Извлекает аудио, гоняет whisper-cli (large-v3-turbo), собирает слова с таймингами.
Пишет <workdir>/words.json {words:[{s,e,t}], text} и печатает транскрипт.
Модель: env WHISPER_MODEL или assets/models/ggml-large-v3-turbo-q5_0.bin
"""
import sys, os, json, subprocess
HERE=os.path.dirname(os.path.abspath(__file__))
def main(video, wd):
    os.makedirs(wd, exist_ok=True)
    model=os.environ.get("WHISPER_MODEL", os.path.join(HERE,"..","assets","models","ggml-large-v3-turbo-q5_0.bin"))
    lang=os.environ.get("WHISPER_LANG","ru")
    wav=os.path.join(wd,"a16k.wav")
    subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",video,"-ac","1","-ar","16000","-vn",wav],check=True)
    of=os.path.join(wd,"words")
    subprocess.run(["whisper-cli","-m",model,"-l",lang,"-f",wav,"-ml","1","-oj","-of",of],check=True)
    d=json.load(open(of+".json")); segs=d.get("transcription") or []
    words=[]; cur=None
    for s in segs:
        t=s.get("text","")
        if t.strip()=="" : continue
        frm=s["offsets"]["from"]/1000.0; to=s["offsets"]["to"]/1000.0
        if t.startswith(" ") or cur is None:
            if cur: words.append(cur)
            cur={"s":round(frm,3),"e":round(to,3),"t":t.strip()}
        else:
            cur["e"]=round(to,3); cur["t"]+=t.strip()
    if cur: words.append(cur)
    words=[w for w in words if w["t"].strip()]
    text=" ".join(w["t"] for w in words)
    json.dump({"words":words,"text":text}, open(os.path.join(wd,"words.json"),"w"), ensure_ascii=False)
    print("WORDS", len(words))
    print("TRANSCRIPT:\n"+text)
if __name__=="__main__":
    main(sys.argv[1], sys.argv[2])
