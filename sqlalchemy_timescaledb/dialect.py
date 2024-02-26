import textwrap
from typing import Optional, Mapping, Any

from sqlalchemy import schema, event, DDL, Table, Dialect, ExecutableDDLElement
from sqlalchemy.dialects.postgresql.asyncpg import PGDialect_asyncpg
from sqlalchemy.dialects.postgresql.base import PGDDLCompiler
from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2
from sqlalchemy.engine.interfaces import SchemaTranslateMapType
from sqlalchemy.ext import compiler
from sqlalchemy_utils.view import CreateView, compile_create_materialized_view

try:
    import alembic
except ImportError:
    pass
else:
    from alembic.ddl import postgresql

    class TimescaledbImpl(postgresql.PostgresqlImpl):
        __dialect__ = 'timescaledb'


def _get_interval(value):
    if isinstance(value, str):
        return f"INTERVAL '{value}'"
    elif isinstance(value, int):
        return str(value)
    else:
        return "NULL"


def _create_map(mapping: dict):
    return ", ".join([f'{key} => {value}' for key, value in mapping.items()])


@compiler.compiles(CreateView, 'timescaledb')
def compile_create_view(create, compiler, **kw):
    return compiler.visit_create_view(create, **kw)

class TimescaledbDDLCompiler(PGDDLCompiler):

    def visit_create_view(self, create, **kw):
        ret = compile_create_materialized_view(create, self, **kw)
        view = create.element
        continuous = view.kwargs.get('timescaledb_continuous', {})
        if continuous:
            event.listen(
                view,
                'after_create',
                self.ddl_add_continuous(
                    view.name, continuous
                ).execute_if(
                    dialect='timescaledb'
                )
            )
        return ret

    def visit_create_table(self, create, **kw):
        ret = super().visit_create_table(create, **kw)
        table = create.element
        hypertable = table.kwargs.get('timescaledb_hypertable', {})
        compress = table.kwargs.get('timescaledb_compress', {})

        if hypertable:
            event.listen(
                table,
                'after_create',
                self.ddl_hypertable(
                    table.name, hypertable
                ).execute_if(
                    dialect='timescaledb'
                )
            )

        if compress:
            event.listen(
                table,
                'after_create',
                self.ddl_compress(
                    table.name, compress
                ).execute_if(
                    dialect='timescaledb'
                )
            )
            event.listen(
                table,
                'after_create',
                self.ddl_compression_policy(
                    table.name, compress
                ).execute_if(
                    dialect='timescaledb'
                )
            )

        return ret

    @staticmethod
    def ddl_hypertable(table_name, hypertable):
        time_column_name = hypertable['time_column_name']
        chunk_time_interval = _get_interval(hypertable.get('chunk_time_interval', '7 days'))

        parameters = _create_map(dict(chunk_time_interval=chunk_time_interval, if_not_exists="TRUE"))
        return DDL(textwrap.dedent(f"""SELECT create_hypertable('{table_name}','{time_column_name}',{parameters})"""))

    @staticmethod
    def ddl_compress(table_name, compress):
        segmentby = compress['compress_segmentby']

        return DDL(textwrap.dedent(f"""
            ALTER TABLE {table_name} SET (timescaledb.compress, timescaledb.compress_segmentby = '{segmentby}')
            """))

    @staticmethod
    def ddl_compression_policy(table_name, compress):
        schedule_interval = _get_interval(compress.get('compression_policy_schedule_interval', '7 days'))

        parameters = _create_map(dict(schedule_interval=schedule_interval))
        return DDL(textwrap.dedent(f"""SELECT add_compression_policy('{table_name}', {parameters})"""))

    @staticmethod
    def ddl_add_continuous(table_name, continuous):
        start_offset = _get_interval(continuous.get('continuous_aggregate_policy_start_offset', None))
        end_offset = _get_interval(continuous.get('continuous_aggregate_policy_end_offset', None))
        schedule_interval = _get_interval(continuous.get('continuous_aggregate_policy_schedule_interval', None))

        parameters = _create_map(
            dict(start_offset=start_offset, end_offset=end_offset, schedule_interval=schedule_interval))
        return DDL(textwrap.dedent(f"""SELECT add_continuous_aggregate_policy('{table_name}', {parameters})"""))


class TimescaledbDialect:
    name = 'timescaledb'
    ddl_compiler = TimescaledbDDLCompiler
    construct_arguments = [
        (
            schema.Table, {
                "hypertable": {},
                "compress": {},
                "continuous": {},
            }
        )
    ]


class TimescaledbPsycopg2Dialect(TimescaledbDialect, PGDialect_psycopg2):
    driver = 'psycopg2'
    supports_statement_cache = True


class TimescaledbAsyncpgDialect(TimescaledbDialect, PGDialect_asyncpg):
    driver = 'asyncpg'
    supports_statement_cache = True
