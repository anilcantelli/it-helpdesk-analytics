USE it_helpdesk_analytics;

SELECT issue_type, COUNT(*) AS ticket_count
FROM tickets
GROUP BY issue_type
ORDER BY ticket_count DESC;

SELECT priority, issue_type,
       ROUND(AVG(resolution_time_hours), 1) AS avg_resolution_hours
FROM tickets
WHERE is_closed = TRUE
GROUP BY priority, issue_type
ORDER BY avg_resolution_hours DESC
LIMIT 15;

SELECT sla_plan,
       COUNT(*) AS total_closed,
       SUM(CASE
               WHEN sla_plan = 'standard' AND resolution_time_hours > 48 THEN 1
               WHEN sla_plan = 'gold' AND resolution_time_hours > 24 THEN 1
               WHEN sla_plan = 'platinum' AND resolution_time_hours > 8 THEN 1
               ELSE 0
           END) AS breached_count,
       ROUND(
         SUM(CASE
               WHEN sla_plan = 'standard' AND resolution_time_hours > 48 THEN 1
               WHEN sla_plan = 'gold' AND resolution_time_hours > 24 THEN 1
               WHEN sla_plan = 'platinum' AND resolution_time_hours > 8 THEN 1
               ELSE 0
           END) / COUNT(*) * 100, 1) AS breach_rate_pct
FROM tickets
WHERE is_closed = TRUE
GROUP BY sla_plan
ORDER BY breach_rate_pct DESC;

SELECT issue_type,
       ROUND(AVG(csat_score), 2) AS avg_csat,
       SUM(CASE WHEN customer_sentiment = 'very_negative' THEN 1 ELSE 0 END) AS very_negative_count,
       COUNT(*) AS rated_ticket_count
FROM tickets
WHERE is_rated = TRUE
GROUP BY issue_type
ORDER BY avg_csat ASC;

SELECT channel,
       SUM(reopened) AS reopened_count,
       COUNT(*) AS total_count,
       ROUND(SUM(reopened) / COUNT(*) * 100, 1) AS reopen_rate_pct
FROM tickets
GROUP BY channel
ORDER BY reopen_rate_pct DESC;
