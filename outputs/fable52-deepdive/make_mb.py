import sys, pathlib
sys.path.insert(0, str(pathlib.Path.home() / "Desktop/codebases/content_os"))
from content_os.orchestrator import modelcall, moodboard
script, outdir, title = sys.argv[1:4]
txt = pathlib.Path(script).read_text()
prompt = ("REEL: " + title + "\nStyle: house style - bright hand-drawn line and architecture diagrams on dark, tables that fill row by row, full-frame section cards; the creator seated in the bottom half. "
          "Tone and colour must follow the TONE GUIDE in the screenplay (positive = warm, bright; fear = cold, desaturated, red accents). "
          "\n\nSCREENPLAY:\n" + txt[:16000])
out, prov = modelcall.call("moodboard", prompt, modelcall.MoodboardOut)
mb = out.model_dump()
d = pathlib.Path(outdir); d.mkdir(exist_ok=True)
moodboard.write_board(d, mb, title)
moodboard.render_frames(d, mb)
moodboard.write_board(d, mb, title)
print(title, len(mb["keyframes"]), "keyframes", prov.get("model"), prov.get("seconds"))
