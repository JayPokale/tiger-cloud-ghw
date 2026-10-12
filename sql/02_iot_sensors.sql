-- Challenge: Simulate an IoT sensor dataset
-- Based on https://www.tigerdata.com/docs/learn/tutorials/simulate-iot-sensor-data
CREATE TABLE IF NOT EXISTS sensors(
  id SERIAL PRIMARY KEY,
  type VARCHAR(50),
  location VARCHAR(50)
);
CREATE TABLE IF NOT EXISTS sensor_data (
  time TIMESTAMPTZ NOT NULL,
  sensor_id INTEGER,
  temperature DOUBLE PRECISION,
  cpu DOUBLE PRECISION,
  FOREIGN KEY (sensor_id) REFERENCES sensors (id)
) WITH (
  tsdb.hypertable
);
INSERT INTO sensors (type, location) VALUES
('a','floor'), ('a', 'ceiling'), ('b','floor'), ('b', 'ceiling');

INSERT INTO sensor_data (time, sensor_id, cpu, temperature)
SELECT time, sensor_id, random() AS cpu, random()*100 AS temperature
FROM generate_series(now() - interval '24 hour', now(), interval '5 minute') AS g1(time),
     generate_series(1,4,1) AS g2(sensor_id);
