"""
mix_audio.py <workdir>
Синтезирует мягкий свуш и подмешивает его в голос base.mp4 в моменты sfx.json.
Пишет mixaudio.m4a. (Музыки нет — только голос + свуши; трек можно добавить отдельно.)
"""
import sys, os, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env import FFMPEG
def main(wd):
    sw=os.path.join(wd,"swoosh.wav")
    subprocess.run([FFMPEG,"-y","-hide_banner","-loglevel","error","-f","lavfi",
        "-i","anoisesrc=d=0.32:c=pink:a=0.28:r=44100",
        "-af","aformat=channel_layouts=stereo,highpass=f=250,lowpass=f=5500,"
        "afade=t=in:d=0.015,afade=t=out:st=0.06:d=0.26,volume=0.55",sw],check=True)
    ts=json.load(open(os.path.join(wd,"sfx.json"))) if os.path.exists(os.path.join(wd,"sfx.json")) else []
    base=os.path.join(wd,"base.mp4"); out=os.path.join(wd,"mixaudio.m4a")
    if not ts:
        subprocess.run([FFMPEG,"-y","-hide_banner","-loglevel","error","-i",base,
            "-vn","-c:a","aac","-b:a","192k",out],check=True); print("MIX (no sfx)"); return
    n=len(ts); p=[f"[1:a]asplit={n}"+"".join(f"[s{i}]" for i in range(n))+";"]
    for i,t in enumerate(ts):
        ms=int(t*1000); p.append(f"[s{i}]adelay={ms}|{ms},volume=0.5[d{i}];")
    p.append("[0:a]"+"".join(f"[d{i}]" for i in range(n))+f"amix=inputs={n+1}:normalize=0:dropout_transition=0[a]")
    fg=os.path.join(wd,"mix.fg"); open(fg,"w").write("".join(p))
    subprocess.run([FFMPEG,"-y","-hide_banner","-loglevel","error","-i",base,"-i",sw,
        "-filter_complex_script",fg,"-map","[a]","-c:a","aac","-b:a","192k",out],check=True)
    print("MIX swooshes",n)
if __name__=="__main__":
    main(sys.argv[1])
