# sqldiff

Compare database schemas, generate migration SQL.

## Install

```bash
git clone https://github.com/openkickstartai/sqldiff.git
cd sqldiff && pip install -e .
```

## Usage

```bash
sqldiff compare old.db new.db
sqldiff migrate v1.sql v2.sql --output migration.sql
```

## Testing

```bash
pytest -v
```
