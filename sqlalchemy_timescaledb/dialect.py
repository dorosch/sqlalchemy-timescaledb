from sqlalchemy import schema, event, DDL
from sqlalchemy.dialects.postgresql.asyncpg import PGDialect_asyncpg
from sqlalchemy.dialects.postgresql.base import PGDDLCompiler
from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2
from sqlalchemy.dialects.postgresql.psycopg import PGDialect_psycopg

try:
    import alembic
except ImportError:
    pass
else:
    from alembic.ddl import postgresql

    class TimescaledbImpl(postgresql.PostgresqlImpl):
        __dialect__ = 'timescaledb'


class TimescaledbDDLCompiler(PGDDLCompiler):
    def post_create_table(self, table):
        hypertable = table.kwargs.get('timescaledb_hypertable', {})

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

        return super().post_create_table(table)

    @staticmethod
    def ddl_hypertable(table_name, hypertable):
        time_column_name = hypertable['time_column_name']
        chunk_time_interval = hypertable.get('chunk_time_interval', '7 days')

        if isinstance(chunk_time_interval, str):
            if chunk_time_interval.isdigit():
                chunk_time_interval = int(chunk_time_interval)
            else:
                chunk_time_interval = f"INTERVAL '{chunk_time_interval}'"

        return DDL(
            f"""
            SELECT create_hypertable(
                '{table_name}',
                '{time_column_name}',
                chunk_time_interval => {chunk_time_interval},
                if_not_exists => TRUE
            );
            """
        )


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


class TimescaledbPsycopgDialect(TimescaledbDialect, PGDialect_psycopg):
    driver = 'psycopg'
    supports_statement_cache = True
