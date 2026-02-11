"""Output formatting."""
import json
def format_migration(changes, fmt="sql"):
    if fmt=="json": return json.dumps([{"action":c.action,"table":c.table,"detail":c.detail,"up":c.sql_up,"down":c.sql_down} for c in changes],indent=2)
    lines = ["-- sqldiff migration",f"-- {len(changes)} changes\n"]
    for c in changes: lines += [f"-- {c.action}: {c.table}"+("."+c.detail if c.detail else ""),c.sql_up,""]
    return "\n".join(lines)
