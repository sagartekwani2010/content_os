# H3 Combined 01 — Trajectory and memory gap

**Output:** `01-trajectory-memory-gap.mp4`  
**Settings:** H3 text-to-video, 16:9, 12 seconds, 24 fps, complete silence.

```text
integrated_multimodal_description: [Shot 1] A simple flat 2D instructional animation on a plain warm-white background, designed to explain one mechanism clearly rather than look cinematic. Use a fixed straight-on camera with no zoom, pan, depth, texture, shadows or decorative motion. Keep every object and every letter large and inside the central 55 percent of the 16:9 frame. Reserve the top 28 percent of the safe area for large, bold, uppercase charcoal text in a clean geometric sans-serif. Render only the exact text specified below. Keep every word stable, correctly spelled and fully readable; do not invent, paraphrase, duplicate or morph any letters.

From 0.00 to 2.50 seconds, render the exact title `TRAJECTORY` at the top. Beneath it, show one dark-grey rounded rectangle containing the exact word `QUERY` on the far left of the safe area. A single blue arrow grows from it toward a large magnifying-glass icon with the exact label `ACTION` below it. Nothing else moves.

From 2.50 to 5.00 seconds, the search icon produces one white result card containing the exact word `RESULT`. Only after the result card is fully visible, a second blue arrow grows toward a simple diamond containing the exact two-line label `NEXT` and `ACTION`. A small blue information dot travels from the result card along the arrow into the decision diamond. This must clearly show that the result of one step becomes the input to the next step.

From 5.00 to 6.50 seconds, the decision diamond selects one of two short outgoing paths. The selected path turns muted lime while the other stays light grey. Hold the completed four-part chain clearly on screen: query, search, result, next decision.

From 6.50 to 9.00 seconds, replace the top title with the exact text `PAST RUN ≠ FUTURE LEARNING`. Move the completed chain slightly upward without changing any objects or their labels. Directly below it, reveal a second identical chain using empty light-grey outlines and no words inside the objects. Leave a clear physical gap between the completed upper chain and the new lower chain. Do not draw any arrow connecting them.

From 9.00 to 10.50 seconds, one small blue information dot leaves the completed chain and moves toward the gap, but stops at a thin red boundary line before reaching the new chain. The new chain remains completely empty and unchanged. This must communicate that finishing one run does not automatically transfer learning into the next run.

From 10.50 to 12.00 seconds, hold the final comparison with no motion: completed coloured chain above, empty outlined future chain below, blue information dot stopped at the red boundary. The final frame must remain readable for at least 1.5 seconds.

Use only five visual symbols: rounded query rectangle, magnifying glass, result card, decision diamond and directional arrows. Use dark grey for inactive objects, electric blue for information flow, muted lime for the selected action, light grey for the untouched future run and one thin red line for the missing transfer. Complete silence throughout. Apart from the exact specified labels, generate no other text, letters or numbers. No 3D objects, people, robots, faces, logos, branded interface, realistic computer screens, code, dashboards, gradients, lighting effects, particles, holograms, neural networks, camera movement, scene cuts or ornamental animation.

overall_soundscape: N/A

non_diegetic_music: N/A
```

**Text baked into the H3 generation:**

- 0.00–6.50s: `TRAJECTORY`, plus the object labels `QUERY`, `ACTION`,
  `RESULT`, `NEXT ACTION`
- 6.50–12.00s: `PAST RUN ≠ FUTURE LEARNING`

**Accept when:** a first-time viewer can explain, without hearing the voiceover,
that results guide later steps inside one run but do not automatically improve
the next run. Reject if H3 adds decorative motion, changes the icons, animates
multiple causal steps simultaneously, connects the two runs, or makes the final
comparison unreadable after the centre crop, or misspells any specified label.
