"""Leftover scan of one site DB for the old name. Read-only.
  bench --site S execute /path/db_scan.py --kwargs "{'pattern':'old_app|Old App','allow':'keep_prefix_|other'}"
"""
import re
import frappe


def execute(pattern, allow=""):
    rx, ok = re.compile(pattern, re.I), (re.compile(allow, re.I) if allow else None)
    cols = frappe.db.sql("""select table_name, column_name from information_schema.columns
        where table_schema=database() and data_type in ('varchar','text','longtext','mediumtext','json')""")
    hits = {}
    for t, c in cols:
        for (v,) in frappe.db.sql(f"select `{c}` from `{t}` where `{c}` regexp %s limit 50", (pattern,)):
            if v and rx.search(v) and not (ok and ok.search(v)):
                hits[f"{t}.{c}"] = hits.get(f"{t}.{c}", 0) + 1
    print({"columns_scanned": len(cols), "hits": hits})
