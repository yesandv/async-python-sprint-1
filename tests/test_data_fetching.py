from tasks import DataFetchingTask
from utils import CITIES


def test_get_city_info():
    task = DataFetchingTask()
    assert all(task.get_city_info(city) for city in CITIES)


def test_get_invalid_city_info():
    invalid_city = "COPENHAGEN"
    task = DataFetchingTask()
    try:
        task.get_city_info(invalid_city)
        assert False
    except Exception:
        assert True


def test_fetch_city_data():
    res = DataFetchingTask().fetch_city_data(CITIES)
    assert len(list(res)) == len(CITIES)
