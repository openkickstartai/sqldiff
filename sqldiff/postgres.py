"""PostgreSQL schema parser."""
import re
from typing import Dict, Optional
from sqldiff.differ import Table, Column

def parse_pg_url(url: str) -> Dict[str, str]:
    """Parse postgresql://user:pass@host:port/dbname."""
    m = re.match(r'postgresql://(?:([^:]+):([^@]+)@)?([^:/]+)(?::(\d+))?/(.+)', url)
    if not m:
        raise ValueError(f'Invalid PostgreSQL URL: {url}')
    return {'user': m.group(1) or 'postgres', 'password': m.group(2) or '',
            'host': m.group(3), 'port': m.group(4) or '5432', 'dbname': m.group(5)}

def fetch_pg_schema(url: str) -> Dict[str, Table]:
    """Fetch schema from a live PostgreSQL database."""
    try:
        import psycopg2
    except ImportError:
        raise ImportError('pip install psycopg2-binary for PostgreSQL support')
    params = parse_pg_url(url)
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    cur.execute("""SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'""")
    tables = {}
    for (table_name,) in cur.fetchall():
        cur.execute("""SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns WHERE table_name = %s
            ORDER BY ordinal_position""", (table_name,))
        columns = [Column(name=r[0], type=r[1], nullable=(r[2]=='YES'), default=r[3])
                   for r in cur.fetchall()]
        tables[table_name] = Table(name=table_name, columns=columns)
    conn.close()
    return tables
