# Local validation

Validated October 21, 2026 using Python 3.12.14 on Windows.

Command: `python -m unittest discover -s tests -v`

Result: **15 tests passed**. Includes distinct-account counting, source/account isolation, inclusive and exclusive time boundaries, prevention of duplicate access counts, schema constraints, parameter binding, timestamp conversion, timeline preservation, independently specified fixture results, and CLI success/error behavior.

Expected results were specified separately from the SQL implementation. The demo contains one qualifying spray anchor, two qualifying successful logins, one aggregate with two access records totaling 12,000,000 bytes, and a 12-record account timeline.

GitHub CI has not run for this project because it has not been published. Linux and Python 3.10 compatibility are targeted, not yet verified. These tests establish behavior on synthetic fixtures, not real-world detection performance.
