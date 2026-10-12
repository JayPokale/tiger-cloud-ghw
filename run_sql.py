"""Run a .sql file statement by statement and print each result as a table."""
import sys

import sqlparse

from db import connect

with connect(autocommit=True) as conn:
    for path in sys.argv[1:]:
        for stmt in sqlparse.split(open(path).read()):
            sql = sqlparse.format(stmt, strip_comments=True).strip()
            if not sql:
                continue
            print(f"\n=> {sql.splitlines()[0][:110]}")
            cur = conn.execute(sql)
            if cur.description:
                cols = [d.name for d in cur.description]
                rows = cur.fetchall()
                print(" | ".join(cols))
                for r in rows[:20]:
                    print(" | ".join(str(v)[:36] for v in r))
                if len(rows) > 20:
                    print(f"... ({len(rows)} rows)")
            else:
                print(cur.statusmessage)
