-- Challenge: Set up a Tiger Cloud service and create your first hypertable
-- Based on https://www.tigerdata.com/docs/build/how-to/your-first-hypertable
CREATE TABLE IF NOT EXISTS conditions (
   time        TIMESTAMPTZ       NOT NULL,
   location    TEXT              NOT NULL,
   device      TEXT              NOT NULL,
   temperature DOUBLE PRECISION  NULL,
   humidity    DOUBLE PRECISION  NULL
) WITH (
   tsdb.hypertable,
   tsdb.segmentby = 'device',
   tsdb.orderby = 'time DESC'
);

INSERT INTO conditions (time, location, device, temperature, humidity)
VALUES
   (NOW() - INTERVAL '2 hours', 'office', 'sensor-1', 22.1, 45.0),
   (NOW() - INTERVAL '1 hour',  'office', 'sensor-1', 22.3, 44.8),
   (NOW(),                      'office', 'sensor-1', 22.2, 45.1);

-- Two weeks of readings every minute for three rooms, so the table spans several chunks
INSERT INTO conditions (time, location, device, temperature, humidity)
SELECT t, loc, 'sensor-' || loc,
       20 + 4 * sin(extract(epoch FROM t) / 43200 * pi()) + random(),
       45 + 10 * cos(extract(epoch FROM t) / 86400 * pi()) + random() * 2
FROM generate_series(NOW() - INTERVAL '14 days', NOW() - INTERVAL '3 hours', INTERVAL '1 minute') AS t,
     unnest(ARRAY['office', 'lab', 'server-room']) AS loc;
