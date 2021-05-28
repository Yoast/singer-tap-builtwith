"""builtwith API Client."""  # noqa: WPS226
# -*- coding: utf-8 -*-

import logging
from datetime import date, datetime, timedelta
from typing import Callable, Generator, List, Union

import httpx
import singer
from dateutil.rrule import DAILY, rrule

from tap_builtwith.cleaners import CLEANERS

API_SCHEME: str = 'https://'
API_BASE_URL: str = 'api.builtwith.com'
API_TRENDS: str = '/trends/v6/api.json?'
API_KEY: str = 'KEY=:key:'
API_TECH: str = '&TECH=:tech:'
API_DATE: str = '&DATE=:date:'


class Builtwith(object):  # noqa: WPS230
    """Builtwith API Client."""

    def __init__(
        self,
        api_key: str,
        technologies: Union[List[str], str]
    ) -> None:  # noqa: DAR101
        """Initialize client.

        Arguments:
            api_key {str} -- builtwith API key
        """
        self.api_key: str = api_key
        self.logger: logging.Logger = singer.get_logger()
        self.client: httpx.Client = httpx.Client(http2=True)
        # Set plugin or plugins
        if isinstance(technologies, str):
            self.technologies = [technologies]
        else:
            self.technologies = technologies


    def trends(
        self,
        **kwargs: dict,
    ) -> Generator[dict, None, None]:
        """Get all trends from a technology from date.

        Raises:
                ValueError: When the parameter start_date is missing

        Yields:
                Generator[dict] --  Cleaned Trends Data
        """
        # Validate the start_date value exists
        start_date_input: str = str(kwargs.get('start_date', ''))

        # Validate if technology name exists
        self.logger.info(
                f'Technology : {self.technologies}'
            )

        if not start_date_input:
            raise ValueError('The parameter start_date is required.')

        cleaner: Callable = CLEANERS.get('trends', {})

        self._set_api_key()

        for tech in self.technologies:
        # Replace placeholder in reports path
            api_tech: str = API_TECH.replace(
                ':tech:',
                tech,
            )
            for date_day in self._start_days_till_yesterday(start_date_input):

                # Replace placeholder in reports path
                from_to_date: str = API_DATE.replace(
                    ':date:',
                    date_day,
                )
                
                url: str = (
                    f'{API_SCHEME}{API_BASE_URL}{API_TRENDS}'
                    f'{self.api_key_url}{from_to_date}{api_tech}'
                )


                # Make a call to the builtwith API
                response: httpx._models.Response = self.client.get(
                    url
                )

                # Raise error on 4xx and 5xxx
                response.raise_for_status()

                # Create dictionary from response
                response_data: dict = response.json()

                self.logger.info(
                    f'Streaming {tech} trends data from: {date_day}'
                )

                # Yield cleaned results
                yield cleaner(date_day, response_data, tech)

    def _set_api_key(
        self,
    ) -> None:
        # Replace apikey placeholder in API path
        api_key_url: str = API_KEY.replace(
            ':key:',
            self.api_key,
        )
        self.api_key_url = api_key_url

    def _start_days_till_yesterday(
        self,
        start_date: str,
    ) -> Generator:
        """Yield YYYY/MM/DD for every day until now.

        Arguments:
            start_date {str} -- Start date e.g. 2020-01-01

        Yields:
            Generator -- Every day until now.
        """
        # Parse input date
        year: int = int(start_date.split('-')[0])
        month: int = int(start_date.split('-')[1].lstrip())
        day: int = int(start_date.split('-')[2].lstrip())

        # Setup start period
        period: date = date(year, month, day)

        # Calculate yesterday's date
        yesterday = datetime.utcnow() - timedelta(days=1)

        # Setup itterator
        dates: rrule = rrule(
            freq=DAILY,
            dtstart=period,
            until=yesterday,
        )

        # Yield dates in YYYY-MM-DD format
        yield from (date_day.strftime('%Y-%m-%d') for date_day in dates)
