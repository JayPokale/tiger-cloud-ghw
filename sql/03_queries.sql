SELECT view_name, materialized_only FROM timescaledb_information.continuous_aggregates;
SELECT j.job_id, j.application_name, j.schedule_interval FROM timescaledb_information.jobs j WHERE j.proc_name = 'policy_refresh_continuous_aggregate';
EXPLAIN (ANALYZE, COSTS OFF, SUMMARY ON) SELECT time_bucket('1 hour', time) AS bucket, location, avg(temperature), min(temperature), max(temperature), avg(humidity) FROM conditions GROUP BY 1, 2;
EXPLAIN (ANALYZE, COSTS OFF, SUMMARY ON) SELECT * FROM conditions_hourly;
SELECT bucket, location, round(avg_temp::numeric,2) AS avg_temp, round(min_temp::numeric,2) AS min_temp, round(max_temp::numeric,2) AS max_temp, readings FROM conditions_hourly ORDER BY bucket DESC, location LIMIT 6;
