import pytest

from models import DateForecast, CityForecast
from tasks import DataCalculationTask

calculation_task = DataCalculationTask()


@pytest.fixture
def mock_date_info():
    return {
        "date": "2022-03-31",
        "hours": [
            {
                "hour": "0",
                "temp": 10,
                "condition": "rain",
            },
            {
                "hour": "9",
                "temp": 15,
                "condition": "overcast",
            },
            {
                "hour": "12",
                "temp": 20,
                "condition": "partly-cloudy",
            },
            {
                "hour": "18",
                "temp": 25,
                "condition": "clear"
            },
            {
                "hour": "23",
                "temp": 5,
                "condition": "thunderstorm",
            },
        ],
    }


@pytest.fixture
def city_forecast_obj():
    return CityForecast(
        name="COPENHAGEN",
        dates=[
            DateForecast(date="2022-03-31", avg_temp=20, dry_hours=3)
        ],
        avg_temp=20.0,
        avg_num_hours=3.0
    )


def test_calculate_avg_daily_temp(mock_date_info):
    assert calculation_task._calculate_avg_daily_temp(mock_date_info) == 20


def test_calculate_dry_hours(mock_date_info):
    assert calculation_task._calculate_dry_hours(mock_date_info) == 3


def test_calculate_avgs():
    dates = [
        DateForecast(date="2023-01-01", avg_temp=20, dry_hours=10),
        DateForecast(date="2023-01-02", avg_temp=25, dry_hours=8),
        DateForecast(date="2023-01-03", avg_temp=None, dry_hours=0),
    ]
    assert calculation_task._calculate_avgs(dates) == (22.5, 9)


def test_get_city_forecast(mock_date_info, city_forecast_obj):
    city_data = (('COPENHAGEN', [mock_date_info]),)
    res = calculation_task.get_city_forecasts(city_data)
    assert city_forecast_obj == res[0]
