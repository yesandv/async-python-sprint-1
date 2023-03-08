from enum import Enum

from pydantic import BaseModel


class DateForecast(BaseModel):
    date: str
    avg_temp: int | None
    dry_hours: int | None


class CityForecast(BaseModel):
    name: str
    dates: list[DateForecast] | None
    avg_temp: float | None
    avg_num_hours: float | None
    rating: int | None

    def __lt__(self, other):
        return (self.avg_temp, self.avg_num_hours) < (other.avg_temp, other.avg_num_hours)


class TableHeader(Enum):
    CITY = "Город/день"
    EMPTY = ""
    AVG = "Среднее"
    RATING = "Рейтинг"


class TableRow(Enum):
    AVG_TEMP = "Температура, среднее"
    DRY_HOURS = "Без осадков, часов"
