# Hybrid Gym Assistant — B-roll package for today

## Production decision

Use Sagar on camera for **0–5s** and **43–50s**. Everything between those
moments is a static, vertically framed GPT-2.5 image with a gentle 4–6% zoom
in while editing. Do not use generated video for this Reel.

The visuals must look like evidence from one small system, not stock AI art:
warm off-white background, charcoal type, electric-blue routing lines, muted
lime only for the hybrid/Jev route, and restrained amber/red only for risk.

## Required assets

| ID | Reel time | File name | What it proves | Source |
| --- | --- | --- | --- | --- |
| B1 | 5–11s | `01-messy-check-in.png` | The viewer's original message is ambiguous, not a clean model input. | GPT-2.5 image prompt 1 |
| B2 | 11–17s | `02-gpt-cleans-input.png` | GPT's role is to turn human language into usable state. | GPT-2.5 image prompt 2 |
| B3 | 17–25s | `03-jev-risk-route.png` | Jev receives the state and selects one bounded route, including human review. | GPT-2.5 image prompt 3 |
| B4 | 25–29s | `04-policy-block.png` | The workflow—not a free-form response—enforces the risk boundary. | GPT-2.5 image prompt 4 |
| B5 | 29–37s | `05-two-paths.png` | The fair comparison is `GPT → GPT` versus `GPT → JEV`. | GPT-2.5 image prompt 5 |
| B6 | 37–43s | `06-result-estimate.png` | The controlled architecture estimate: 36% less waiting and 49% lower model cost. | GPT-2.5 image prompt 6 |
| T1 | Cover / thumbnail | `thumbnail-99-to-49.png` | The curiosity gap: why does 99% become 49%? | GPT-2.5 thumbnail prompt |

## Editing order

1. Sagar, direct-to-camera: hook. Overlay `99% → 49%` as text in the edit.
2. B1 through B4: use each still for its single spoken claim; do not reuse a
   still for another claim.
3. B5: hold long enough to read both complete paths.
4. B6: remain on screen for the complete numbers. The visible disclosure must
   stay: `ESTIMATE · LIVE LOGS PENDING`.
5. Sagar, direct-to-camera: the three-part operating rule and close.

## Real-material option

If available, replace the **message card inside B1 only** with an actual
anonymised Gym Assistant check-in before rendering. The exact wording must
still lead to the same state shown in B2. Do not manufacture code logs,
model-response screenshots, or performance graphs.

## Do not do

- Do not use the old sci-fi gym-agent renders: they do not prove this
  comparison.
- Do not show robots, model logos, neural brains, terminal windows, or generic
  dashboards.
- Do not show `99%` as the hybrid result. It is component context only.
- Do not remove the estimate disclosure from B6.
