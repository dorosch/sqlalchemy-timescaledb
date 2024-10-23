# SQLAlchemy TimescaleDB

[![PyPI version](https://badge.fury.io/py/sqlalchemy-timescaledb.svg)][1]
[![Tests](https://github.com/dorosch/sqlalchemy-timescaledb/actions/workflows/tests.yml/badge.svg)][2]
[![codecov](https://codecov.io/gh/dorosch/sqlalchemy-timescaledb/branch/develop/graph/badge.svg?token=Gzh7KpADjZ)][3]
[![Downloads](https://pepy.tech/badge/sqlalchemy-timescaledb)][4]

This is the TimescaleDB dialect driver for SQLAlchemy. Drivers `psycopg2`, `psycopg` and `asyncpg` are supported.

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

# or use timescaledb+psycopg/asyncpg
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

Or using `declarative_base` style:

```Python
import datetime

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Float, String, DateTime

Base = declarative_base()

class Metric(Base):
    __table_args__ = ({
        'timescaledb_hypertable': {
            'time_column_name': 'timestamp'
        }
    })

    name = Column(String)
    value = Column(Float)
    timestamp = Column(
        DateTime(), default=datetime.datetime.now, primary_key=True
    )
```

## Parameters

* [chunk_time_interval][6]

## Functions

Timescaledb functions implemented:

### [first(value, time)][7]

```Python
func.first(Metric.value, Metric.timestamp)
```

### [last(value, time)][8]

```Python
func.last(Metric.value, Metric.timestamp)
```


[1]: https://badge.fury.io/py/sqlalchemy-timescaledb
[2]: https://github.com/dorosch/sqlalchemy-timescaledb/actions/workflows/tests.yml
[3]: https://codecov.io/gh/dorosch/sqlalchemy-timescaledb
[4]: https://pepy.tech/project/sqlalchemy-timescaledb
[5]: https://docs.timescale.com/api/latest/hypertable/create_hypertable/#optional-arguments
[6]: https://docs.timescale.com/api/latest/hypertable/set_chunk_time_interval/
[7]: https://docs.timescale.com/api/latest/hyperfunctions/first/
[8]: https://docs.timescale.com/api/latest/hyperfunctions/last/
