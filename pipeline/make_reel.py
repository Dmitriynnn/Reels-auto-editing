"""
make_reel.py <video> <edit_plan.json> <out.mp4> [workdir]
Механическая сборка ролика по готовому edit_plan (его пишет Claude из транскрипта).
Порядок: build_base -> facescan -> render_overlays -> compose -> mix_audio -> encode.
Требует уже созданный <workdir>/words.json (шаг transcribe.py).
"""
import sys, os, json, subprocess
HERE=os.path.dirname(os.path.abspath(__file__))
def run(mod,*args):
    subprocess.run([sys.executable,os.path.join(HERE,mod),*[str(a) for a in args]],check=True)
def main(video, plan, out, wd=None):
    wd=wd or os.path.join(os.path.dirname(os.path.abspath(out)),"_work")
    os.makedirs(wd,exist_ok=True)
    if not os.path.exists(os.path.join(wd,"words.json")):
        run("transcribe.py",video,wd)
    ep=json.load(open(plan)); speed=ep.get("speed",1.25)
    run("build_base.py",video,wd,speed)
    run("facescan.py",wd)
    run("render_overlays.py",wd,plan)
    run("compose.py",wd)
    run("mix_audio.py",wd)
    subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-framerate","30",
        "-i",os.path.join(wd,"frames_final","%05d.png"),"-i",os.path.join(wd,"mixaudio.m4a"),
        "-map","0:v","-map","1:a","-c:v","libx264","-crf","18","-preset","medium",
        "-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",out],check=True)
    print("REEL_DONE ->",out)
if __name__=="__main__":
    main(*sys.argv[1:])
