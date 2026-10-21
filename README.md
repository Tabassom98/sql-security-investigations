# SQL Security Investigations

A small, reproducible investigation lab built with SQL, SQLite, and Python. Follow a simulated authentication case from suspicious login activity to resource access, then explain what the evidence supports and what it leaves unanswered.

This portfolio project uses entirely synthetic records. It is designed for learning and review; no real incident, production deployment, or detection accuracy is claimed.

## Run it

Requires Python 3.10+; uses only the standard library. From this repository's directory:

```sh
python lab.py
python -m unittest discover -s tests -v
```

Use `python3` if that is your system's Python command. No packages, accounts, database server, network access, or administrator permissions are needed. Each run creates a fresh in-memory database, loads the fixture, prints JSON, and closes the database. It does not create or overwrite database files. Exit code 0 means success; 2 means a handled input or database error.

```sh
python lab.py --user erin --min-bytes 20000000
```

`--user` changes only the account timeline; other queries still analyze the whole fixture. `--min-bytes` changes the resource-access aggregate threshold. All numeric query parameters can also be supplied through the Python `run_query` API.

## Investigation questions

| SQL file | Question | Techniques |
| --- | --- | --- |
| `01_password_spray.sql` | Did one source fail against at least four distinct accounts in five minutes? | Self join, distinct counts, GROUP BY, HAVING |
| `02_success_after_failures.sql` | Did an account log in successfully after at least five failures from the same source? | User metadata join, time correlation |
| `03_access_after_flagged_login.sql` | Did the same account/source access at least 10 MB of one resource within ten minutes of a flagged login? | CTE, EXISTS, aggregation without duplicate inflation |
| `04_account_timeline.sql` | What happened to one account across both data sources? | UNION ALL, parameter binding, chronological ordering |

The fixture produces one password-spray anchor, two flagged successful logins, and one resource summary totaling **12,000,000 bytes across two access events**. The default account timeline contains 12 records. Compare the full output to [expected results](examples/expected-results.json).

## Read the case

Start with [the investigation report](docs/investigation.md). [Query semantics](docs/query-design.md) explains time boundaries, repeated anchors, source matching, and why a naive join could double-count access events. [Practice exercises](docs/exercises.md) helps you extend and explain the work yourself.

## Data and limitations

The fixture contains invented users and documentation-range IP addresses. Timestamps become integer Unix seconds in UTC. The schema enforces unique record IDs, known accounts, valid outcomes, and nonnegative integer byte counts. IP strings are fixture values; there is no IP normalization or real-log ingestion adapter. Raw schema timestamps are integer seconds; the fixture loader rejects timezone-free or fractional timestamps.

These queries identify patterns worth reviewing. Shared networks, stale credentials, and legitimate exports can look suspicious. The access query correlates by account and IP, not a session identifier; it does not establish that a particular login caused a download. Byte counts are synthetic application telemetry and do not prove data exfiltration. Distributed or slow attacks may be missed. No DNS analysis, automated response, live monitoring, or production-scale benchmark is implemented.

The password-spray query emits matching anchors, not deduplicated incidents. Simultaneous failures are included in its window. The success query excludes equal-time failures because their order is unknown. Usernames and IP strings compare exactly. Use this only as a small offline lab until source-specific normalization and operational controls exist.

## Project layout

`schema.sql` defines tables and indexes; `data/scenario.json` supplies the scenario; `queries/` contains readable SQL; `lab.py` runs the lab; `tests/` checks behavior and edge cases. The proposed GitHub workflow runs the suite on Windows and Linux with Python 3.10 and 3.12. A remote CI result is only verified after publication.

## Provenance

The project includes synthetic evidence and reproducible tests. Future contributions should describe the actual work performed and retain tests and evidence for conclusions.

MIT licensed. See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).
