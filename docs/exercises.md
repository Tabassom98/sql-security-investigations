# Practice and explain the work

1. Run the lab and trace `login-1` to its five preceding failures. Explain the inclusive lower time boundary.
2. Explain why the repeated failures for `svc-backup` are not password spraying under Query 01.
3. Replace EXISTS with a naive join in a scratch query. Observe how overlapping successful logins inflate the access count, then explain the fix.
4. Add a case where two resources are accessed. Write expectations showing that their byte totals remain separate.
5. Create a query for service accounts with repeated failures, add positive and negative tests, and document benign explanations.
6. Record your own dated investigation notes and what you changed. Be ready to explain your investigation and implementation choices.

Possible interview discussion: Why SQLite? What does GROUP BY change? Why COUNT(DISTINCT user_id)? What does a successful login fail to tell us? How would shared VPN addresses affect interpretation? What evidence would establish session linkage?
