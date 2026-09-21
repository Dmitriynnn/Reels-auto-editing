"""
Стиль-ядро reels (ProDesign/@yanadlx). Шрифты — OFL-аналоги с кириллицей
(оригиналы коммерческие). Все размеры под кадр 1080x1920.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE=os.path.dirname(os.path.abspath(__file__))
FONTS=os.path.join(HERE,"..","assets","fonts")
W,H=1080,1920

# палитра
CREAM=(243,238,229,255); WARM=(233,214,186,255)
GREEN=(150,205,150,255); RED=(214,110,104,255)

_FCACHE={}
def _vfont(fname,size,wght):
    key=(fname,size,wght)
    if key in _FCACHE: return _FCACHE[key]
    f=ImageFont.truetype(os.path.join(FONTS,fname),size)
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    _FCACHE[key]=f; return f
# роли (замены оригиналов): Stadium->Oswald, Gramatika->Montserrat, Baystar->Caveat, Anticva->Playfair
def stad(s):  return _vfont("Oswald.ttf",s,700)          # конденсед-хук
def gram(s):  return _vfont("Montserrat.ttf",s,700)      # заголовочный гротеск
def gramr(s): return _vfont("Montserrat.ttf",s,500)      # субтитры/капшены
def scr(s):   return _vfont("Caveat.ttf",s,700)          # рукописный
def serif(s): return _vfont("PlayfairDisplay.ttf",s,700) # серив (опц.)

TMP=ImageDraw.Draw(Image.new("RGB",(10,10)))
def canv(h): return Image.new("RGBA",(W,h),(0,0,0,0))

def dsh(im,xy,text,fnt,fill=CREAM,anchor="mm",sh=(0,5),blur=14,sa=155,track=0):
    """текст с мягкой тенью (без плашки). track>0 — разрядка."""
    d=ImageDraw.Draw(im)
    def dr(drw,x,y,col):
        if track:
            ws=[drw.textlength(c,font=fnt) for c in text]; tot=sum(ws)+track*(len(text)-1); cx=x-tot/2
            for c,wc in zip(text,ws): drw.text((cx,y),c,font=fnt,fill=col,anchor="lm"); cx+=wc+track
        else: drw.text((x,y),text,font=fnt,fill=col,anchor=anchor)
    sl=Image.new("RGBA",im.size,(0,0,0,0)); sd=ImageDraw.Draw(sl)
    dr(sd,xy[0]+sh[0],xy[1]+sh[1],(0,0,0,sa)); sl=sl.filter(ImageFilter.GaussianBlur(blur))
    im.alpha_composite(sl); dr(d,xy[0],xy[1],fill)

def fit(text,maker,start,maxw=780,minsz=44):
    s=start
    while s>minsz and TMP.textlength(text,font=maker(s))>maxw: s-=2
    return maker(s)

# ---------------- СПРАЙТЫ (RGBA, контент в y[8..~195], высота<=210; contrast<=294) ----------------
def s_hook(kicker,lines):
    im=canv(210)
    if kicker: dsh(im,(W//2,20),kicker.upper(),gram(30),fill=WARM,track=6)
    f=fit(max(lines,key=len),stad,100)
    y=74
    for ln in lines: dsh(im,(W//2,y),ln.upper(),f); y+=int(f.size*0.84)
    return im
def s_section(tag,kw,cap):
    im=canv(210); dsh(im,(W//2,14),tag,gram(32),fill=WARM,track=8)
    dsh(im,(W//2,74),kw.upper(),fit(kw.upper(),stad,96))
    if cap: dsh(im,(W//2,178),cap,fit(cap,gramr,38,maxw=740))
    return im
def s_quote(small_top,big,small_bot):
    im=canv(210)
    if small_top: dsh(im,(W//2,14),small_top,gramr(42))
    dsh(im,(W//2,74),big.upper(),fit(big.upper(),stad,86))
    if small_bot: dsh(im,(W//2,168),small_bot,gramr(48),fill=WARM)
    return im
def s_tag(text,warm=False):
    im=canv(120); dsh(im,(W//2,60),text,gramr(46),fill=(WARM if warm else CREAM),blur=18,sa=185); return im
def s_flow(word):
    im=canv(210); dsh(im,(W//2,100),word,fit(word,stad,100),fill=WARM)
    dsh(im,(W//2-260,44),word,gramr(38),fill=(*CREAM[:3],140),track=1)
    dsh(im,(W//2+250,170),word,gramr(38),fill=(*CREAM[:3],140),track=1); return im
def s_razbor(small_top,big,caption):
    im=canv(210)
    if small_top: dsh(im,(W//2,12),small_top,gramr(38))
    dsh(im,(W//2,72),big.upper(),fit(big.upper(),stad,100),fill=WARM)
    if caption: dsh(im,(W//2,176),caption,fit(caption,gramr,32,maxw=820))
    return im
def s_contrast(title,bad,good):
    cw,ch=790,214; card=Image.new("RGBA",(cw+80,ch+80),(0,0,0,0))
    sh=Image.new("RGBA",card.size,(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle([40,50,40+cw,50+ch],radius=32,fill=(0,0,0,80))
    card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(24)))
    d=ImageDraw.Draw(card); d.rounded_rectangle([40,40,40+cw,40+ch],radius=32,fill=(18,18,20,140))
    d.text((80,60),title.upper(),font=stad(50),fill=WARM,anchor="lm")
    d.line([84,126,110,152],fill=RED,width=8); d.line([110,126,84,152],fill=RED,width=8)
    d.text((140,140),bad,font=gramr(33),fill=(175,158,150,255),anchor="lm")
    d.line([84,190,104,210],fill=GREEN,width=8); d.line([104,210,132,178],fill=GREEN,width=8)
    d.text((140,200),good,font=gramr(37),fill=CREAM,anchor="lm")
    return card
def s_outro(big_lines,sign):
    im=canv(210); y=50
    f=fit(max(big_lines,key=len).upper(),stad,104)
    for ln in big_lines: dsh(im,(W//2,y),ln.upper(),f); y+=int(f.size*0.86)
    if sign: dsh(im,(W//2+150,y+30),sign,scr(58),fill=WARM,blur=8)
    return im
