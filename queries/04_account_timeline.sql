-- UNION ALL preserves events across the two source tables.
SELECT event_time, datetime(event_time, 'unixepoch') AS event_utc,
       'authentication' AS source, event_id AS record_id,
       src_ip, outcome AS detail, NULL AS bytes_sent
FROM auth_events WHERE user_id = :user_id
UNION ALL
SELECT event_time, datetime(event_time, 'unixepoch'),
       'resource_access', access_id, src_ip, resource, bytes_sent
FROM access_events WHERE user_id = :user_id
ORDER BY event_time, source, record_id;
