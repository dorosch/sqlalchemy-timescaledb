from sqlalchemy import schema
from sqlalchemy.dialects.postgresql.asyncpg import PGDialect_asyncpg
from sqlalchemy.dialects.postgresql.base import PGDDLCompiler
from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2


class TimescaledbDDLCompiler(PGDDLCompiler):
    def post_create_table(self, table):
        hypertable = table.kwargs.get('timescaledb_hypertable', {})

        if hypertable:
            hypertable_sql = \
                ';\n\nSELECT create_hypertable(' \
                f"'{table.name}', '{hypertable['time_column_name']}'" \
                ");"

            return super().post_create_table(table) + hypertable_sql

        return super().post_create_table(table)


class TimescaledbDialect:
    name = 'timescaledb'
    ddl_compiler = TimescaledbDDLCompiler
    construct_arguments = [
        (
            schema.Table, {
                "hypertable": {}
            }
        )
    ]


class TimescaledbPsycopg2Dialect(TimescaledbDialect, PGDialect_psycopg2):
    driver = 'psycopg2'
    supports_statement_cache = True


class TimescaledbAsyncpgDialect(TimescaledbDialect, PGDialect_asyncpg):
    driver = 'asyncpg'
    supports_statement_cache = True
