#!/usr/bin/env python3

'''
    city_bikes.py web interface

    Webapp to show city bikes sorted by location

'''

from city_bike import app

from flask import Flask, jsonify, render_template, url_for, redirect
from city_bike.stations import Stations


def get_location():
    '''
        Placeholder function for geolocation:

        Can be replaced with gmaps, or mozilla navigator geolocation API
    '''
    return 59.913547, 10.755817  # Origo

@app.route('/')
def show_bikes():
    '''
        Render a site with a list of all bike stations and their availability
    '''
    location = get_location()
    all_stations = Stations(logger=app.logger)

    stations = all_stations.get_stations(location)

    return render_template('show_bikes.html', data=stations)


if __name__ == '__main__':
    app.run()
