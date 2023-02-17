# SQLAlchemy TimescaleDB

[![PyPI version](https://badge.fury.io/py/sqlalchemy-timescaledb.svg)][1]
[![Tests](https://github.com/dorosch/sqlalchemy-timescaledb/actions/workflows/tests.yml/badge.svg)][2]
[![codecov](https://codecov.io/gh/dorosch/sqlalchemy-timescaledb/branch/develop/graph/badge.svg?token=Gzh7KpADjZ)][3]
[![Downloads](https://pepy.tech/badge/sqlalchemy-timescaledb)][4]

This is the TimescaleDB dialect driver for SQLAlchemy. Drivers `psycopg2` and `asyncpg` are supported.

## Install

```bash
$ pip install sqlalchemy-timescaledb
```

## Usage

Adding to table `timescaledb_hypertable` option allows you to configure the [hypertable parameters][5]:

```Python
import datetime
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, Integer, String, DateTime

engine = create_engine('timescaledb://user:password@host:port/database')
metadata = MetaData()
metadata.bind = engine

Metric = Table(
    'metric', metadata,
    Column('name', String),
    Column('value', Integer),
    Column('timestamp', DateTime(), default=datetime.datetime.now),
    timescaledb_hypertable={
        'time_column_name': 'timestamp'
    }
)

metadata.create_all(engine)
```

## Functions

Timescaledb functions implemented:

### [first(value, time)][6]

```Python
func.first(Metric.value, Metric.timestamp)
```

### [last(value, time)][7]

```Python
func.last(Metric.value, Metric.timestamp)
```


[1]: https://badge.fury.io/py/sqlalchemy-timescaledb
[2]: https://github.com/dorosch/sqlalchemy-timescaledb/actions/workflows/tests.yml
[3]: https://codecov.io/gh/dorosch/sqlalchemy-timescaledb
[4]: https://pepy.tech/project/sqlalchemy-timescaledb
[5]: https://docs.timescale.com/api/latest/hypertable/create_hypertable/#optional-arguments
[6]: https://docs.timescale.com/api/latest/hyperfunctions/first/
[7]: https://docs.timescale.com/api/latest/hyperfunctions/last/
