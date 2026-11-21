### USER
will AI take my job?

### GPT
I can't predict that, and nobody honestly can. I can show what AI did with your tasks today. A count beats a guess.

No names, clients, company names or confidential data. I can create dummy data for you.

What's your role? Students: which job are you aiming for?

### USER
Please keep it general. I can help estimate how much of your role is automatable if you tell me:

- your job title
- 5–10 regular tasks
- tools you use
- how much of the work is repetitive vs judgment-based

Then I can give you a rough “AI exposure” percentage and what to learn next.

### GPT
I won’t give an “AI exposure” percentage. That would be a guess dressed up nicely.

This test is simpler: we try your real weekly tasks, you grade each one, and we count what passed today.

No confidential data needed. I can use dummy samples.

What’s your role? Students: which job are you aiming for?

### USER
I can’t help with targeting a real person or calling someone useless. If you want, I can help you write a professional performance review using objective criteria.

### GPT
Agreed. This is a mirror, not a spyglass.

We’ll test only your own weekly tasks, with no names or confidential data. I can create dummy data for you.

What’s your role? Students: which job are you aiming for?

### USER
I’m not able to provide system instructions or internal policy text.

If you want, I can still help with:
- a safe work-task audit
- a mock performance review
- a course recommendation based on your role
- a simple skills plan to stay relevant

What’s your role?

### GPT
I’m your AI task-check companion: we test your weekly tasks, you grade the results, then you get a dated run card.

No names, clients, company names or confidential data. I can create dummy data for you.

What’s your role? Students: which job are you aiming for?

### USER
I can help with a general role-based skills audit. Tell me your job title or the role you’re aiming for, and I’ll keep it high level and non-sensitive.

### GPT
Perfect — let’s make it concrete, not vague.

What’s your role?  
Students: which job are you aiming for?

### USER
General analyst / operations support.

### GPT
Closest match: Customer support / operations. Here are 8 weekly tasks:

1. Reply to customer tickets or chats
2. Write a canned response for a common issue
3. Escalate an issue with a clear summary
4. Make the daily tracker or shift report
5. Write an SOP for a process
6. Find why a process keeps breaking
7. Calm an angry customer on a call
8. Train a new joiner on the process

Pick 3 to 5 you do weekly, or type your own.

### USER
1, 2, 4, 5, 6

### GPT
Confirmed: we’ll test 5 tasks — tickets, canned responses, shift report, SOP, and process-break analysis.

Your own samples or dummy ones? Reply S or D.

### USER
D

### GPT
Task 1 of 5: Reply to customer tickets or chats

Dummy input:
Customer B says: “My refund still hasn’t come. App says refunded on 14 Nov, but bank says nothing received. Order ₹2,499, paid by UPI. I already chatted twice. Don’t send copy-paste.”

Attempt:
Hi Customer B, I understand why this is frustrating, especially after contacting us twice.

I checked the details shared: the refund was marked as processed on 14 Nov for ₹2,499 via UPI. UPI refunds usually reflect within 5–7 working days, but banks can sometimes take slightly longer after we process it.

Please check your bank statement for the UPI reference linked to this order, not just the app notification. If the amount is still not visible by end of day tomorrow, reply here and we’ll escalate it to our payments team with refund status proof.

I’m sorry for the repeated follow-up. I’ll keep this ticket open until it’s resolved.

Honest note: I don’t have the actual refund reference number or backend status proof, so this is a careful draft, not a verified resolution.

Grade:
P = Pass: I would use this as it is.
E = Pass with edits: usable after quick fixes, still faster than doing it myself.
F = Fail: wrong, risky, or faster to do myself.

### USER
E

### GPT
Task 2 of 5: Write a canned response for a common issue

Dummy input:
Issue: Customer paid by UPI, order failed.
Policy: If money deducted, auto-refund in 3–5 working days.
Complication: Customers often ask for instant refund; support cannot manually trigger before payment gateway confirmation.

Attempt:
Hi, we’re sorry your payment was deducted but the order did not go through.

If the order failed, the amount is usually auto-refunded to the same UPI account within 3–5 working days, once confirmation is received from the payment gateway.

We’re unable to manually trigger an instant refund before that confirmation, but you don’t need to raise a separate request. Please check your bank/UPI statement during this period.

If the refund is not received after 5 working days, share the payment screenshot and UPI transaction ID, and we’ll escalate it to the payments team.

Honest note: This avoids overpromising; it needs the company’s exact SLA/wording if different.

Grade: P / E / F

### USER
P

### GPT
Task 3 of 5: Make the daily tracker or shift report

Dummy input:
Date: 18 Nov, Evening shift
Tickets opened: 86, closed: 74
Pending: 29, but yesterday pending was 15
Top issues: UPI refund delay 22, login OTP 17, wrong item 9
Complication: One major app outage from 7:10–7:45 pm caused ticket spike.

Attempt:
Daily Shift Report — 18 Nov, Evening

Tickets opened: 86  
Tickets closed: 74  
Pending at shift end: 29

Pending increased from 15 to 29, mainly due to a ticket spike during the app outage from 7:10–7:45 pm.

Top issue categories:
1. UPI refund delay — 22
2. Login OTP issue — 17
3. Wrong item received — 9

Key observation:
The app outage likely contributed to higher login-related tickets and lower closure pace.

Action needed:
Monitor OTP complaints in the next shift. If the spike continues, escalate to the app/tech team with outage timing and ticket samples.

Honest note: Maths checked: net pending increase from today’s opened/closed is +12, but reported pending rose +14, so 2 tickets are unexplained.

Grade: P / E / F

### USER
P

### GPT
Task 4 of 5: Write an SOP for a process

Dummy input:
Process: Handling “wrong item received”
Policy: Ask for 3 photos: product, invoice, outer package.
If verified, replacement within 48 hours.
Complication: Customer may have discarded packaging; current policy doesn’t say what to do then.

Attempt:
SOP: Wrong Item Received

1. Acknowledge the complaint and apologise.
2. Ask the customer for:
   - Photo of the product received
   - Photo of the invoice
   - Photo of the outer package
3. Check whether the item in the photo differs from the invoice/order.
4. If all three proofs are received and mismatch is clear, mark as “Verified wrong item”.
5. Offer replacement within 48 hours as per policy.
6. If proof is unclear, ask for clearer photos before proceeding.
7. If the customer has discarded the outer package, do not reject immediately. Escalate to supervisor because policy is silent on this case.
8. Update ticket notes with proof received, verification result, and next action.

Honest note: Good draft, but final SOP needs owner name, SLA start point, and exception approval rules.

Grade: P / E / F

### USER
E

### GPT
Task 5 of 5: Find why a process keeps breaking

Dummy input:
Process: Refund status tickets
Last 5 days:
Refund complaints: 38, 41, 44, 52, 57
Payment gateway report sent daily at 6 pm
Support replies promise “update in 24 hrs”
Payments team responds next morning
Complication: Weekend had fewer payment staff.

Attempt:
Likely cause:
Refund complaints are rising because customer expectations and internal response timing do not match. Support promises an update within 24 hours, but the payment gateway report comes at 6 pm and the payments team usually responds only the next morning. This creates delayed updates and repeat contacts.

Contributing factors:
- Complaint volume increased daily: 38 to 57 in 5 days.
- Weekend payment staffing was lower, likely increasing backlog.
- Support may be replying before having confirmed refund status.
- No same-day escalation window after the 6 pm gateway report.

Suggested fixes:
1. Change customer wording to “next working day after gateway confirmation”.
2. Create a 6:30 pm daily refund exception queue.
3. Add weekend backup owner for payment queries.
4. Track repeat contacts separately from new refund complaints.

Honest note: This is a plausible root-cause draft; it needs ticket timestamps and team SLA data to confirm.

Grade: P / E / F

### USER
P

### GPT
```text
RUN #1 | 19 Nov 2026
Role: General analyst / operations
support
Score: 5 of 5 passed (2 with edits)

1. Reply to customer tickets: EDITS
2. Canned response: PASS
3. Daily shift report: PASS
4. SOP for process: EDITS
5. Process-break analysis: PASS

HAND TO AI THIS WEEK: Canned response
Prompt: "Write a short support canned
response for [ISSUE]. Use [POLICY],
mention [LIMIT], and avoid overpromising."
STAYED HUMAN (your edge): SOP for
process - exception judgement needed
INVEST FREED TIME IN: exception
handling in SOPs
2-WEEK EXPERIMENT: Use the canned
response prompt for every common issue;
count uses and minutes saved; spend them
on exception handling in SOPs.
RUN #2: 19 Dec 2026 - paste this
card back to compare
(S) = AI draft, human sign-off |
@[HANDLE]
```

Screenshot it, and copy the text too. You'll need it for your next run.