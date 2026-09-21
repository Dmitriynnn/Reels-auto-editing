"""
render_overlays.py <workdir> <edit_plan.json>
Строит слой оформления по творческому плану (edit_plan) + таймингам (plan.json)
+ safe-зонам (face.json). Правила: всё над лицом / субтитры ниже; в верхней зоне
одновременно ОДИН блок (планировщик разносит стикеры); акцентные слова; без плашек.
Пишет frames/*.png и sfx.json.
"""
import sys, os, json, math
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style as st
W,H,FPS=1080,1920,30

def main(wd, plan_path):
    plan=json.load(open(os.path.join(wd,"plan.json"))); words=plan["words"]; DUR=plan["total_final"]
    face=json.load(open(os.path.join(wd,"face.json"))) if os.path.exists(os.path.join(wd,"face.json")) else {"top":222,"sub_y":1292}
    ep=json.load(open(plan_path))
    TOP=face.get("top",222); SUB_Y=face.get("sub_y",1292)
    FR=os.path.join(wd,"frames"); os.makedirs(FR,exist_ok=True)
    for f in os.listdir(FR): os.remove(os.path.join(FR,f))

    def cue_t(cue, default=None):
        if cue is None: return default
        if isinstance(cue,(int,float)): return float(cue)
        n=1
        if "@" in str(cue): cue,ns=cue.split("@"); n=int(ns)
        c=0
        for w in words:
            if cue.lower() in w["t"].lower():
                c+=1
                if c==n: return w["s"]
        return default

    EL=[]
    def E(t0,t1,sp,ty=TOP,anim="pop",sw=False,prio="hi"):
        EL.append({"t0":t0,"t1":t1,"sp":sp,"ty":ty,"anim":anim,"sw":sw,"prio":prio})

    hk=ep.get("hook")
    if hk:
        end=cue_t(hk.get("end_cue"), hk.get("end",2.6))
        E(0.0,end,st.s_hook(hk.get("kicker"),hk["lines"]),TOP,"fade")
        hook_end=end
    else: hook_end=0.0
    for s in ep.get("sections",[]):
        t=cue_t(s["cue"]);
        if t is None: continue
        E(t,t+s.get("dur",2.3),st.s_section(s["tag"],s["keyword"],s.get("caption","")),TOP,"fade",True)
    for s in ep.get("stickers",[]):
        t=cue_t(s["cue"]);
        if t is None: continue
        E(t,t+s.get("dur",1.7),st.s_tag(s["text"]),TOP+16,"pop",True,prio="lo")
    for c in ep.get("cards",[]):
        t=cue_t(c["cue"]);
        if t is None: continue
        if c.get("type")=="contrast":
            E(t,t+c.get("dur",2.5),st.s_contrast(c["title"],c["bad"],c["good"]),max(180,TOP-30),"pop",True)
    q=ep.get("quote"); quote_win=None
    if q:
        t=cue_t(q["cue"]); t1=cue_t(q.get("until_cue"), (t+3 if t else None))
        if t is not None:
            E(t,(t1 or t+3)-0.1,st.s_quote(q.get("small_top"),q["big"],q.get("small_bot")),TOP,"fade",True)
            quote_win=(t,(t1 or t+3)-0.1)
    cf=ep.get("cta_flow")
    if cf:
        t=cue_t(cf["cue"])
        if t is not None: E(t+0.1,t+0.1+cf.get("dur",3.0),st.s_flow(cf["word"]),TOP,"pop",True)
    rz=ep.get("razbor")
    if rz:
        t=cue_t(rz["cue"])
        if t is not None: E(t,t+rz.get("dur",3.0),st.s_razbor(rz.get("small_top"),rz["big"],rz.get("caption","")),TOP,"fade",True)
    ou=ep.get("outro")
    if ou: E(DUR-1.7,DUR+0.5,st.s_outro(ou["big"],ou.get("sign","")),TOP,"fade")

    # ---------- планировщик: верхняя зона = один блок, без наложений ----------
    GAP=0.38
    def bbox(e):
        a=e["sp"].split()[3].getbbox()
        return (e["ty"], e["ty"]+1) if a is None else (e["ty"]+a[1], e["ty"]+a[3])
    hi=sorted([e for e in EL if e["prio"]=="hi"], key=lambda e:e["t0"])
    for i in range(1,len(hi)):
        if hi[i]["t0"]<hi[i-1]["t1"]+GAP: hi[i-1]["t1"]=min(hi[i-1]["t1"],hi[i]["t0"]-GAP)
    hi=[e for e in hi if e["t1"]-e["t0"]>=0.4]
    reserved=[(e["t0"]-GAP,e["t1"]+GAP) for e in hi]
    def freeslot(s,dur,occ): return 0.2<=s and s+dur<=DUR-0.05 and all(not(s<y and x<s+dur) for x,y in occ)
    placed=[]; kept=[]
    for e in sorted([e for e in EL if e["prio"]=="lo"], key=lambda e:e["t0"]):
        dur=e["t1"]-e["t0"]; occ=reserved+placed; s0=e["t0"]; ch=None
        for d in [i*0.1 for i in range(0,46)]:
            for cand in ([s0] if d==0 else [s0+d,s0-d]):
                if freeslot(cand,dur,occ): ch=cand; break
            if ch is not None: break
        if ch is None:
            dur=1.2
            for d in [i*0.1 for i in range(0,46)]:
                for cand in ([s0] if d==0 else [s0+d,s0-d]):
                    if freeslot(cand,dur,occ): ch=cand; break
                if ch is not None: break
        if ch is not None:
            e["t0"]=round(ch,3); e["t1"]=round(ch+dur,3); placed.append((e["t0"],e["t1"])); kept.append(e)
    EL=hi+kept
    sfx=sorted({round(e["t0"],2) for e in EL if e["sw"]})
    viol=0
    for i in range(len(EL)):
        for j in range(i+1,len(EL)):
            a,b=EL[i],EL[j]
            if a["t0"]<b["t1"] and b["t0"]<a["t1"]:
                ay0,ay1=bbox(a); by0,by1=bbox(b)
                if ay0<by1 and by0<ay1: viol+=1
    json.dump(sfx,open(os.path.join(wd,"sfx.json"),"w"))

    # ---------- субтитры ----------
    STRONG=set(x.lower() for x in ep.get("accent_strong",[]))
    MILD=set(x.lower() for x in ep.get("accent_mild",[]))
    CENS=[x.lower() for x in ep.get("censor",[])]
    def norm(w): return ''.join(c for c in w.lower() if c.isalpha())
    def cens(t):
        for c in CENS:
            if c in t.lower(): return t[:len(c)]+"*"
        return t
    sc_={}
    def sub_sprite(word):
        if word in sc_: return sc_[word]
        n=norm(word); im=st.canv(180); disp=cens(word)
        if n in STRONG: st.dsh(im,(W//2,96),disp,st.fit(disp,st.stad,100),fill=st.WARM,blur=16,sa=185)
        elif n in MILD: st.dsh(im,(W//2,96),disp,st.fit(disp,st.gramr,74),fill=st.WARM,blur=15,sa=180)
        else: st.dsh(im,(W//2,96),disp,st.fit(disp,st.gramr,60),fill=st.CREAM,blur=14,sa=170)
        sc_[word]=im; return im
    def ease(p): return 1-(1-max(0,min(1,p)))**2
    def place(cv,sp,cx,cy,op,sc,top_anchor):
        if sc!=1.0: sp=sp.resize((max(1,int(sp.width*sc)),max(1,int(sp.height*sc))),Image.LANCZOS)
        if op<1.0:
            sp=sp.copy(); a=sp.split()[3].point(lambda v:int(v*op)); sp.putalpha(a)
        y=int(cy) if top_anchor else int(cy-sp.height/2)
        cv.alpha_composite(sp,(int(cx-sp.width/2),y))

    NF=int(math.ceil(DUR*FPS))+2
    for fi in range(NF):
        t=fi/FPS; cv=Image.new("RGBA",(W,H),(0,0,0,0))
        cur=None
        for w in words:
            if w["s"]-0.02<=t<w["e"]+0.28: cur=w
        hide=t<hook_end or (quote_win and quote_win[0]<=t<quote_win[1])
        if cur and not hide:
            place(cv,sub_sprite(cur["t"]),W//2,SUB_Y,ease((t-cur["s"])/0.06),1.0,top_anchor=False)
        for e in EL:
            if e["t0"]-0.03<=t<=e["t1"]:
                into=t-e["t0"]; rem=e["t1"]-t
                if e["anim"]=="pop":
                    if into<0.09: p=ease(into/0.09); op=p; scl=0.955+0.045*p
                    elif rem<0.12: op=max(0,rem/0.12); scl=1.0
                    else: op=1.0; scl=1.0
                else:
                    op=ease(into/0.15) if into<0.15 else (max(0,rem/0.2) if rem<0.2 else 1.0); scl=1.0
                place(cv,e["sp"],W//2,e["ty"],op,scl,top_anchor=True)
        cv.save(os.path.join(FR,f"{fi:05d}.png"))
    print("OVERLAYS frames",NF,"elements",len(EL),"swooshes",len(sfx),"collisions",viol)
if __name__=="__main__":
    main(sys.argv[1], sys.argv[2])
