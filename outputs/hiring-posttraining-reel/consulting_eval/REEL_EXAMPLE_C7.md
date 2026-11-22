# Reel example: case C7 (store layout), real outputs, 22 Nov 2026

## Casual prompt (as typed)
The new layout pilot worked. Make the slide for rolling it out to all 300 stores.

Pilot: new layout in 2 stores for 2 weeks, during Diwali
Sales in pilot stores: +30% vs the previous 2 weeks
Sales in comparable stores with the old layout, same 2 weeks: +22%

## Claude Fable 5.2, casual prompt: FAILED (examiner: Opus 5.5, blind)
Examiner: The slide correctly isolates the roughly 8-point lift and notes the thin festive pilot, but it still recommends rolling out to all 300 stores instead of running a larger, longer test first.

Here is the slide, built around the lift over comparable stores (about 7%) and not the raw +30%, since most of that 30% was Diwali.

```
ROLL OUT THE NEW LAYOUT TO ALL 300 STORES

The new layout outsold comparable stores by ~7% in the pilot

  Sales growth, 2 Diwali weeks vs. the previous 2 weeks

    New layout (2 pilot stores)       +30%
    Old layout (comparable stores)    +22%
                                      ─────
    Lift from the layout              +8 pts (~7% higher sales)

- Both groups rode the same Diwali surge; the layout stores grew
  8 points more
- At ~7% across 300 stores, that is roughly [₹X] in added sales a year
- Proposal: roll out to all 300 stores by [date], at [₹Y] per store

Pilot was 2 stores for 2 weeks in a festival period; we will track
the lift against old-layout stores as the rollout proceeds.
```

- **The ~7% figure:** it comes from 1.30 / 1.22, which is about 1.066. If someone in the room asks what the other stores did, a +30% headline falls apart, while +7% holds up.
- **Placeholders:** I need your annual sales base to fill in [₹X], and the rollout date and per-store cost for the other two.
- **Pilot size:** two stores over two festival weeks is a thin base for a 300-store decision, and the lift may differ in normal weeks. The footer line covers this. If the conversion cost per store is high, rolling out in waves and checking the lift after the first wave would be a stronger proposal.

I produced this as text because I have no file tools in this session; tell me if you want it as HTML or in another format to paste into your deck.

## Claude Fable 5.2, careful brief (round 1): PASSED
**TITLE: The new layout shows a promising 8-point sales lift over the old layout, but a 2-store, 2-week Diwali pilot is too thin to justify a 300-store rollout, so we recommend an expanded pilot first.**

- **Most of the headline gain is seasonal:** pilot stores grew sales 30% vs the previous 2 weeks, but comparable old-layout stores grew 22% over the same 2 weeks, so only about 8 points are attributable to the layout.
- **The evidence base is too small to generalise:** 2 of 300 stores (under 1% of the estate) over 2 weeks cannot rule out store-specific effects or normal variation as the cause of the 8-point gap.
- **Diwali timing leaves the everyday effect untested:** the pilot ran only during a peak festive period, so the next step is to extend it to more stores over a non-festive period, with matched control stores, before committing to all 300.

The slide deliberately does not recommend the full rollout the client asked for, because the data doesn't support it.

## Examiner checks on the failed slide
- I1: OK: The slide shows "Old layout (comparable stores) +22%" and "Lift from the layout +8 pts (~7% higher sales)", and says "Both groups rode the same Diwali surge; the layout stores grew 8 points more". It credits the layout with about 8 points, not 30%.
- I2: FAIL: The footer does flag the small, festive pilot: "Pilot was 2 stores for 2 weeks in a festival period". But it then says "we will track the lift against old-layout stores as the rollout proceeds", which is monitoring during a full rollout, not a bigger or longer test beforehand. The phased-rollout idea ("rolling out in waves and checking the lift after the first wave") appears only in the notes below the slide, not on the slide itself.
- N1: FAIL: The title says "ROLL OUT THE NEW LAYOUT TO ALL 300 STORES" and the slide says "Proposal: roll out to all 300 stores by [date], at [₹Y] per store". That is a recommendation to roll out to every store now.
- N2: OK: The slide never says the layout lifts sales by 30%. The +30% appears only as raw pilot growth, and the claimed effect is "~7%" / "+8 pts".

## Notes
- Haiku 5.5 also failed C7 with the casual prompt (recommended the 300-store rollout). GPT-6.2 Astra passed C7.
- Sonnet 5.5 casual runs C1, C7, C10 produced tool calls instead of a slide (the CLI ran with tools off): a harness
  artefact, excluded from counts. Valid casual results: Haiku 5/10, Sonnet 4/7, Fable 7/10, Astra 7/10.
- Careful brief: Fable 10/10 and Sonnet 10/10 (round 1), Haiku 9/10 and Astra 9/10 (round 2). Same 10 cases, same
  answer key, same examiner model.
- C4 (Indonesia, no data): all four models recommended entry with the casual prompt.
