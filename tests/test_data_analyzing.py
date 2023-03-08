import pytest

from models import CityForecast
from tasks import DataAnalyzingTask


@pytest.fixture
def city_forecasts():
    return [
        CityForecast(name="COPENHAGEN", avg_temp=20.0, avg_num_hours=3.0),
        CityForecast(name="LA", avg_temp=31.2, avg_num_hours=20.0),
        CityForecast(name="ATHENS", avg_temp=29.7, avg_num_hours=25.0)
    ]


def test_verify_sorted_forecasts(city_forecasts):
    task = DataAnalyzingTask(city_forecasts)
    sorted_forecasts = task._sort()
    assert ["LA", "ATHENS", "COPENHAGEN"] == [forecast.name for forecast in sorted_forecasts]


def test_verify_have_ratings(city_forecasts):
    task = DataAnalyzingTask(city_forecasts)
    rated_forecasts = task._calculate_rating()
    assert all(forecast.rating for forecast in rated_forecasts)


def test_sort_by_rating(city_forecasts):
    task = DataAnalyzingTask(city_forecasts)
    sorted_forecasts = task.sort_by_rating()
    assert [("LA", 1), ("ATHENS", 2), ("COPENHAGEN", 3)] == [(_sf.name, _sf.rating) for _sf in sorted_forecasts]


def test_fav_city(city_forecasts):
    task = DataAnalyzingTask(city_forecasts)
    task.sort_by_rating()
    res = task.fav_city()
    assert res == "The most favorable city to visit is LA"
