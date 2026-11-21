import sys, pymupdf
doc = pymupdf.open("fable52_system_card.pdf")
jobs = [("P14_p186", 186, "among the least self-critical Claude models when|on its own work"),
        ("P15_p34", 34, "quit without running an experiment in 63% of sessions at medium effort"),
        ("P16_p91", 91, "aware that it may be in an evaluation in as many as 43% of automated behavioral audit transcripts"),
        ("P17_p216", 216, "Fable 5.2 scored 91.6% (up from 85.6%)")]
for name, pno, phrase in jobs:
    pg = doc[pno - 1]
    hits = [h for ph in phrase.split("|") for h in pg.search_for(ph)][:3]
    if not hits:
        # try a shorter prefix
        hits = pg.search_for(" ".join(phrase.split()[:5]))
    if name == "P14_p186" and len(hits) >= 2: hits.append(pymupdf.Rect(hits[0].x1, hits[0].y0, hits[1].x0, hits[0].y1))
    print(name, len(hits), [tuple(round(v) for v in h) for h in hits][:4])
    if not hits: continue
    for h in hits:
        a = pg.add_highlight_annot(h); a.set_colors(stroke=(1, 1, 0)); a.update()
    y0 = min(h.y0 for h in hits) - 1.5; y1 = max(h.y1 for h in hits) + 2.5
    blocks = [b for b in pg.get_text("blocks") if b[1] <= y1 and b[3] >= y0]
    x0 = min(b[0] for b in blocks) - 8; x1 = max(b[2] for b in blocks) + 8
    clip = pymupdf.Rect(x0, y0, x1, y1)
    z = 1480 / clip.width
    pg.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=clip).save(f"cuts/tight/{name}.png")
