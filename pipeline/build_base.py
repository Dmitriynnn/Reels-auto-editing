"""
build_base.py <video> <workdir> [speed]
Режет паузы (>0.2с), ускоряет, апскейлит в 1080x1920 (cover+crop), тёплый грейд,
нормализует голос. Пишет base.mp4 и plan.json (слова на финальном таймлайне).
"""
import sys, os, json, subprocess
def main(video, wd, speed=1.25):
    speed=float(speed)
    d=json.load(open(os.path.join(wd,"words.json"))); words=d["words"]
    PAD,GAP=0.05,0.20; keeps=[]
    for w in words:
        a=max(0.0,w["s"]-PAD); b=w["e"]+PAD
        if keeps and a-keeps[-1][1]<=GAP: keeps[-1][1]=b
        else: keeps.append([a,b])
    cum=0.0; seg=[]
    for a,b in keeps: seg.append((a,b,cum)); cum+=(b-a)
    total_cut=cum; total_final=total_cut/speed
    def tf(t):
        for a,b,c in seg:
            if a-1e-6<=t<=b+1e-6: return (c+(t-a))/speed
        prev=0.0
        for a,b,c in seg:
            if t<a: return c/speed
            prev=(c+(b-a))/speed
        return prev
    fw=[]
    for w in words:
        fs=tf(w["s"]); fe=tf(w["e"])
        if fe<=fs: fe=fs+0.12
        fw.append({"s":round(fs,3),"e":round(fe,3),"t":w["t"]})
    sel="+".join(f"between(t,{a:.3f},{b:.3f})" for a,b in keeps)
    vf=(f"[0:v]select='{sel}',setpts=N/FRAME_RATE/TB/{speed},"
        f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"eq=contrast=1.05:brightness=-0.01:saturation=1.04,curves=all='0/0 0.25/0.21 1/1',"
        f"colorbalance=rs=0.02:rm=0.02:bs=-0.02:bm=-0.02,unsharp=5:5:0.25:5:5:0.0,fps=30,format=yuv420p[v];"
        f"[0:a]aselect='{sel}',asetpts=N/SR/TB,atempo={speed},loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    fg=os.path.join(wd,"base.fg"); open(fg,"w").write(vf)
    base=os.path.join(wd,"base.mp4")
    subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",video,
        "-filter_complex_script",fg,"-map","[v]","-map","[a]",
        "-c:v","libx264","-crf","18","-preset","medium","-c:a","aac","-b:a","192k",base],check=True)
    json.dump({"words":fw,"total_final":round(total_final,3),"speed":speed},
              open(os.path.join(wd,"plan.json"),"w"), ensure_ascii=False)
    print("BASE_OK total_final", round(total_final,2), "keeps", len(keeps))
if __name__=="__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv)>3 else 1.25)
