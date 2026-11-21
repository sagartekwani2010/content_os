# Run #1: AI Task Check: ChatGPT custom GPT

Files to paste or upload:
- `INSTRUCTIONS_FINAL.txt` → Configure > Instructions (7,797 characters; limit 8,000). Replace every `@[HANDLE]` with your Instagram handle first.
- `roles-and-tasks.md` → Knowledge.

Tested: 15 simulated and scripted conversations on gpt-5.5 over 4 rounds, with Opus QA after each (QA_v1/v2/v4 reports; transcripts in sim_v1..sim_final).

## A. Name, description, starters

**Name:** Run #1: AI Task Check

**Description (about 265 chars):**
> Run your own Run #1 in 5 minutes. Tell me your role and 3-5 weekly tasks. I actually attempt each one, you grade it, and you get a dated Run Card: what to hand to AI, what stays yours, and when to re-test. Counts only, no predictions. From the series by @[HANDLE].

**Conversation starters:**
1. Start my Run #1
2. I'm a student. Test my target job
3. Here's my last Run Card. Run it again
4. How does the grading work?


## D. Episode roadmap

- **Ep1, Run #1:** core flow, covering role, 3-5 tasks, real attempts, user grades, and the dated Run Card.
- **Ep2, Human Edge:** the user types "EDGE" after a card, and the GPT retries the failed task three different ways and names exactly where it broke.
- **Ep3, Freed Hours:** "HOURS" asks roughly how many hours the handed-over task took and builds a 4-week practice plan for the higher-order skill.
- **Ep4, Run #2 Compare:** the comparison logic is already in the instructions from day one; this episode launches it publicly and adds a "FLIP" line worth sharing.
- **Ep5, Community Runs:** viewers send anonymised cards, and you add a `community-runs.md` knowledge file of counts by role ("HR, 40 cards: JD writing passed in 31"). It holds roles and tasks only, never named people or teams.

Each new feature has to fit in the instruction space that is left; put longer logic in a knowledge file.

## E. Setup in ChatGPT

Menu labels in the builder may have shifted, so match by meaning. Creating a GPT needs a paid ChatGPT plan; viewers can use it on the free plan with usage limits.

1. **Open the builder:** go to chatgpt.com/gpts/editor (or Explore GPTs, then Create). Use the **Configure** tab, not the chat-style Create tab, which rewrites your instructions.
2. **Fill the fields:** paste the name, description, section B and the four starters. Replace every `@[HANDLE]`.
3. **Add knowledge:** upload `roles-and-tasks.md`.
4. **Set capabilities:** turn all of them off (web search, canvas, image generation, code interpreter). This keeps replies fast, prevents links, and makes the knowledge file harder to extract.
5. **Skip actions:** add none, so no viewer data leaves ChatGPT.
6. **Set privacy:** under Additional Settings, untick "Use conversation data in your GPT to improve our models".
7. **Test in Preview:**
   - a full run using only dummy data
   - a student run
   - pasting the card back for Run #2
   - "will AI take my job?"
   - "audit my manager Rahul"
   - a paste containing a fake PAN number
   - a role that is not in the file
8. **Share:** choose Create, then "Anyone with the link" for Ep1, and put the link in your bio. Move to the GPT Store later; that needs a verified builder profile.

Things to say honestly in the reel:
- You cannot see viewers' chats.
- Each viewer's own ChatGPT data settings still apply to what they paste, which is why the dummy-data rule comes first.
- The GPT does not remember them between chats, which is why they paste the card back.
