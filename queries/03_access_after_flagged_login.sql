-- Aggregate each access event once, even if multiple flagged logins precede it.
WITH flagged_logins AS (
    SELECT s.event_id, s.event_time, s.user_id, s.src_ip
    FROM auth_events AS s
    JOIN auth_events AS f
      ON f.user_id = s.user_id AND f.src_ip = s.src_ip
     AND f.outcome = 'failure'
     AND f.event_time >= s.event_time - :window_seconds
     AND f.event_time < s.event_time
    WHERE s.outcome = 'success'
    GROUP BY s.event_id, s.event_time, s.user_id, s.src_ip
    HAVING COUNT(f.event_id) >= :min_failures
)
SELECT a.user_id, a.src_ip, a.resource,
       COUNT(*) AS access_count,
       SUM(a.bytes_sent) AS total_bytes,
       datetime(MIN(a.event_time), 'unixepoch') AS first_access_utc,
       datetime(MAX(a.event_time), 'unixepoch') AS last_access_utc
FROM access_events AS a
WHERE EXISTS (
    SELECT 1 FROM flagged_logins AS s
    WHERE s.user_id = a.user_id AND s.src_ip = a.src_ip
      AND a.event_time > s.event_time
      AND a.event_time <= s.event_time + :followup_seconds
)
GROUP BY a.user_id, a.src_ip, a.resource
HAVING SUM(a.bytes_sent) >= :min_bytes
ORDER BY total_bytes DESC, a.user_id, a.src_ip, a.resource;
