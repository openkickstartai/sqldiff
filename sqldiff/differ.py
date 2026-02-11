"""Schema comparison engine."""
import sqlite3, re
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Column:
    name: str; type: str; nullable: bool = True; default: Optional[str] = None; pk: bool = False

@dataclass
class Table:
    name: str; columns: List[Column] = field(default_factory=list)

@dataclass
class Change:
    action: str; table: str; detail: str = ""; sql_up: str = ""; sql_down: str = ""

class SchemaDiffer:
    def parse_schema(self, src: str) -> Dict[str, Table]:
        if src.endswith((".db",".sqlite")): return self._parse_sqlite(src)
        if src.endswith(".sql"): return self._parse_sql(src)
        return {}

    def _parse_sqlite(self, p):
        conn = sqlite3.connect(p); tables = {}
        for (n,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
            t = Table(name=n)
            for r in conn.execute(f"PRAGMA table_info('{n}')"):
                t.columns.append(Column(name=r[1],type=r[2],nullable=not r[3],default=r[4],pk=bool(r[5])))
            tables[n] = t
        conn.close(); return tables

    def _parse_sql(self, p):
        sql = open(p).read(); tables = {}
        for m in re.finditer(r"CREATE TABLE\s+(\w+)\s*\(([^;]+)\)", sql, re.I):
            t = Table(name=m.group(1))
            for c in m.group(2).split(","):
                c = c.strip()
                if c and not c.upper().startswith(("PRIMARY","UNIQUE","CHECK","FOREIGN")):
                    parts = c.split()
                    if len(parts)>=2: t.columns.append(Column(name=parts[0],type=parts[1]))
            tables[m.group(1)] = t
        return tables

    def diff(self, old, new) -> List[Change]:
        changes = []
        for n in new:
            if n not in old:
                cols = ", ".join(f"{c.name} {c.type}" for c in new[n].columns)
                changes.append(Change("add_table",n,sql_up=f"CREATE TABLE {n} ({cols});",sql_down=f"DROP TABLE {n};"))
        for n in old:
            if n not in new: changes.append(Change("drop_table",n,sql_up=f"DROP TABLE {n};"))
        for n in set(old)&set(new):
            oc = {c.name:c for c in old[n].columns}; nc = {c.name:c for c in new[n].columns}
            for cn in nc:
                if cn not in oc:
                    c = nc[cn]; changes.append(Change("add_column",n,cn,f"ALTER TABLE {n} ADD COLUMN {c.name} {c.type};"))
            for cn in oc:
                if cn not in nc: changes.append(Change("drop_column",n,cn,f"-- manual: DROP COLUMN {cn}"))
        return changes
