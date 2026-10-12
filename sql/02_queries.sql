SELECT * FROM sensors;
SELECT count(*) AS readings FROM sensor_data;
SELECT time_bucket('30 minutes', time) AS period, AVG(temperature) AS avg_temp, AVG(cpu) AS avg_cpu
FROM sensor_data GROUP BY period ORDER BY period DESC LIMIT 5;
SELECT time_bucket('30 minutes', time) AS period, AVG(temperature) AS avg_temp, last(temperature, time) AS last_temp, AVG(cpu) AS avg_cpu
FROM sensor_data GROUP BY period ORDER BY period DESC LIMIT 5;
SELECT sensors.location, time_bucket('30 minutes', time) AS period, AVG(temperature) AS avg_temp, last(temperature, time) AS last_temp, AVG(cpu) AS avg_cpu
FROM sensor_data JOIN sensors ON sensor_data.sensor_id = sensors.id
GROUP BY period, sensors.location ORDER BY period DESC, location LIMIT 6;
