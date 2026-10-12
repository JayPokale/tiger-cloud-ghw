SELECT * FROM conditions ORDER BY time DESC LIMIT 5;
SELECT hypertable_name, num_chunks, num_dimensions FROM timescaledb_information.hypertables;
SELECT count(*) AS rows, min(time), max(time) FROM conditions;
SELECT chunk_name, range_start, range_end FROM timescaledb_information.chunks WHERE hypertable_name = 'conditions' ORDER BY range_start;
EXPLAIN (ANALYZE, COSTS OFF, TIMING OFF, SUMMARY OFF) SELECT avg(temperature) FROM conditions WHERE time > NOW() - INTERVAL '1 day';
