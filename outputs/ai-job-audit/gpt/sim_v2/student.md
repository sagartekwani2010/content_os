### USER
Start my Run #1

### GPT
We’ll test your real weekly tasks: I attempt them here, you grade each.

Privacy rule: No names, clients, company names or confidential data. I can create dummy data for you.

What’s your role? Students: which job are you aiming for?

### USER
I’m Karan, a final-year BTech student in Hyderabad. I’m aiming for a data analyst job.

### GPT
For a data analyst job, these are the tasks you’ll be handed in year one:

1. Pull data with SQL
2. Clean and join messy Excel or CSV files
3. Make a dashboard or a chart
4. Explain what the numbers mean in a mail
5. Write requirements or user stories
6. Do an ad hoc analysis for a manager’s question
7. Check data for errors before sending
8. Present findings to stakeholders

Pick 3 to 5 you do/expect weekly, or type your own. Then: your own samples or dummy ones? Reply S or D.

### USER
3, 6, 7. D

### GPT
Task 1 of 3: Make a dashboard or a chart

Dummy input:
Weekly food delivery orders, Hyderabad:
Mon 120 orders, ₹36,000 revenue, 8 complaints
Tue 150, ₹45,000, 5 complaints
Wed 90, ₹31,500, complaints missing
Thu 180, ₹54,000, 12 complaints
Fri 210, ₹58,800, 9 complaints
Manager asks: “Show growth and service quality. Use one chart.”

Attempt:
Use a combo chart.

Title: Weekly Orders, Revenue and Complaints

X-axis: Day
Bars: Orders
Line 1: Revenue
Line 2: Complaints

Key callouts:
- Orders rose from 120 on Monday to 210 on Friday.
- Revenue rose from ₹36,000 to ₹58,800.
- Wednesday complaints data is missing, so do not treat it as zero.
- Thursday had the highest complaint count: 12, despite not being the highest order day.
- Friday had the highest orders and revenue, with complaints lower than Thursday.

Suggested insight:
“Demand improved through the week, but service quality needs checking on Thursday. Wednesday complaint data must be confirmed before sharing final weekly quality trend.”

Honest note: I cannot render an actual Excel/Power BI chart here; this is the chart design and insight, with the missing value flagged.

Grade:
P = Pass: I would use this as it is.
E = Pass with edits: usable after quick fixes, still faster than doing it myself.
F = Fail: wrong, risky, or faster to do myself.

### USER
what would you grade it?

### GPT
Honest note: I’d only repeat that I can’t render the chart here, but the design and insight are usable and the missing complaint value is flagged. The grade is yours.

Grade: P / E / F

### USER
E

### GPT
Task 2 of 3: Do an ad hoc analysis for a manager’s question

Dummy input:
Manager asks: “Why did Friday revenue beat Thursday?”
Thu: 180 orders, ₹54,000 revenue, 12 complaints
Fri: 210 orders, ₹58,800 revenue, 9 complaints
Promo: Thu 10% off, Fri no promo
AOV field says Thu ₹300, Fri ₹260, but revenue/orders gives different Fri AOV.

Attempt:
Friday revenue beat Thursday mainly because order volume was higher.

Calculations:
- Thursday AOV = ₹54,000 / 180 = ₹300
- Friday calculated AOV = ₹58,800 / 210 = ₹280
- Revenue increase = ₹58,800 - ₹54,000 = ₹4,800
- Order increase = 210 - 180 = 30 orders
- Complaint count fell from 12 to 9

Interpretation:
Friday had 30 more orders, which offset its lower AOV. The stated Friday AOV of ₹260 does not match revenue/orders, so the AOV field needs validation before final reporting.

Manager-ready answer:
“Friday revenue was higher due to higher order volume, not higher order value. Orders rose from 180 to 210, while calculated AOV fell from ₹300 to ₹280. Please verify the Friday AOV field, since ₹260 conflicts with revenue/orders.”

Honest note: I spotted the conflicting AOV and did not use it as final truth.

Grade: P / E / F

### USER
E

### GPT
Task 3 of 3: Check data for errors before sending

Dummy input:
Customer order export:
Order ID 101, Customer A, 18 Nov 2026, ₹500, Paid
Order ID 102, Customer B, 18/11/26, ₹0, Paid
Order ID 102, Customer C, 19 Nov 2026, ₹750, Failed
Order ID blank, Customer D, 20 Nov 2026, ₹1,200, Paid
Order ID 105, Customer E, 31 Nov 2026, ₹900, Paid

Attempt:
Data quality checks found:

1. Duplicate Order ID
- Order ID 102 appears twice.
- Needs confirmation: duplicate entry or two separate orders?

2. Missing primary key
- Customer D has blank Order ID.
- Cannot reliably track this order until ID is added.

3. Invalid date
- 31 Nov 2026 is not a valid date.
- November has 30 days.

4. Inconsistent date format
- “18/11/26” differs from “18 Nov 2026”.
- Standardise date format before analysis.

5. Suspicious amount/status combination
- Order 102 for Customer B has ₹0 but status Paid.
- Could be coupon/free order, refund, or data error; needs validation.

Recommended action before sending:
Hold the file and ask source team to fix duplicate ID, blank ID, invalid date, and confirm the ₹0 paid order.

Honest note: I flagged likely issues but cannot verify business rules, like whether ₹0 paid orders are allowed.

Grade: P / E / F

### USER
P

### GPT
```text
RUN #1 | 19 Nov 2026
Role: final-year BTech student,
Hyderabad; aiming data analyst
Score: 3 of 3 passed (2 with edits)

1. Dashboard/chart: EDITS
2. Ad hoc analysis: EDITS
3. Data error check: PASS

HAND TO AI THIS WEEK: Data error
check
Prompt: "Check this [DATA] before
sending. Flag duplicates, missing IDs,
invalid dates, inconsistent formats and
suspicious values. Give fixes."
STAYED HUMAN (your edge):
Dashboard/chart - visual judgement
INVEST FREED TIME IN: Data
visualisation storytelling
2-WEEK EXPERIMENT: Use the prompt on
5 datasets; count errors found and
minutes saved.
RUN #2: 19 Dec 2026 - paste this
card back to compare
(S) = AI draft, human sign-off |
@[HANDLE]
```

Screenshot it, and copy the text too. You'll need it for your next run.

### USER
Thanks. DONE

### GPT
Nice. See you for Run #2.