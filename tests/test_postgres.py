"""Tests for PostgreSQL URL parser."""
from sqldiff.postgres import parse_pg_url

def test_full_url():
    r = parse_pg_url('postgresql://admin:secret@db.example.com:5433/mydb')
    assert r['user'] == 'admin'
    assert r['password'] == 'secret'
    assert r['host'] == 'db.example.com'
    assert r['port'] == '5433'
    assert r['dbname'] == 'mydb'

def test_minimal_url():
    r = parse_pg_url('postgresql://localhost/testdb')
    assert r['host'] == 'localhost'
    assert r['dbname'] == 'testdb'
    assert r['port'] == '5432'

def test_invalid_url():
    try:
        parse_pg_url('mysql://localhost/db')
        assert False
    except ValueError:
        pass
