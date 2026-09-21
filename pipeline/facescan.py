"""
facescan.py <workdir>
Определяет зону лица по base.mp4 (cv2 FaceDetectorYN / yunet) и пишет face.json:
{top, sub_y, ay, forbid:[x0,y0,x1,y1]} — safe-зоны для оверлеев.
При неудаче — консервативные дефолты.
"""
import sys, os, json
HERE=os.path.dirname(os.path.abspath(__file__))
DEF={"top":222,"sub_y":1292,"ay":0.34,"forbid":[300,470,780,830]}
def main(wd):
    out=os.path.join(wd,"face.json")
    try:
        import cv2, numpy as np
        model=os.path.join(HERE,"..","assets","models","face_detection_yunet.onnx")
        det=cv2.FaceDetectorYN.create(model,"",(320,320),0.6,0.3,5000)
        cap=cv2.VideoCapture(os.path.join(wd,"base.mp4"))
        fps=cap.get(cv2.CAP_PROP_FPS) or 30; step=max(1,int(fps*0.3)); i=0; B=[]
        det.setInputSize((1080,1920))
        while True:
            ok,fr=cap.read()
            if not ok: break
            if i%step==0:
                _,faces=det.detect(fr)
                if faces is not None and len(faces):
                    f=max(faces,key=lambda r:r[2]*r[3]); x,y,w,h=f[:4]
                    B.append((float(x),float(y),float(w),float(h)))
            i+=1
        cap.release()
        if len(B)<5: raise RuntimeError("too few faces")
        a=np.array(B); xs,ys,ws,hs=a[:,0],a[:,1],a[:,2],a[:,3]
        L=float(np.percentile(xs,10)); R=float(np.percentile(xs+ws,90))
        T=float(np.percentile(ys,10)); Bt=float(np.percentile(ys+hs,90))
        cy=float(np.median(ys+hs/2))
        top=int(min(max(T-218,196),300))
        sub_y=int(min(max(Bt+360,1150),1340))
        ay=round(min(max(cy/1920.0,0.22),0.5),3)
        res={"top":top,"sub_y":sub_y,"ay":ay,"forbid":[int(L),int(T),int(R),int(Bt)],"n":len(B)}
    except Exception as e:
        res=dict(DEF); res["error"]=str(e)
    json.dump(res,open(out,"w"))
    print("FACE", res)
if __name__=="__main__":
    main(sys.argv[1])
