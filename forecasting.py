from tasks import (
    DataFetchingTask,
    DataCalculationTask,
    DataAggregationTask,
    DataAnalyzingTask,
)
from utils import CITIES


def forecast_weather():
    """
    Анализ погодных условий по городам
    """
    city_data = DataFetchingTask().fetch_city_data(CITIES)
    calculation_task = DataCalculationTask()
    forecasts = calculation_task.get_city_forecasts(city_data)
    analyzing_task = DataAnalyzingTask(list(forecasts))
    ratings = analyzing_task.sort_by_rating()
    print(analyzing_task.fav_city())
    aggregation_task = DataAggregationTask()
    aggregation_task.create_table(ratings)
    aggregation_task.create_file("forecasts.csv")


if __name__ == "__main__":
    forecast_weather()
