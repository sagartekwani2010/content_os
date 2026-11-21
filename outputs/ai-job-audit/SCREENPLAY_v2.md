# AI Job Audit: screenplay v2 (concept stage)

All review fixes are applied except two that a custom GPT cannot honestly deliver ("no login" and fully deterministic scoring); see section 8. Percentages become counts, so `[MY_RESULT_%]` is replaced by `[MY_N]` of `[MY_TOTAL]`.

## 1. Logline and promise

An AI engineer audits his own week and a friend's non-tech week task by task on camera, then hands viewers the same free tool.

**Promise:** "AI meri job le lega" becomes a short list of what to hand over, what to grow, and what to try for two weeks.

## 2. Emotional arc

| Scene | Emotion | Why it turns |
|---|---|---|
| 1 Hook | Surprise | The AI guy is exposed too |
| 2 Reframe | Recognition | The fear shrinks from "job" to "tasks" in one line |
| 3 Friend | "That's me" | A non-tech job appears by 0:06 |
| 4 His audit | Vulnerability | He takes a hit too |
| 5 How | Ease | Tick tasks, no typing essay |
| 6 Output | Control | The fear becomes a 2-week plan |
| 7 CTA | Agency | Their turn, one comment |

## 3. Screenplay (about 55 s, Hinglish speech and captions)

**S1, 0:00–0:03. Hook**
- VISUAL: Full-frame real recording of his result, with the count circled by hand.
- SPOKEN: "Main AI banata hoon. Mere hafte ke [MY_TOTAL] tasks mein se [MY_N] AI already kar leta hai."
- TEXT: "AI engineer. [MY_N] of [MY_TOTAL] tasks: AI kar leta hai."
- EMOTION: Surprise.
- DELIVERY: Flat, with half a smile.

**S2, 0:03–0:06. Reframe**
- VISUAL: Top: a job box cracks into tiles. Bottom: him.
- SPOKEN: "AI poori job nahi karta. Tasks karta hai."
- TEXT: "Job nahi. Tasks."
- EMOTION: Recognition.
- DELIVERY: Slow and clear on "tasks".

**S3, 0:06–0:18. Friend's audit**
- VISUAL: Full-frame real recording, role tag on top, rows lighting up one by one.
- SPOKEN: "Mera dost [FRIEND_ROLE] hai. Uske [FRIEND_TOTAL] tasks mein se [FRIEND_N] AI aaj kar sakta hai, uski checking ke saath. [FRIEND_TASK_1] seedha AI ko de sakta hai. [FRIEND_TASK_2]? AI draft karega, sign wohi karega."
- TEXT: "[FRIEND_ROLE]: [FRIEND_N] of [FRIEND_TOTAL]". Tag: "AI draft, human sign-off".
- EMOTION: "That's me."
- DELIVERY: Warm, like a friend's story told with permission.

**S4, 0:18–0:27. His audit**
- VISUAL: Full-frame real recording of his rows.
- SPOKEN: "Mera? [MY_TASK_1]: AI kar leta hai. Yeh thoda chubha. [MY_TASK_2]: AI madad karta hai. [MY_TASK_3]: abhi bhi insaan chahiye."
- TEXT: The three rating tags.
- EMOTION: Vulnerability.
- DELIVERY: Real wince on "chubha", then a one-beat pause.

**S5, 0:27–0:36. How it works**
- VISUAL: Top: four role tiles, held about 2 s each (section 5). Then the task tick-list.
- SPOKEN: "Free tool hai. Apna role chuno, apne tasks tick karo. Hindi mein bhi chalega. Ek-do minute lagega."
- TEXT: "AI Job Audit. Free. Hindi / Hinglish OK."
- EMOTION: Ease.
- DELIVERY: Brisk, casual.

**S6, 0:36–0:46. Output**
- VISUAL: Top: three boxes tick in: "AI ko do", "Skill badhao", "2-week experiment".
- SPOKEN: "Yeh batata hai abhi AI ko kya dena hai, bache time mein kaunsi skill badhani hai, aur ek do-hafte ka experiment. Gym jaisa: weak lift dhoondo, wahi train karo. Layoff predict nahi karta. Koi nahi kar sakta."
- TEXT: "No layoff prediction. Sirf aapke tasks."
- EMOTION: Control.
- DELIVERY: Firm on the last two lines.

**S7, 0:46–0:55. CTA**
- VISUAL: His real result card, full-frame, then his face.
- SPOKEN: "Comment karo AUDIT aur apni job. Link DM karunga, pinned comment mein bhi hai. Sabse common jobs main agli reel mein audit karunga."
- TEXT: "Comment: AUDIT + your job".
- EMOTION: Agency.
- DELIVERY: Direct to lens, short.

## 4. Hooks, ranked

1. **Surprise (use this).** Frame: his real count. Text: "Main AI banata hoon. [MY_N] of [MY_TOTAL] tasks AI kar leta hai."
2. **Curiosity.** Frame: a result card with one row visible. Text: "Aapka kaunsa task AI aaj kar sakta hai?"
3. **Defiance.** Frame: arms crossed. Text: "AI meri job nahi lega. [MY_TASK_1] le lega."
4. **Humour.** Frame: deadpan. Text: "AI se poocha, mujhe replace kar sakta hai? Usne list bhej di."
5. **Fear (last).** Frame: a real, sourced headline. Text: "Sab darr rahe hain. Kisi ne check nahi kiya."

The final hook is chosen after the real run. If `[MY_N]` is low, use hook 3.

## 5. Relatability

- **S3 carries it:** `[FRIEND_ROLE]` must be a CA, bank employee or HR, on screen by 0:06.
- **S5 tiles:** four tiles, each a role plus one real task, readable for about 2 s.
  - IT services: "weekly status report"
  - CA: "GST reconciliation" (tag: AI draft, CA sign-off)
  - Bank: "KYC checks" (tag: human sign-off)
  - Teacher: "question paper banana"
- **Caption:** "Kisi bhi desk job ke liye. Tech knowledge nahi chahiye. Student ho? Target job chuno."
- **Words:** "hafte ka kaam", never "workflow" or "LLM".

## 6. Participation engine

- **Why they comment:** he and a friend went first, and their own result is withheld. "AUDIT + your job" is one line.
- **Why comments compound:** job titles in comments are social proof ("same, HR here") and research for Reel 2.
- **Why they finish:** role templates, tick-list, Hindi/Hinglish, voice dictation. Target: under 90 seconds.
- **Delivery:** the auto-DM triggers on comments *containing* "AUDIT". Test it on fresh accounts before posting, and keep the link in the pinned comment.
- **Result card:** screenshot-ready and safe for family and office groups (layout in section 8).
- **Send trigger:** the card footer reads "Alag job wale dost se compare karo".
- **Loop:**
  - Reel 2: the five most-commented jobs, audited on his own example weeks for those roles.
  - Reel 3: his own 2-week experiment, reported honestly even if it fails.

## 7. Risks and how the script avoids them

- **Fear-mongering:**
  - No layoff numbers are spoken, and the 66% figure stays out because it covers AI/ML workers only.
  - Every flagged task is paired with an action.
  - The card never shows a headline number.
- **Sales funnel:** free, with no email gate, course or waitlist. The DM is the link plus one line.
- **Fake:**
  - Every screen is a real recording, and placeholders stay until the runs happen.
  - The friend consents, or S3 uses a second role run on the creator's own described example, labelled as an example.
- **Unstable results:** counts from a fixed rubric, not percentages (section 8).
- **Regulated work:** KYC, GST filing and resume screening are never rated "AI kar leta hai".
- **Hurting someone's standing:** the card leads with actions, and "aapki checking ke saath" is attached to the top rating.
- **Managers auditing others:** the tool takes first-person input only, "aapka apna hafta".
- **Borrowed authority:** the caption says "inspired by task-based research" with links. Nothing on screen implies the numbers come from those papers.

## 8. Tool spec v1

**Inputs**
1. Mode: "My job" or "Target job" (students).
2. Role: pick from templates (IT services, CA, bank, HR, sales, teacher, other).
3. Tasks: a numbered list of 8–12 prefilled tasks. The user replies with numbers and adds 1–2 of their own, in Hindi, Hinglish or by voice.
4. First screen warning: "Naam, client ya company ka naam mat likho."

**Ratings**
- "AI kar leta hai, aapki checking ke saath"
- "AI madad karta hai"
- "Insaan chahiye"
- Flag: "AI draft, human sign-off"

**Output card (square)**
1. Role and "My AI Job Audit".
2. "AI ko do": top 1–2 tasks.
3. "Skill badhao": one skill.
4. "2-week experiment": one line.
5. Counts in small bars ("4 of 11 tasks"), no percentage.
6. Footer: "Layoff prediction nahi. Apna karo: comment AUDIT @handle."

**Guardrails**
- Template tasks carry ratings pre-written by the creator in a fixed table. The model rates only user-added tasks, against a written rubric.
- A regulated-task list forces the sign-off flag.
- The tool refuses to audit another named person or a team.
- It refuses layoff or salary predictions.
- Acceptance test: each template run five times must give identical counts.

**Platform decision (needed before the shoot)**

| | Custom GPT | Small web form with a fixed task table |
|---|---|---|
| Login | Needs a ChatGPT login | None |
| Scoring | No temperature control or caching | Deterministic |
| Privacy | Chats saved in the user's own ChatGPT history | Inputs need not be stored |

I recommend the web form, because rerun mismatches are the biggest credibility risk. If it stays a custom GPT, the reel says "free" but never "no login", and the acceptance test still has to pass.
