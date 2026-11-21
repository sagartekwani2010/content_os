### USER
hi, I'm a pharmacist

### GPT
Great. We’ll test your real weekly tasks: I attempt them, you grade them.

Privacy rule: No names, clients, company names or confidential data. I can create dummy data for you.

For pharmacist, I’ll use likely tasks. Pick 3 to 5 you do weekly:

1. Check prescription for dose/interactions (sign-off)
2. Explain medicine usage to a patient
3. Handle a patient complaint
4. Make inventory reorder list
5. Substitute unavailable medicine safely (sign-off)
6. Write counselling notes
7. Prepare daily sales/stock summary
8. Flag expired/near-expiry stock

### USER
3, 4, 8

### GPT
Confirmed: we’ll test 3 tasks — complaint reply, inventory reorder list, and near-expiry stock flagging.

Your own samples or dummy ones? Reply S or D.

### USER
D

### GPT
Task 1 of 3: Handle a patient complaint

Dummy input:
Customer B says: “I bought cough syrup yesterday. The seal looked loose after I reached home, so I didn’t use it. Bill is missing, but payment was by UPI around 8:15 pm. Staff told me no exchange without bill. I’m angry.”

Attempt:
Sorry for the inconvenience. Please do not use the syrup if the seal looks loose.

We can check yesterday’s UPI payment around 8:15 pm and match it with our sales record. Please bring the bottle, outer pack, and any UPI payment screenshot. Once verified, we will inspect the product and help with a replacement or refund as per store policy.

I also apologise if the earlier response felt unhelpful. Medicine packaging concerns must be handled carefully. I’ll brief the staff to escalate such cases instead of giving a flat “no bill, no exchange” answer.

Honest note: I did not promise refund without verification; complaint handling may still need store policy alignment.

Grade:
P = Pass: I would use this as it is.
E = Pass with edits: usable after quick fixes, still faster than doing it myself.
F = Fail: wrong, risky, or faster to do myself.

### USER
E

### GPT
Task 2 of 3: Make inventory reorder list

Dummy input:
Current stock:
Paracetamol 500mg: 18 strips, avg weekly sale 35, lead time 3 days
Cetirizine 10mg: 9 strips, avg weekly sale 12, lead time 2 days
ORS sachets: 22 pcs, avg weekly sale 40, lead time 5 days
Insulin pen needles: 6 boxes, avg weekly sale 4, lead time 10 days
Supplier says minimum order: 20 units per SKU.

Attempt:
Reorder list:

1. ORS sachets
Order: 40 pcs
Reason: stock 22, weekly sale 40, lead time 5 days. High risk of stockout before next cycle.

2. Paracetamol 500mg
Order: 40 strips
Reason: stock 18, weekly sale 35, lead time 3 days. Current stock is below one week’s sale.

3. Cetirizine 10mg
Order: 20 strips
Reason: stock 9, weekly sale 12, but supplier minimum is 20.

Do not reorder now:
Insulin pen needles
Reason: stock 6 boxes, weekly sale 4. Lead time is longer, but current stock covers around 1.5 weeks. Review again in 3–4 days.

Honest note: I assumed reorder quantities should roughly cover one week and respect supplier minimum; no target safety stock was provided.

Grade: P / E / F

### USER
E

### GPT
Task 3 of 3: Flag expired/near-expiry stock

Dummy input:
Stock check on 19 Nov 2026:
Amoxicillin 500mg: 12 strips, expiry Dec 2026
Vitamin D3 sachets: 30 pcs, expiry Mar 2027
Eye drops: 5 bottles, expiry Nov 2026
Cough syrup: 8 bottles, expiry missing on 2 bottles
Cold-chain insulin: 3 pens, expiry Jan 2027

Attempt:
Expiry action list:

Immediate quarantine:
1. Eye drops — 5 bottles
Expiry Nov 2026. Since only month is given and current date is 19 Nov, do not sell unless exact expiry date is confirmed and valid.

2. Cough syrup — 2 bottles
Expiry missing. Keep aside and verify batch/expiry from invoice, outer carton, or supplier.

Near-expiry priority:
3. Amoxicillin 500mg — 12 strips
Expiry Dec 2026. Mark as near-expiry and sell only if full course can be completed before expiry.

4. Cold-chain insulin — 3 pens
Expiry Jan 2027. Keep cold-chain records checked; flag for priority dispensing if compliant.

Monitor:
5. Vitamin D3 sachets — 30 pcs
Expiry Mar 2027. Review in next monthly check.

Honest note: Exact policy depends on store SOP; I treated missing/unclear expiry as not saleable until verified.

Grade: P / E / F

### USER
P

### GPT
```text
RUN #1 | 19 Nov 2026
Role: pharmacist
Score: 3 of 3 passed (2 with edits)

1. Handle patient complaint: EDITS
2. Make inventory reorder list: EDITS
3. Flag near-expiry stock: PASS

HAND TO AI THIS WEEK: Flag near-expiry
stock
Prompt: "Flag expired or near-expiry
items from [STOCK LIST] as quarantine,
priority, or monitor with reasons."
STAYED HUMAN (your edge): Handle
patient complaint - policy judgement and
tone
INVEST FREED TIME IN: complaint
de-escalation
2-WEEK EXPERIMENT: Use the expiry
prompt for each stock check; count uses
and minutes saved; practise complaint
phrasing.
RUN #2: 19 Dec 2026 - paste this
card back to compare
(S) = AI draft, human sign-off |
@[HANDLE]
```

Screenshot it, and copy the text too. You'll need it for your next run.

### USER
Thanks — DONE

### GPT
Done. See you for Run #2.