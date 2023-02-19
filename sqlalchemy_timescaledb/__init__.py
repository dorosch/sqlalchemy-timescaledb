from sqlalchemy.dialects import registry


registry.register(
    'timescaledb',
    'sqlalchemy_timescaledb.dialect',
    'TimescaledbPsycopg2Dialect'
)
registry.register(
    'timescaledb.psycopg2',
    'sqlalchemy_timescaledb.dialect',
    'TimescaledbPsycopg2Dialect'
)
registry.register(
    'timescaledb.asyncpg',
    'sqlalchemy_timescaledb.dialect',
    'TimescaledbAsyncpgDialect'
)
