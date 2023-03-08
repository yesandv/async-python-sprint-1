import logging
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Queue, Pool, Manager
from typing import Iterable

from pandas import DataFrame

from api_client import YandexWeatherAPI
from models import CityForecast, DateForecast, TableHeader, TableRow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetchingTask:

    def __init__(self):
        self.api = YandexWeatherAPI()
        self.queue = Queue()

    def get_city_info(self, city_name: str) -> tuple[str, dict]:
        try:
            logger.info(f"Getting a forecast for {city_name.capitalize()}")
            return city_name, self.api.get_forecasting(city_name)["forecasts"]
        except KeyError:
            raise Exception(
                f"There is no 'forecasts' key for {city_name.capitalize()}"
            )

    def fetch_city_data(self, cities: dict) -> Iterable:
        with ThreadPoolExecutor() as executor:
            city_data = executor.map(self.get_city_info, cities)
        return city_data


class DataCalculationTask:

    def __init__(self):
        self.queue = Manager().Queue()
        self.dry_conditions = [
            "clear",
            "partly-cloudy",
            "cloudy",
            "overcast",
        ]

    @staticmethod
    def _calculate_avg_daily_temp(date_info: dict) -> int:
        date = date_info["date"]
        logger.info(f"Calculating an average temperature on {date}")
        total_temp = [
            hour["temp"]
            for hour in date_info["hours"]
            if int(hour["hour"]) in range(9, 20)
        ]
        avg_temp = None
        try:
            avg_temp = sum(total_temp) // len(total_temp)
        except ZeroDivisionError:
            logger.info(f"Not enough data for {date}")
        return avg_temp

    def _calculate_dry_hours(self, date_info: dict) -> int:
        date = date_info["date"]
        logger.info(
            f"Calculating the number of hours without precipitation on {date}"
        )
        num_hours = sum(
            1
            for hour in date_info["hours"]
            if int(hour["hour"]) in range(9, 20)
            and hour["condition"] in self.dry_conditions
        )
        return num_hours

    @staticmethod
    def _calculate_avgs(dates: list[DateForecast]) -> tuple[float, float]:
        logger.info(f"Calculating the averages")
        total_temp = []
        total_hours = []
        for date in dates:
            if date.avg_temp:
                total_temp.append(date.avg_temp)
                total_hours.append(date.dry_hours)

        avg_temp = round(sum(total_temp) / len(total_temp), 1)
        avg_num_hours = round(sum(total_hours) / len(total_hours), 1)

        return avg_temp, avg_num_hours

    # def _get_city_forecast(self, city_data: tuple[str, dict]) -> CityForecast:
    def _get_city_forecast(self, city_data: tuple[str, dict]):
        city_name = city_data[0]
        city_forecast = city_data[1]
        logger.info(f"Getting a forecast for {city_name}")
        dates = [
            DateForecast(
                date=date_info["date"],
                avg_temp=self._calculate_avg_daily_temp(date_info),
                dry_hours=self._calculate_dry_hours(date_info),
            )
            for date_info in city_forecast
        ]
        avg_temp, avg_num_hours = self._calculate_avgs(dates)
        # # faster
        # return CityForecast(
        #     name=city_name,
        #     dates=dates,
        #     avg_temp=avg_temp,
        #     avg_num_hours=avg_num_hours,
        # )
        self.queue.put(
            CityForecast(
                name=city_name,
                dates=dates,
                avg_temp=avg_temp,
                avg_num_hours=avg_num_hours,
            )
        )

    def get_city_forecasts(self, city_data: Iterable) -> list[CityForecast]:
        city_forecasts = []
        # processes = []
        # for data in city_data:
        #     process = Process(target=self._get_city_forecast, args=(data,))
        #     process.start()
        #     processes.append(process)
        # for process in processes:
        #     process.join()
        with Pool() as pool:
            for data in city_data:
                pool.apply_async(self._get_city_forecast, args=(data,))
            pool.close()
            pool.join()
        while not self.queue.empty():
            city_forecasts.append(self.queue.get())
        return city_forecasts


class DataAggregationTask:

    def __init__(self):
        self.table = {
            TableHeader.CITY.value: [],
            TableHeader.EMPTY.value: [],
            TableHeader.AVG.value: [],
            TableHeader.RATING.value: [],
        }

    def _create_table(self, city_forecast: CityForecast):
        self.table[TableHeader.CITY.value].extend([city_forecast.name, ""])
        self.table[TableHeader.EMPTY.value].extend(
            [TableRow.AVG_TEMP.value, TableRow.DRY_HOURS.value]
        )
        self.table[TableHeader.AVG.value].extend(
            [city_forecast.avg_temp, city_forecast.avg_num_hours]
        )
        self.table[TableHeader.RATING.value].extend([city_forecast.rating, ""])
        for i in range(len(city_forecast.dates)):
            _forecast_date = city_forecast.dates[i]
            if _forecast_date.date in self.table.keys():
                _forecast_date = city_forecast.dates[i]
                self.table[_forecast_date.date].extend(
                    [_forecast_date.avg_temp, _forecast_date.dry_hours]
                )
            else:
                self.table.update(
                    {
                        _forecast_date.date: [
                            _forecast_date.avg_temp,
                            _forecast_date.dry_hours,
                        ]
                    }
                )

    def create_table(self, city_forecasts: list[CityForecast]):
        list(map(self._create_table, city_forecasts))

    def _create_dataframe(self) -> DataFrame:
        return DataFrame.from_dict(self.table)

    def create_file(self, file_name: str):
        df = self._create_dataframe()
        columns = df.columns.tolist()
        columns.pop(2)
        columns.append(TableHeader.AVG.value)
        columns.pop(2)
        columns.append(TableHeader.RATING.value)
        df[columns].to_csv(file_name, index=False)


class DataAnalyzingTask:

    def __init__(self, data: list[CityForecast]):
        self.forecasts = data

    def _sort(self):
        return sorted(self.forecasts, reverse=True)

    def _calculate_rating(self) -> list[CityForecast]:
        for i, forecast in enumerate(self._sort(), 1):
            forecast.rating = i
        return self.forecasts

    def sort_by_rating(self):
        return sorted(self._calculate_rating(), key=lambda city: city.rating)

    def fav_city(self):
        _city = min(self.forecasts, key=lambda city: city.rating).name
        return f"The most favorable city to visit is {_city}"
