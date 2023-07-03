import pytest
from sqlalchemy import DDL

from sqlalchemy_timescaledb.dialect import TimescaledbDDLCompiler


class TestTimescaledbDDLCompiler:
    def test_default_params(self):
        assert TimescaledbDDLCompiler.ddl_hypertable(
            'test', {'time_column_name': 'timestamp'}
        ).compile().string == DDL(
            f"""
            SELECT create_hypertable(
                'test',
                'timestamp',
                chunk_time_interval => INTERVAL '7 days',
                if_not_exists => TRUE
            );
            """
        ).compile().string

    @pytest.mark.parametrize('interval,expected', [
        ('1 days', "INTERVAL '1 days'"),
        ('7 hour', "INTERVAL '7 hour'"),
        (86400, 86400),
        ('86400', 86400)
    ])
    def test_chunk_time_interval(self, interval, expected):
        assert TimescaledbDDLCompiler.ddl_hypertable(
            'test', {
                'time_column_name': 'timestamp',
                'chunk_time_interval': interval
            }
        ).compile().string == DDL(
            f"""
            SELECT create_hypertable(
                'test',
                'timestamp',
                chunk_time_interval => {expected},
                if_not_exists => TRUE
            );
            """
        ).compile().string
