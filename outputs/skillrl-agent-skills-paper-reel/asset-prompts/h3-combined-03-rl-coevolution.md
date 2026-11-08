# H3 Combined 03 — RL and SkillBank co-evolution

**Output:** `05-rl-coevolution.mp4`  
**Settings:** H3 text-to-video, 16:9, 15 seconds, 24 fps, complete silence.

```text
integrated_multimodal_description: [Shot 1] A simple flat 2D instructional animation on a plain warm-white background. Use a fixed straight-on camera with no zoom, pan, depth, texture, shadows or decorative motion. Keep every object and every letter large and inside the central 55 percent of the 16:9 frame. Reserve the top 25 percent of the safe area for large, bold, uppercase charcoal text in a clean geometric sans-serif and the bottom 10 percent for one small evidence disclosure. Create two stable horizontal lanes: a policy-learning lane above and a SkillBank-evolution lane below. Render only the exact text specified below. Keep every word stable, correctly spelled and fully readable; do not invent, paraphrase, duplicate or morph any letters.

Throughout all 15 seconds, render the exact small disclosure `AUTHOR-REPORTED · NOT INDEPENDENTLY REPRODUCED` along the bottom of the safe area. From 0.00 to 3.00 seconds, render the exact top title `TASK → REWARD → POLICY UPDATE`. In the upper lane, move one dark-grey task token to a decision diamond with two outgoing paths. The token chooses the upper light-grey path and reaches an amber no-reward endpoint. Return the token to the decision diamond. Keep the diagram stable.

From 3.00 to 6.00 seconds, the same token chooses the lower path and reaches a muted-lime reward circle. Only after the reward appears, thicken the successful lower path in electric blue and make the unsuccessful upper path thinner. Move a small policy-pointer triangle at the decision diamond toward the rewarded path. This sequence must show reward changing the later decision preference.

From 6.00 to 8.00 seconds, run the task token once more. It now chooses the strengthened lower path immediately and reaches the reward. Hold the updated policy state.

From 8.00 to 11.00 seconds, replace the top title with the exact two-line title `VALIDATION FAILURE → REVIEW` and `REVIEW → SKILLBANK UPDATE`. In the lower lane, show a new task trajectory ending in an amber validation-failure cross. Move that failed trajectory into a small blue-outline review gate containing the exact label `REVIEW`. Only after it passes through the gate, highlight one gap in a tidy two-level library of skill cards.

From 11.00 to 13.50 seconds, replace exactly one highlighted skill card with a refined muted-lime-edged version. Leave every other card unchanged. Do not connect the validation failure directly to the upper policy lane; these are two coordinated learning processes during reinforcement learning, not one uncontrolled update.

From 13.50 to 15.00 seconds, replace the top title with the exact two-line title `POLICY + SKILLBANK` and `IMPROVE TOGETHER`. Hold both completed lanes together: the upper policy now favours the rewarded route and the lower SkillBank contains one controlled refinement. Add one thin blue bracket linking the two lanes only in this final hold to communicate that both improve during the overall training process.

Use dark charcoal outlines, electric blue for learned information flow, muted lime for reward and validated refinement, amber for failed attempts, light grey for inactive paths and one restrained red validation cross. Complete silence throughout. Apart from the exact specified labels, generate no other text, letters or numbers. No 3D objects, people, robots, faces, logos, branded interfaces, code, dashboards, gradients, lighting effects, particles, holograms, neural networks, camera movement, scene cuts or ornamental animation.

overall_soundscape: N/A

non_diegetic_music: N/A
```

**Text baked into the H3 generation:**

- 0.00–8.00s: `TASK → REWARD → POLICY UPDATE`
- 8.00–13.50s: `VALIDATION FAILURE → REVIEW → SKILLBANK UPDATE`
- 13.50–15.00s: `POLICY + SKILLBANK IMPROVE TOGETHER`
- Keep on screen throughout: `AUTHOR-REPORTED · NOT INDEPENDENTLY REPRODUCED`

**Accept when:** every specified line is correctly spelled and remains stable,
reward first changes the policy, a later validation failure is
reviewed before exactly one SkillBank entry changes, and both end states remain
visible together. Reject if a failure instantly rewrites the whole system, the
SkillBank changes before review, all objects transform at once, or the evidence
disclosure becomes unreadable.
