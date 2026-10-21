# Query design and assumptions

The trailing failure window is 300 seconds, inclusive at its lower bound. Query 01 includes events at the anchor timestamp, including simultaneous failures, and emits each qualifying failure anchor. Query 02 counts only failures strictly before the successful event. No event-ID ordering is used to infer real-world ordering at equal timestamps.

Query 03 considers access strictly after a flagged success and at most 600 seconds later. It sums per account, source IP, and resource across qualifying accesses. Several qualifying logins may extend the union of access windows; the aggregate is not a per-session total. The 10,000,000-byte threshold is decimal MB, not MiB.

Using EXISTS matters: joining every access event to every preceding flagged login would count the same access multiple times. The fixture deliberately includes two qualifying successes before the two accesses. Tests require the result to stay at two events and 12,000,000 bytes.

Values are bound as SQL parameters. Query names are selected from a local allowlist rather than interpolated into SQL or accepted as arbitrary file paths. This does not make the program a sandbox for untrusted SQL; the bundled SQL files are trusted local source code.

UNION ALL preserves source events even if their IDs match across tables. Timeline sorting breaks equal-time ties by source and record ID only for deterministic display. Indexes support pair/time lookup; no performance claim is made, and the correlated queries need benchmarking and query-plan review for larger datasets.

The database has no session IDs, MFA events, tenant identity, host fields, or authoritative IP ownership. Successive runs do not persist state or deduplicate incidents. All conclusions depend on the modeled input semantics.
