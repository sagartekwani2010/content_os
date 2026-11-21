import sys, pathlib
sys.path.insert(0, str(pathlib.Path.home() / "Desktop/codebases/content_os"))
from content_os.orchestrator import modelcall, moodboard
script, outdir, title = sys.argv[1:4]
txt = pathlib.Path(script).read_text()
prompt = ("REEL: " + title + "\nThis reel's real props and demos matter more than drawings: card flips, a task board with stickies, tape, "
          "laptop screen recordings of AI attempting tasks, the ChatGPT 'Run #1' GPT on a phone. Keep the house split layout where it helps "
          "(top: hand-drawn line diagram or screen recording; bottom: creator), go full-frame for real demos and props.\n\nSCREENPLAY:\n" + txt[:16000])
out, prov = modelcall.call("moodboard", prompt, modelcall.MoodboardOut)
mb = out.model_dump()
d = pathlib.Path(outdir); d.mkdir(exist_ok=True)
moodboard.write_board(d, mb, title)
moodboard.render_frames(d, mb)
moodboard.write_board(d, mb, title)
print(title, len(mb["keyframes"]), "keyframes", prov.get("model"), prov.get("seconds"))
