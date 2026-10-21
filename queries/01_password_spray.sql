-- One row per failure anchor reaching the distinct-account threshold.
-- Inclusive trailing window; repeated anchors intentionally remain visible.
SELECT a.event_id AS anchor_event_id,
       datetime(a.event_time, 'unixepoch') AS observed_utc,
       a.src_ip,
       COUNT(*) AS failure_count,
       COUNT(DISTINCT b.user_id) AS distinct_users
FROM auth_events AS a
JOIN auth_events AS b
  ON b.src_ip = a.src_ip
 AND b.outcome = 'failure'
 AND b.event_time BETWEEN a.event_time - :window_seconds AND a.event_time
WHERE a.outcome = 'failure'
GROUP BY a.event_id, a.event_time, a.src_ip
HAVING COUNT(DISTINCT b.user_id) >= :min_users
ORDER BY a.event_time, a.event_id;
