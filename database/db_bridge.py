#!/usr/bin/env python3
"""
Floor Guard AI - Database Bridge for Node.js / Express Backend
Executes parameterized SQLite queries and returns JSON.
"""

import sqlite3
import json
import sys
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'database.sqlite')

def execute_cmd(payload):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    action = payload.get("action")
    query = payload.get("query")
    params = payload.get("params", [])

    try:
        if action == "query":
            cursor.execute(query, params)
            rows = [dict(row) for row in cursor.fetchall()]
            return {"status": "ok", "data": rows}
        elif action == "execute":
            cursor.execute(query, params)
            conn.commit()
            return {"status": "ok", "lastrowid": cursor.lastrowid, "rowcount": cursor.rowcount}
        elif action == "batch":
            for q, p in payload.get("commands", []):
                cursor.execute(q, p)
            conn.commit()
            return {"status": "ok"}
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

if __name__ == '__main__':
    try:
        input_data = sys.stdin.read()
        payload = json.loads(input_data)
        res = execute_cmd(payload)
        print(json.dumps(res))
    except Exception as err:
        print(json.dumps({"status": "error", "message": str(err)}))
