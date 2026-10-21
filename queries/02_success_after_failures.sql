-- A success is the anchor. Strictly earlier failures only.
SELECT s.event_id AS success_event_id,
       datetime(s.event_time, 'unixepoch') AS success_utc,
       s.user_id, u.department, s.src_ip,
       COUNT(f.event_id) AS preceding_failures
FROM auth_events AS s
JOIN users AS u ON u.user_id = s.user_id
JOIN auth_events AS f
  ON f.user_id = s.user_id AND f.src_ip = s.src_ip
 AND f.outcome = 'failure'
 AND f.event_time >= s.event_time - :window_seconds
 AND f.event_time < s.event_time
WHERE s.outcome = 'success'
GROUP BY s.event_id, s.event_time, s.user_id, u.department, s.src_ip
HAVING COUNT(f.event_id) >= :min_failures
ORDER BY s.event_time, s.event_id;
