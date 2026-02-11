"""Tests."""
import os, sqlite3, tempfile
from sqldiff.differ import SchemaDiffer

def _mk(tables):
    f = tempfile.NamedTemporaryFile(suffix=".db",delete=False)
    c = sqlite3.connect(f.name)
    for s in tables: c.execute(s)
    c.commit(); c.close(); return f.name

def test_new_table():
    o = _mk(["CREATE TABLE u (id INTEGER)"])
    n = _mk(["CREATE TABLE u (id INTEGER)","CREATE TABLE p (id INTEGER)"])
    d = SchemaDiffer(); ch = d.diff(d.parse_schema(o), d.parse_schema(n))
    assert any(c.action=="add_table" and c.table=="p" for c in ch)
    os.unlink(o); os.unlink(n)

def test_new_col():
    o = _mk(["CREATE TABLE u (id INTEGER, name TEXT)"])
    n = _mk(["CREATE TABLE u (id INTEGER, name TEXT, email TEXT)"])
    d = SchemaDiffer(); ch = d.diff(d.parse_schema(o), d.parse_schema(n))
    assert any(c.action=="add_column" and c.detail=="email" for c in ch)
    os.unlink(o); os.unlink(n)

def test_no_change():
    db = _mk(["CREATE TABLE u (id INTEGER)"])
    d = SchemaDiffer(); s = d.parse_schema(db)
    assert len(d.diff(s,s)) == 0; os.unlink(db)
