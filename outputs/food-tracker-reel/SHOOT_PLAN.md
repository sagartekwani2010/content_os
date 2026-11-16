# Food tracker reel: what to record and how (17 November 2026)

Total time: about 60 minutes. **Order matters:** photos first, because beat 12 needs a number that
comes from your lunch photo.

## Step 1. Lunch photos (10 min, before any talking)

Plate your actual lunch on a plain plate, on a plain table, in daylight. iPhone **photo** mode, back
camera, 1x lens.

| # | Shot | How |
|---|---|---|
| P1 | Top-down | Phone flat, directly above, whole plate in frame with a little table around it |
| P2 | 45° | Seated eye-line, as you'd naturally photograph your meal |
| P3 | Top-down with a card | Same as P1, with a bank or ID card (number side down) flat beside the plate |

AirDrop all three to the Mac into `~/Movies/ContentOS/food-tracker/raw/photos/`, then tell me. I run
the tracker on P1 (about 15 s), get its question and how much your answer moves the number, and fill
beat 12 in the teleprompter. You answer its question truthfully (e.g. "yes, cooked in ghee", "two
spoons of rice under the dal").

## Step 2. B-roll (5 min)

Phone horizontal, 4K 30 fps, **HDR video off**. Hold each shot 8 seconds, steady (lean elbows on the
table or use the tripod).

| # | Shot | Used in |
|---|---|---|
| B1 | Over the shoulder: your hand taking the photo of the plate with a second phone | Beat 1 |
| B2 | Close-up of the plate, slow push in (or static) | Beats 12, 14 |

If you don't have a second phone for B1, film your hand holding the phone over the plate from the
side with the tripod.

## Step 3. Talking head (30–40 min)

### Camera

- iPhone **back camera, 1x**, **horizontal**, **4K 30 fps**, **HDR video off**
  (Settings › Camera › Record Video › HDR Video: off).
- Tripod at eye level, 1–1.5 m away. Head and shoulders in the middle half of the frame, eyes slightly
  above centre, space on both sides (the bottom half of the reel is cropped from this).
- Long-press your face on screen until **AE/AF LOCK** shows.
- **Chair that does not swivel or roll.** Sit back against it the same way every beat.
- Light in front of you (window or lamp), nothing bright behind you. One sitting, so the daylight doesn't
  change.

### Sound

- Wireless/lav mic if you have one; otherwise the phone at 1 m in a quiet room with soft furnishings.
- Fans and AC off. Phone on Do Not Disturb.

### The routine for each beat (laptop with `TELEPROMPTER.md` right next to the lens)

1. Say **"beat N"** clearly ("beat one", "beat two"…).
2. Read the line silently on the laptop.
3. Look into the lens. Say it.
4. **Silence for 2 seconds.** (The pipeline splits attempts at pauses; anything under half a second
   can merge two attempts.)
5. Say it again. A third time only if one of the two felt off.
6. Stumbled? Stop, 2 seconds of silence, restart the **whole line**. Never pick up mid-sentence.
7. Move to the next beat. Keep the camera rolling; one long file is fine. If you do stop, that's fine
   too; just say the "beat N" again when you restart.

### Delivery

- Talk to one friend across the table. Same energy from beat 1 to beat 14; don't fade at the end.
- Numbers slowly, with a small pause after them (beats 7–11).
- Beat 8: real pause before "Statistically, a tie."
- Inside a line, keep pauses short (under about half a second) so they don't read as gaps.

## Step 4. Room tone (30 s)

At the end, same position, same mic, stay silent and still for 30 seconds. Used to smooth joins.

## Step 5. Hand-off

Before you stop: play back beat 1 and beat 14. Face in the same place? Voice equally loud? Then AirDrop
everything into `~/Movies/ContentOS/food-tracker/raw/` and tell me. From there:

ingest → transcribe → split by "beat N" → score takes → Fable 5.2 checks the choices → cut-review page
(you approve) → split-screen render with visuals, captions, music → automatic checks → **you listen to
the final file** → post.
