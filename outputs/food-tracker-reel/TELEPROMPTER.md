# Teleprompter: food tracker reel (as recorded, IMG_3507.MOV, 16 November 2026)

Ground truth = the creator's chosen takes (see TAKES_ANALYSIS.md). The pre-shoot version is
TELEPROMPTER.as_planned.md.

**beat 1**
In last video, you met my Gym Jarvis.

**beat 2**
Today, let's see how it scans my plate for protein and calories.

**beat 3**
For building a system like this, I had Claude dig through a lot of research papers online.

**beat 4**
And I realized, naming items in your plate is super easy. But identifying the quantity of items is the hard part.

**beat 5**
So, I split the problem into three parts: find, size, and look up.

**beat 6**
Then I built two agents.

**beat 7**
The first agent is the vision agent on Fable 5.2, which lists the items and its grams.

**beat 8**
It's not allowed to say calories or proteins in those items.

**beat 9**
The second agent is the matcher agent, which finds all the items identified by the vision agent in our database.

**beat 10**
So every number traces back to a real source.

**beat 11**
I packaged all of it as a Claude skill with a single guardrail.

**beat 12**
Which was: if unsure, flag the meal for my review.

**beat 13**
Then I tested it on many meals that I had across days.

**beat 14**
And it performed with reasonable accuracy across all kinds of food.

**beat 15**
Except this one. Chicken hidden under carrots.

**beat 16**
And 500 calories just became 94.

**beat 17**
To explicitly handle cases like this, I added a confidence score.

**beat 18**
Now every meal is logged, and the less confident ones come to me for review.

**beat 19**
Next up, we'll see how my Workout Analyser tracks every set.
