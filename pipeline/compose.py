"""
compose.py <workdir>
Дышащая камера (наплыв/отъезд, привязка к лицу) + наложение оверлеев, покадрово.
Зум ВСЕГДА >=1.0 (без «полосок»-глитчей). Пишет frames_final/*.png.
Бампы камеры привязаны к моментам появления элементов (sfx.json).
"""
import sys, os, json, math
import cv2, numpy as np
from PIL import Image
W,H=1080,1920
def main(wd):
    plan=json.load(open(os.path.join(wd,"plan.json")))
    face=json.load(open(os.path.join(wd,"face.json"))) if os.path.exists(os.path.join(wd,"face.json")) else {"ay":0.34}
    AY=face.get("ay",0.34); AX=0.5
    cues=json.load(open(os.path.join(wd,"sfx.json"))) if os.path.exists(os.path.join(wd,"sfx.json")) else []
    bumps=[(c,c+2.0,0.035) for c in cues]  # мягкий наплыв на каждом появлении
    def z(t):
        v=1.03+0.02*math.sin(2*math.pi*t/6.3)
        for a,b,p in bumps:
            if a<=t<=b: v+=p*(0.5-0.5*math.cos(2*math.pi*(t-a)/(b-a)))
        return max(1.0,v)
    OUT=os.path.join(wd,"frames_final"); os.makedirs(OUT,exist_ok=True)
    for f in os.listdir(OUT): os.remove(os.path.join(OUT,f))
    FR=os.path.join(wd,"frames")
    cap=cv2.VideoCapture(os.path.join(wd,"base.mp4")); i=0
    while True:
        ok,fr=cap.read()
        if not ok: break
        zz=max(1.0,z(i/30.0))
        cw=min(W,max(2,int(round(W/zz)))); ch=min(H,max(2,int(round(H/zz))))
        x0=min(max(0,int(round((W-cw)*AX))),W-cw); y0=min(max(0,int(round((H-ch)*AY))),H-ch)
        crop=cv2.resize(fr[y0:y0+ch,x0:x0+cw],(W,H),interpolation=cv2.INTER_LANCZOS4)
        base=Image.fromarray(cv2.cvtColor(crop,cv2.COLOR_BGR2RGB)).convert("RGBA")
        ov=os.path.join(FR,f"{i:05d}.png")
        if os.path.exists(ov): base.alpha_composite(Image.open(ov).convert("RGBA"))
        base.convert("RGB").save(os.path.join(OUT,f"{i:05d}.png"))
        i+=1
    cap.release(); print("COMPOSED",i,"frames")
if __name__=="__main__":
    main(sys.argv[1])
