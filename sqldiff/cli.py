"""CLI."""
import click
from sqldiff.differ import SchemaDiffer
from sqldiff.formatter import format_migration

@click.group()
def main(): pass

@main.command()
@click.argument("source")
@click.argument("target")
@click.option("--format","fmt",default="sql")
def compare(source, target, fmt):
    d = SchemaDiffer()
    changes = d.diff(d.parse_schema(source), d.parse_schema(target))
    click.echo(format_migration(changes, fmt))
