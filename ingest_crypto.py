"""Stream live crypto ticks from Coinbase's public websocket into the crypto_ticks hypertable.

Same pipeline as Tiger Data's "Ingest real-time financial data" tutorial (websocket ->
in-memory batch -> hypertable), with Coinbase's public ticker channel as the source
instead of Twelve Data, so no API key is needed.
"""
import json
import sys
import time
from datetime import datetime

import websocket

from db import connect

PRODUCTS = {"BTC-USD": "BTC/USD", "ETH-USD": "ETH/USD", "SOL-USD": "SOL/USD"}
BATCH_SIZE = 50
RUN_SECONDS = int(sys.argv[1]) if len(sys.argv) > 1 else 180


def main():
    conn = connect()
    ws = websocket.create_connection("wss://ws-feed.exchange.coinbase.com", timeout=20)
    ws.send(json.dumps({"type": "subscribe", "product_ids": list(PRODUCTS), "channels": ["ticker"]}))
    batch, total, started = [], 0, time.time()
    while time.time() - started < RUN_SECONDS:
        msg = json.loads(ws.recv())
        if msg.get("type") != "ticker":
            continue
        batch.append((datetime.fromisoformat(msg["time"].replace("Z", "+00:00")),
                      PRODUCTS[msg["product_id"]], float(msg["price"]), msg["volume_24h"]))
        if len(batch) >= BATCH_SIZE:
            with conn.cursor() as cur:
                cur.executemany("INSERT INTO crypto_ticks (time, symbol, price, day_volume) VALUES (%s, %s, %s, %s)", batch)
            conn.commit()
            total += len(batch)
            print(f"{time.strftime('%H:%M:%S')} inserted batch of {len(batch)} (total {total}) last {batch[-1][1]} {batch[-1][2]}", flush=True)
            batch = []
    ws.close()
    conn.close()


if __name__ == "__main__":
    main()
