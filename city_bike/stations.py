#!/usr/bin/env python3

from requests import get, Session, HTTPError
from math import sqrt
from dataclasses import dataclass
from functools import reduce


class Station:
    def __init__(self, station_information):
        '''
            Turn station information into Station object
        '''

        for key, value in station_information.items():
            exec(f"self.{key} = value")

    def update(self, status):
        ''' 
            Update all relevant values, with overwrite
        '''
        for key, value in status.items():
            exec(f"self.{key} = value")

    def update_distance(self, location):

        user_latitude, user_longitude = location
        station_latitude, station_longitude = self.lat, self.lon

        # Because coordinates are non-linear, there are small inaccuracies
        # but these are within a reasonable margin of error
        latitudinal_distance = user_latitude - station_latitude
        longitudinal_distance = user_longitude - station_longitude

        distance = sqrt(latitudinal_distance**2 + longitudinal_distance**2)

        self.distance = distance

    def __str__(self):
        name, distance = self.name, self.distance
        bikes, parking = self.num_bikes_available, self.num_docks_available

        there_are_bikes = bikes > 0
        there_is_parking = parking > 0

        bike_message, bike_icon = f' 🚲 {bikes:02d}', '✅' if there_are_bikes else f'❌'
        park_message, park_icon = f'🅿️ {parking:02d}', '✅' if there_is_parking else '❌'

        return '\n'.join((name, bike_message, bike_icon, park_message, park_icon))

    def __repr__(self):

        return f"{self.__dict__}"

    def format(self):
        return str(self).split('\n')


class CityBikeApiConnection():
    '''
        Connection object to Oslo city bike APIs
    '''
    headers = {'Client-Identifier': 'dizz90-city_bike.py'}
    base_url = 'https://gbfs.urbansharing.com/oslobysykkel.no'

    def __init__(self, logger=None):
        self.session = Session()
        if logger is not None:
            self.logger = logger

    def _get_by_api_suburi(self, api: str) -> list:
        '''
            Shared GET and error handling
        '''
        api = f'{self.base_url}{api}'
        try:
            response = self.session.get(api, headers=self.headers)
            response.raise_for_status()
        except HTTPError as e:
            if self.logger is not None:
                self.logger.error(e.with_traceback)

            print(e.with_traceback)
        return response.json()['data']['stations']

    def get_station_information(self) -> list:
        '''
            Information about stations that doesn't change as often
            https://github.com/NABSA/gbfs/blob/master/gbfs.md#station_informationjson
        '''
        return self._get_by_api_suburi('/station_information.json')

    def get_status(self) -> list:
        '''
            Current status of station
            https://github.com/NABSA/gbfs/blob/master/gbfs.md#station_statusjson
        '''
        return self._get_by_api_suburi('/station_status.json')


class Stations():
    '''
        Represents all city bike stations
    '''

    def __init__(self):

        self.connection = CityBikeApiConnection()
        self.stations = []
        self._update_station_information()

    def _update_station_information(self) -> None:
        '''
            Populate stations from API

        '''
        station_information = self.connection.get_station_information()
        for information in station_information:
            self.stations.append(Station(information))

        self.refresh((0, 0))

    def _sort_by_distance(self, location: tuple):
        self.stations = sorted(self.stations, key=lambda s: s.distance)

    def refresh(self, location: tuple):
        '''
            Update bike availability realtime data
        '''
        statuses = self.connection.get_status()

        for status in statuses:
            station = self.get_station_by_id(status['station_id'])
            if station:
                station.update(status)
                station.update_distance(location)

        self._sort_by_distance(location)

    def get_station_by_id(self, identifier) -> Station:
        '''
            Finds the station that has that id
        '''
        def has_same_id(x): return x.station_id == identifier
        stations_with_same_id = tuple(filter(has_same_id, self.stations))

        assert len(stations_with_same_id) == 1

        return stations_with_same_id[0]

    def format_stations(self) -> str:
        '''

        '''
        messages = [station.format() for station in self.stations]

        def flatten(l): return [item for sublist in l for item in sublist]

        return messages

    def get_stations(self, location: tuple):
        '''
            Sort and return
        '''

        self.refresh(location)

        return self.format_stations()


if __name__ == "__main__":
    sts = Stations()
    loc = 59.913547, 10.755817
    stations = sts.get_stations(loc)
    for st in stations[0:6]:
        print(st)
    for s in sts.stations[0:3]:
        print(repr(s))
