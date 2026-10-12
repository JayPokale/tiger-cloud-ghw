-- Challenge: Accelerate dashboards with continuous aggregates
-- Hourly per-room dashboard metrics over the two weeks of conditions data
CREATE MATERIALIZED VIEW IF NOT EXISTS conditions_hourly
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 hour', time) AS bucket,
       location,
       avg(temperature) AS avg_temp,
       min(temperature) AS min_temp,
       max(temperature) AS max_temp,
       avg(humidity)    AS avg_humidity,
       count(*)         AS readings
FROM conditions
GROUP BY bucket, location
WITH NO DATA;

CALL refresh_continuous_aggregate('conditions_hourly', NULL, NULL);

SELECT add_continuous_aggregate_policy('conditions_hourly',
  start_offset => INTERVAL '3 days',
  end_offset   => INTERVAL '1 hour',
  schedule_interval => INTERVAL '30 minutes',
  if_not_exists => true);

-- 1-minute OHLCV candlesticks over the live crypto ticks (see ingest_crypto.py)
CREATE MATERIALIZED VIEW IF NOT EXISTS crypto_candles_1m
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 minute', time) AS bucket,
       symbol,
       first(price, time) AS open,
       max(price)         AS high,
       min(price)         AS low,
       last(price, time)  AS close,
       last(day_volume, time) AS day_volume,
       count(*)           AS ticks
FROM crypto_ticks
GROUP BY bucket, symbol
WITH NO DATA;

SELECT add_continuous_aggregate_policy('crypto_candles_1m',
  start_offset => INTERVAL '1 hour',
  end_offset   => INTERVAL '1 minute',
  schedule_interval => INTERVAL '1 minute',
  if_not_exists => true);
