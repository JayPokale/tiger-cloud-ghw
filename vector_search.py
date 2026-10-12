"""Hybrid semantic + time search over Hacker News stories with pgvector on Tiger Cloud.

1. Pull recent HN stories (title, url, points, created_at) from the public Algolia API.
2. Embed titles locally with BAAI/bge-small-en-v1.5 (384 dims, via fastembed).
3. Store them in a hypertable with a vector column; index with pgvectorscale's
   StreamingDiskANN (falls back to pgvector HNSW if pgvectorscale is unavailable).
4. Query by meaning *and* time window / metadata in one SQL statement.
"""
import sys
import time
from datetime import datetime, timezone

import requests
from fastembed import TextEmbedding

from db import connect

TOPICS = ["postgres", "database", "time series", "vector search", "open source", "rust",
          "llm", "kubernetes", "privacy", "hardware", "space", "climate"]
MODEL = TextEmbedding("BAAI/bge-small-en-v1.5")


def fetch_stories(days=30, per_topic=100):
    since = int(time.time()) - days * 86400
    seen = {}
    for topic in TOPICS:
        r = requests.get("https://hn.algolia.com/api/v1/search_by_date", timeout=30, params={
            "query": topic, "tags": "story", "hitsPerPage": per_topic,
            "numericFilters": f"created_at_i>{since},points>5"})
        for h in r.json()["hits"]:
            if h.get("title"):
                seen[h["objectID"]] = (datetime.fromtimestamp(h["created_at_i"], timezone.utc),
                                       int(h["objectID"]), h["title"], h.get("url") or "", h.get("points") or 0)
    return list(seen.values())


def setup(conn):
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    try:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vectorscale CASCADE")
        index = "USING diskann (embedding vector_cosine_ops)"
    except Exception as e:  # noqa: BLE001
        print("pgvectorscale not available, using HNSW:", e)
        conn.rollback()
        index = "USING hnsw (embedding vector_cosine_ops)"
    conn.execute("""
        CREATE TABLE IF NOT EXISTS hn_stories (
            time      TIMESTAMPTZ NOT NULL,
            id        BIGINT      NOT NULL,
            title     TEXT        NOT NULL,
            url       TEXT,
            points    INT,
            embedding VECTOR(384) NOT NULL
        ) WITH (tsdb.hypertable, tsdb.chunk_interval = '7 days')""")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS hn_stories_id_time ON hn_stories (id, time)")
    conn.execute(f"CREATE INDEX IF NOT EXISTS hn_stories_embedding_idx ON hn_stories {index}")
    conn.commit()
    return index


def load(conn, stories):
    vecs = list(MODEL.embed([s[2] for s in stories]))
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO hn_stories (time, id, title, url, points, embedding) VALUES (%s,%s,%s,%s,%s,%s::vector) "
            "ON CONFLICT (id, time) DO NOTHING",
            [(*s, "[" + ",".join(f"{x:.6f}" for x in v) + "]") for s, v in zip(stories, vecs)])
    conn.commit()


def search(conn, question, days=None, min_points=0, k=5):
    q = "[" + ",".join(f"{x:.6f}" for x in next(MODEL.embed([question]))) + "]"
    sql = """SELECT time::date, points, title, round((1 - (embedding <=> %(q)s::vector))::numeric, 3) AS similarity
             FROM hn_stories
             WHERE points >= %(p)s {time_filter}
             ORDER BY embedding <=> %(q)s::vector LIMIT %(k)s"""
    time_filter = "AND time > now() - make_interval(days => %(d)s)" if days else ""
    return conn.execute(sql.format(time_filter=time_filter), {"q": q, "p": min_points, "d": days, "k": k}).fetchall()


if __name__ == "__main__":
    with connect() as conn:
        if "--load" in sys.argv:
            index = setup(conn)
            stories = fetch_stories()
            load(conn, stories)
            print(f"loaded {len(stories)} stories; vector index: {index}")
        n, lo, hi = conn.execute("SELECT count(*), min(time)::date, max(time)::date FROM hn_stories").fetchone()
        print(f"hn_stories: {n} rows from {lo} to {hi}\n")
        for question, days, pts in [("making Postgres faster for time-series data", None, 0),
                                    ("making Postgres faster for time-series data", 7, 20),
                                    ("open-weight AI models you can run locally", 14, 10)]:
            label = f"last {days} days, >= {pts} points" if days else "all time"
            print(f"Q: {question!r} ({label})")
            for row in search(conn, question, days, pts):
                print("  ", row[0], f"{row[1]:>4} pts", f"sim={row[3]}", row[2][:90])
            print()
        plan = conn.execute("EXPLAIN SELECT id FROM hn_stories ORDER BY embedding <=> (SELECT embedding FROM hn_stories LIMIT 1) LIMIT 5").fetchall()
        print("plan:", " / ".join(r[0].strip() for r in plan if "Index" in r[0]))
