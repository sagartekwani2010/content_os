### USER
Start my Run #1

### GPT
We’ll test your real weekly tasks: I attempt them here, you grade the output.

Privacy rule: No names, clients, company names or confidential data. I can create dummy data for you.

What’s your role? Students: which job are you aiming for?

### USER
I’m Karan, final-year BTech student in Hyderabad, aiming for data analyst.

### GPT
For a data analyst target, these are the tasks you’ll likely be handed in year one:

1. Pull data with SQL
2. Clean and join messy Excel or CSV files
3. Make a dashboard or a chart
4. Explain what the numbers mean in a mail
5. Write requirements or user stories
6. Do an ad hoc analysis for a manager’s question
7. Check data for errors before sending
8. Present findings to stakeholders

Pick 3 to 5 you do every week, or want to test. Reply like: 1, 4, 6.

### USER
1, 2, 6

### GPT
Confirmed: we’ll test 3 data analyst tasks — SQL, messy data cleaning/joining, and ad hoc analysis.

Task 1 of 3: Pull data with SQL

Paste a small sanitised sample plus the question, or reply D and I’ll make a realistic dummy one.

### USER
D

### GPT
Dummy input:

Tables: orders(order_id, customer_id, order_date, city, amount, status)
customers(customer_id, signup_date, segment)
Question: For Oct 2026, show city-wise completed orders, unique customers, revenue.
Only include cities with revenue above ₹1,00,000.

```sql
SELECT
  o.city,
  COUNT(DISTINCT o.order_id) AS completed_orders,
  COUNT(DISTINCT o.customer_id) AS unique_customers,
  SUM(o.amount) AS revenue
FROM orders o
JOIN customers c
  ON o.customer_id = c.customer_id
WHERE o.status = 'Completed'
  AND o.order_date >= DATE '2026-10-01'
  AND o.order_date < DATE '2026-11-01'
GROUP BY o.city
HAVING SUM(o.amount) > 100000
ORDER BY revenue DESC;
```

Grade this:
P = Pass
E = Pass with edits
F = Fail

### USER
P

Will AI take data analyst jobs?

### GPT
I can’t predict that, and nobody honestly can. I can show what AI did with your tasks today. A count beats a guess.

Task 2 of 3: Clean and join messy Excel or CSV files

Paste a small sanitised sample, or reply D and I’ll make a realistic dummy one.

### USER
D

### GPT
Dummy input:

sales.csv: Order ID `O-101`, Customer `c001`, Amount `₹12,500`, Date `01/10/26`
sales.csv: Order ID `O-102`, Customer ` C002 `, Amount `9,800`, Date `2-Oct-2026`
customers.csv: Customer ID `C001`, City `Hyderabad`, Segment `Student`
customers.csv: Customer ID `C002`, City `Pune`, Segment `Working`

Cleaned + joined output:

```csv
order_id,customer_id,order_date,amount,city,segment
O-101,C001,2026-10-01,12500,Hyderabad,Student
O-102,C002,2026-10-02,9800,Pune,Working
```

Excel formulas used:

```excel
Clean Customer ID:
=UPPER(TRIM(B2))

Clean Amount:
=VALUE(SUBSTITUTE(SUBSTITUTE(D2,"₹",""),",",""))

Join City:
=XLOOKUP(C2,customers!A:A,customers!B:B,"Not found")

Join Segment:
=XLOOKUP(C2,customers!A:A,customers!C:C,"Not found")
```

Honest note: I can clean the logic and output here, but I can’t open or validate an actual Excel file in chat.

Grade this:
P = Pass
E = Pass with edits
F = Fail

### USER
P

### GPT
Task 3 of 3: Do an ad hoc analysis for a manager’s question

Paste a small sanitised sample plus the question, or reply D and I’ll make a realistic dummy one.

### USER
D

### GPT
Dummy input:

Manager asks: “Why did app revenue drop in Oct?”
Sep revenue: ₹18.4L, Oct revenue: ₹15.2L
New users: Sep 12,000, Oct 13,500
Conversion: Sep 4.8%, Oct 3.6%
Avg order value: Sep ₹3,194, Oct ₹3,128

Analysis:

Revenue fell by ₹3.2L, mainly because conversion dropped from 4.8% to 3.6%.

Quick bridge:
Sep expected orders = 12,000 × 4.8% = 576
Oct orders = 13,500 × 3.6% = 486
Order drop = 90 fewer orders

Even though new users increased by 1,500, fewer users converted. AOV also dipped slightly from ₹3,194 to ₹3,128, but that is a smaller driver.

Manager-ready summary:

“Oct revenue dropped by ₹3.2L vs Sep. The main reason is lower conversion, not traffic. New users grew 12.5%, but conversion fell from 4.8% to 3.6%, leading to about 90 fewer orders. AOV reduced slightly, adding minor pressure. Next check: conversion by channel, landing page, payment failures, and campaign quality.”

Grade this:
P = Pass
E = Pass with edits
F = Fail

### USER
P

Thanks

### GPT
```text
RUN #1 | 19 Nov 2026
Role: Final-year BTech student aiming for data analyst
Score: 3 of 3 tasks passed (0 with edits)

1. Pull data with SQL: PASS
2. Clean and join messy Excel or CSV files: PASS
3. Do an ad hoc analysis for a manager's question: PASS

HAND TO AI THIS WEEK: Pull data with SQL
Prompt: "Write SQL for [question]. Tables: [table names and columns]. Filters: [date/status/segment]. Output fields: [fields]. Include grouping, joins and ordering."
STAYED HUMAN (your edge): None this run. Pick harder tasks for Run #2.
INVEST FREED TIME IN: checking AI output
2-WEEK EXPERIMENT: Use the SQL prompt 5 times; count fixes needed and minutes saved; spend them checking edge cases.
RUN #2: 19 Dec 2026 - paste this card back here to compare
(S) = AI draft, human sign-off | @[HANDLE]
```

Screenshot it, and copy the text too. You'll need it for Run #2.

### USER
Thanks

DONE

### GPT
Done. See you for Run #2 — paste the card back when you’re ready.