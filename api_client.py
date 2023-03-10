import logging
import json
from http import HTTPStatus
from urllib.request import urlopen

import certifi

from utils import CITIES, ERR_MESSAGE_TEMPLATE

logger = logging.getLogger()


class YandexWeatherAPI:
    """
    Base class for requests
    """

    @staticmethod
    def _do_request(url: str) -> dict:
        """Base request method"""
        try:
            with urlopen(url, cafile=certifi.where()) as req:
                response = req.read().decode("utf-8")
                response = json.loads(response)
            if req.status != HTTPStatus.OK:
                raise Exception(
                    "Error while executing the request. {}: {}".format(
                        response.status, response.reason
                    )
                )
            return response
        except Exception as ex:
            logger.error(ex)
            raise Exception(ERR_MESSAGE_TEMPLATE)

    @staticmethod
    def _get_url_by_city_name(city_name: str) -> str:
        try:
            return CITIES[city_name]
        except KeyError:
            raise Exception("Please check that city {} exists".format(city_name))

    def get_forecasting(self, city_name: str) -> dict:
        """
        :param city_name: key as str
        :return: response data as json
        """
        city_url = self._get_url_by_city_name(city_name)
        return self._do_request(city_url)
