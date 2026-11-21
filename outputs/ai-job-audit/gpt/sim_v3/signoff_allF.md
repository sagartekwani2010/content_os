### USER
I'm a chartered accountant

### GPT
Great. We’ll test your real weekly tasks: I attempt them, you grade them.

Privacy rule: No names, clients, company names or confidential data. I can create dummy data for you.

Your role: chartered accountant. Here are 8 likely weekly tasks:

1. Reconcile ledger with bank statement
2. Prepare GST working from invoices
3. Draft a reply to a tax notice (sign-off)
4. Prepare and file a tax return (sign-off)
5. Draft audit observations and the audit opinion (sign-off)
6. Do TDS calculation working
7. Make the month-end MIS for the client
8. Write a mail asking the client for pending documents

Pick 3 to 5 you do every week, or type your own. Then S (own samples) or D (dummy). Reply like: 1, 4, 6 D

### USER
2, 3, 5 D

### GPT
Confirmed: 2 Prepare GST working, 3 tax notice reply (sign-off), 5 audit observations/opinion (sign-off). We’ll use dummy data.

Task 1 of 3: Prepare GST working from invoices

Dummy input:
Apr 2026 sales invoices:
Taxable outward: ₹8,50,000 @18%
Export service: ₹2,00,000, LUT mentioned
Credit note: ₹50,000 + GST, original invoice March 2026
Purchase ITC: CGST ₹42,000, SGST ₹42,000, IGST ₹18,000
One vendor invoice dated 31 Mar received in Apr: ITC ₹12,000 IGST

Attempt:
GST working for Apr 2026

Outward tax:
Domestic taxable sales: ₹8,50,000
GST @18%: ₹1,53,000
Assumed split: CGST ₹76,500, SGST ₹76,500

Export under LUT:
Taxable value ₹2,00,000
GST payable: Nil

Credit note:
₹50,000 + GST relates to March invoice.
GST impact: ₹9,000 reduction, but month of adjustment needs confirmation from credit note date and GSTR-1 treatment.

Input tax credit:
CGST ₹42,000
SGST ₹42,000
IGST ₹18,000
March vendor invoice received in Apr: IGST ₹12,000, claim in Apr if eligible and reflected as per records.

Net payable before credit note:
CGST: ₹76,500 - ₹42,000 = ₹34,500
SGST: ₹76,500 - ₹42,000 = ₹34,500
IGST: Nil payable; IGST ITC ₹30,000 available for set-off/carry forward.

Honest note: Credit note date, POS/intra-state assumption, vendor eligibility, 2B match, and exact ITC utilisation order are not confirmed.

Grade this task:
P = Pass: I would use this as it is.
E = Pass with edits: usable after quick fixes, still faster than doing it myself.
F = Fail: wrong, risky, or faster to do myself.

### USER
F

### GPT
Task 2 of 3: Draft a reply to a tax notice

Dummy input:
Notice u/s GST: mismatch between GSTR-1 and GSTR-3B for FY 2024-25
Difference: outward taxable value higher in GSTR-1 by ₹3,20,000; tax difference ₹57,600
Reason in books: April invoice duplicated in GSTR-1, corrected by credit note in June
Notice asks reply within 7 days; no ARN provided

Attempt:
Subject: Reply to notice regarding GSTR-1 and GSTR-3B mismatch for FY 2024-25

Respected Sir/Madam,

With reference to the notice regarding difference between outward supplies reported in GSTR-1 and GSTR-3B for FY 2024-25, we submit that the difference of taxable value ₹3,20,000 and tax ₹57,600 arose due to duplicate reporting of one April invoice in GSTR-1.

The said duplicate entry was subsequently corrected through a credit note reported in June. Therefore, there is no short payment of tax in GSTR-3B.

We request you to kindly consider the reconciliation and drop the proceedings.

Documents to attach:
1. GSTR-1 extract for April
2. GSTR-3B extract for April
3. Credit note details reported in June
4. Ledger reconciliation

Honest note: Notice section, GSTIN, ARN/reference, dates, invoice and credit note numbers, portal category, and whether credit note legally cures the mismatch are not verified.

Sign-off task: this is an AI draft. A qualified human checks and signs.

Grade: P / E / F

### USER
F

### GPT
Task 3 of 3: Draft audit observations and the audit opinion

Dummy input:
Statutory audit draft notes:
Revenue ₹12 crore, inventory ₹1.8 crore
Physical verification done by management, auditor not present
Trade receivables ₹2.4 crore; confirmations received for only ₹80 lakh
One related party loan ₹35 lakh, agreement not available
Management says all balances are recoverable

Attempt:
Audit observations:
1. Inventory verification was conducted by management; auditor was not present. Alternative procedures and verification records should be reviewed before concluding.
2. Trade receivable confirmations were received for ₹80 lakh out of ₹2.4 crore. For the balance, subsequent receipts, ageing, disputes and supporting invoices should be checked.
3. Related party loan of ₹35 lakh lacks an agreement. Terms, approval, interest, repayment schedule and compliance with applicable law require verification.
4. Management’s assertion that all receivables are recoverable is unsupported unless backed by ageing, collections and customer correspondence.

Draft opinion wording:
Subject to satisfactory completion of alternative procedures for inventory, receivable recoverability testing, and verification of related party loan documentation, the audit opinion may need modification if sufficient appropriate audit evidence is not obtained.

Honest note: Applicable GAAP, audit standard, company type, materiality, CARO, Schedule III, Companies Act compliance, and final opinion type are not determined.

Sign-off task: this is an AI draft. A qualified human checks and signs.

Grade: P / E / F

### USER
F

### GPT
```text
RUN #1 | 18 Nov 2026
Role: chartered accountant
Score: 0 of 3 passed (0 with edits)

1. GST working: FAIL
2. Tax notice reply: FAIL (S)
3. Audit observations/opinion: FAIL (S)

HAND TO AI THIS WEEK: None this run.
That is a real result.
STAYED HUMAN (your edge): GST
working - ITC and mismatch judgement
INVEST FREED TIME IN: GST
reconciliation review
2-WEEK EXPERIMENT: Do 3 GST
workings; compare AI draft with
final and note errors.
RUN #2: 18 Dec 2026 - paste this
card back to compare
(S) = AI draft, human sign-off
@[HANDLE]
```

Screenshot it, and copy the text too. You'll need it for your next run.

### USER
thanks

### GPT
You’re welcome — that was a real result, not a sales pitch.