import os

import pytest
from pandas import DataFrame

from models import CityForecast, DateForecast, TableHeader
from tasks import DataAggregationTask

aggregation_task = DataAggregationTask()


@pytest.fixture
def city_forecast_obj():
    return CityForecast(
        name="COPENHAGEN",
        dates=[
            DateForecast(date="2023-01-01", avg_temp=15, dry_hours=8),
            DateForecast(date="2023-01-02", avg_temp=18, dry_hours=6),
            DateForecast(date="2023-01-03", avg_temp=22, dry_hours=12)
        ],
        avg_temp=20.0,
        avg_num_hours=10.0,
        rating=1
    )


def test_create_table(city_forecast_obj):
    aggregation_task.create_table([city_forecast_obj])
    assert aggregation_task.table == {
        TableHeader.CITY.value: ["COPENHAGEN", ""],
        TableHeader.EMPTY.value: ["Температура, среднее", "Без осадков, часов"],
        TableHeader.AVG.value: [20.0, 10.0],
        TableHeader.RATING.value: [1, ""],
        "2023-01-01": [15, 8],
        "2023-01-02": [18, 6],
        "2023-01-03": [22, 12],
    }


def test_create_file(city_forecast_obj, tmp_path):
    aggregation_task.create_table([city_forecast_obj])
    file_name = "test.csv"
    aggregation_task.create_file(file_name)
    assert os.path.isfile(file_name)
