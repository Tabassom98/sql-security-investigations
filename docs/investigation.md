# Investigation report: simulated authentication and resource access

## Question and scope

Does the synthetic telemetry contain a pattern consistent with password guessing followed by unusual access? All names, addresses, paths, and activity are invented. This is a worked investigation example, not a report of a real breach.

## Observations

1. At 09:00-09:03 UTC on January 15, 2026, source `192.0.2.50` fails against four different accounts. Query 01 returns `spray-4` as the threshold-crossing anchor.
2. At 10:00:30-10:04:30 UTC, `alex` receives five failed logins from `198.51.100.25`. Successful events `login-1` and `login-2` follow at 10:05:00 and 10:05:30. Both match Query 02.
3. Events `access-1` and `access-2`, at 10:06 and 10:07, record access to `/finance/export.csv` from the same account/source. Their byte counts sum to 12,000,000. Query 03 counts each event once even though both preceding successes qualify.
4. A 90,000,000-byte event from another source and another at 10:20 are excluded by source and time scope. They remain in the timeline and should not be dismissed solely because Query 03 excludes them.
5. A separate account's single failure and success do not meet the repeated-failure threshold. A service account's five failures without a success do not match Query 02 or the distinct-user spray threshold; other rules could still consider them relevant.

## Assessment

The records support hypotheses of password spraying and account guessing followed by access. They do not prove malicious intent or compromise. The earlier spray and later guessing use different IPs; this fixture contains no evidence linking those sources to the same actor.

## Next evidence to request in a real investigation

MFA outcomes, identity-provider session IDs, device context, the user's explanation, service ownership, export authorization, and file sensitivity. Verify whether byte counts represent completed downloads, responses, or attempted transfers. Follow the organization's escalation process after evaluating that context.

## Reproduce

Run `python lab.py`, inspect each query's result, and match record IDs to `data/scenario.json`. Run the tests to check boundary cases and duplicate prevention. The default `alex` timeline contains 12 records from both authentication and access tables.
