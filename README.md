# Tiger Cloud challenges, Global Hack Week: Hacktoberfest

Six Tiger Data challenges done on one free Tiger Cloud service (`hacktoberfest-ghw`, TimescaleDB 2.30 on PostgreSQL 18), driven from the [Tiger CLI](https://github.com/timescale/tiger-cli). Raw query output for every step is in the `out-*.txt` files.

| # | Challenge | Files | Result |
|---|---|---|---|
| 1 | Set up a service and create your first hypertable | `sql/01_*.sql` → `out-01.txt` | `conditions` hypertable, 59,946 rows over 14 days in 3 weekly chunks. A one-day query excludes the other chunks. |
| 2 | Simulate an IoT sensor dataset | `sql/02_*.sql` → `out-02.txt` | 4 sensors, 24 h of readings every 5 min, plus `time_bucket`, `last()` and joins on metadata. |
| 3 | Ingest real-time financial data | `sql/04_crypto_tables.sql`, `ingest_crypto.py` → `out-ingest*.txt` | Live BTC/ETH/SOL ticks from Coinbase's public websocket, batched 50 rows per insert into `crypto_ticks` (~1,750 ticks). |
| 4 | Accelerate dashboards with continuous aggregates | `sql/03_*.sql` → `out-03*.txt` | `conditions_hourly` (per-room hourly avg/min/max) and `crypto_candles_1m` (1-minute OHLCV), each with a refresh policy. The same 1,005-row hourly dashboard query takes **21.4 ms** on the raw hypertable and **0.12 ms** from the continuous aggregate. |
| 5 | AI-powered vector search with pgvector | `vector_search.py` → `out-05.txt` | 484 recent Hacker News stories, embedded locally with `bge-small-en-v1.5` (384 dims), stored in a hypertable with a pgvectorscale **StreamingDiskANN** index, and queried by meaning plus a time window and points in one SQL statement. |
| 6 | Integrate Tiger Cloud with your AI agent (Tiger CLI + MCP) | `out-06-*.txt` | `tiger mcp install copilot`, then GitHub Copilot CLI answered questions about the service in plain English using the Tiger MCP tools (list services, show schema, execute SQL). |

## Notes

- **Financial data:** the Tiger tutorial uses Twelve Data, which needs an API key. `ingest_crypto.py` keeps the tutorial's schema and pipeline (websocket → in-memory batch → hypertable) but reads Coinbase's public ticker channel instead.
- **Vector search:** DiskANN is approximate, so results are close to, but not strictly in, similarity order. With the "last 7 days" filter the matches are weaker, simply because the recent sample has no strong Postgres story.
- **Safety:** the Tiger CLI runs with `read_only = prod`. The service is tagged `DEV`, so anything tagged `PROD` stays protected.

## Run it

```bash
python -m venv .venv && .venv/bin/pip install "psycopg[binary]" sqlparse websocket-client fastembed requests
tiger auth login && tiger service create --name hacktoberfest-ghw --cpu shared
.venv/bin/python run_sql.py sql/01_first_hypertable.sql sql/01_queries.sql
.venv/bin/python run_sql.py sql/02_iot_sensors.sql sql/02_queries.sql
.venv/bin/python run_sql.py sql/04_crypto_tables.sql && .venv/bin/python ingest_crypto.py 180
.venv/bin/python run_sql.py sql/03_continuous_aggregates.sql sql/03_queries.sql
.venv/bin/python vector_search.py --load
```
