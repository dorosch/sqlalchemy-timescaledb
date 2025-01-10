from sqlalchemy import schema, event, DDL
from sqlalchemy.dialects.postgresql.asyncpg import PGDialect_asyncpg
from sqlalchemy.dialects.postgresql.base import PGDDLCompiler, PGDialect
from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2
from sqlalchemy.sql.elements import ClauseElement

try:
    import alembic
except ImportError:
    pass
else:
    from alembic.ddl import postgresql

    class TimescaledbImpl(postgresql.PostgresqlImpl):
        __dialect__ = 'timescaledb'

def all_subclasses(cls, include_cls: bool = True) -> set:
    """
    A Recursive version of cls.__subclasses__() (i.e including subclasses of subclasses)
    """
    if not hasattr(cls, "__subclasses__"):
        if type(cls) is type:
            cls_name = cls.__name__
        else:
            cls_name = cls.__class__.__name__

        raise ValueError(f"Can't get subclasses of {cls_name}")

    ret = cls.__subclasses__()
    for subcls in ret:
        ret += all_subclasses(subcls, include_cls = False)

    if include_cls:
        ret = [cls] + ret

    return set(ret)



class TimescaledbDDLCompiler(PGDDLCompiler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        # patch sqlalchemy to use postgres compilers for timescaledb dialect:
        # we do this when the compiler is instantiated rather than in python's parse/init phase to remove the possibility
        #  of load order causing problems (i.e perhaps timescaledb might somehow be loaded before postgresql
        #  [or some postgresql extension])
        self.patch_postgres_compilers()

    @staticmethod
    def patch_postgres_compilers():
        """
        Here we iterate over ClauseElement subclasses to find postgres-specific compilers, and duplicate them so that they also
         work with timescaledb

        This allows the timescaledb dialect to use postgres compilers which specify the postgresql dialect via e.g
            @compile(class,dialect="postgresql")
            something.execute_if(dialect="postgresql")

        (if we didn't do this, the "if dialect == postgresql" test will fail for these compilers when using the timescaledb dialect,
         [ because weirdly it seems that "postgresql" != "timescaledb" ])

        The compiler_dispatcher works by having a 'specs' dict, with the key being the db dialect and the value being the
         compiler for that type of SQL clause for that dialect.

        When attempting to compile, it chooses the dialect-specific compiler and compiles the sql with something like:

         if dialect not in dispatcher.specs: compiler = default_compiler
         else compiler = dispatcher.specs[dialect]

         compiled_sql = compiler(some_clauseelement) # call compiler with the ClauseElement

        Due to this, if a compiler specifies 'postgresql' as the dialect and the system is running on timescaledb, then
         the dispatcher will fall back to the default compiler rather than using the postgres one, because the current
         db dialect isn't 'postgresql'

        We handle this here by iterating through all ClauseElement subclasses, looking for postgres-specific compilers,
         and we copy them into a new 'timescaledb' entry in dispatcher.specs so that timescaledb is handled the same as
         postgresql.

        This approach saves us from needing to re-implement timescaledb compilers for everything - if we didn't do the
         above, we would need to manually copy a bunch of compilers, like you see commented out at the end of this file
        """

        for cls in all_subclasses(ClauseElement):
            if (hasattr(cls, "_compiler_dispatcher") and hasattr(cls._compiler_dispatcher, "specs") and 'postgresql' in cls._compiler_dispatcher.specs):
                # print(f"Patching compiler to use {cls._compiler_dispatcher.specs['postgresql']} for {cls} and timescaledb dialect")
                cls._compiler_dispatcher.specs['timescaledb'] = cls._compiler_dispatcher.specs['postgresql']

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


class TimescaledbDialect(PGDialect):
    name = 'timescaledb'
    ddl_compiler = TimescaledbDDLCompiler
    construct_arguments = [
        (
            schema.Table, {
                "hypertable": {}
            }
        )
    ]


class TimescaledbPsycopg2Dialect(TimescaledbDialect,PGDialect_psycopg2):
    driver = 'psycopg2'
    supports_statement_cache = True


class TimescaledbAsyncpgDialect(TimescaledbDialect, PGDialect_asyncpg):
    driver = 'asyncpg'
    supports_statement_cache = True


"""
This function blatantly stolen from venv/lib/python3.11/site-packages/alembic/ddl/postgresql.py
You shouldn't need to add any of these, see TimescaledbDDLCompiler.patch_postgres_compilers.

@compiles(PostgresqlColumnType, "timescaledb")
def visit_column_type(
    element: PostgresqlColumnType, compiler: PGDDLCompiler, **kw
) -> str:
    return "%s %s %s %s" % (
        alter_table(compiler, element.table_name, element.schema),
        alter_column(compiler, element.column_name),
        "TYPE %s" % format_type(compiler, element.type_),
        "USING %s" % element.using if element.using else "",
    )

"""
