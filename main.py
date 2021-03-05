import json
import os
import requests
from geopy import distance
import folium
from flask import Flask
from dotenv import load_dotenv


NEAREST_BARS_AMOUNT = 5


def fetch_coordinates(apikey, place):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    params = {"geocode": place, "apikey": apikey, "format": "json"}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    places_found = response.json()['response']['GeoObjectCollection']['featureMember']
    most_relevant = places_found[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def load_file(file):
    with open(file, "r", encoding="CP1251") as my_file:
        moscow_bars_json = my_file.read()
        return json.loads(moscow_bars_json)


def get_distance(place):
     return place['distance']


def get_roster_bars(moscow_bars, coordinates):
    roster_bars = []
    for bar in moscow_bars:
        roster_bars.append({
        'title' : bar['Name'],
        'longitude' : bar['Longitude_WGS84'],
        'latitude' : bar['Latitude_WGS84'],
        'distance' : distance.distance(coordinates, [bar['Latitude_WGS84'], bar['Longitude_WGS84']]). km
        })
    return roster_bars


def get_nearest_bars(roster_bars, key_sort, count): 
    nearest_bars = (sorted(roster_bars, key=key_sort))[:count]
    return nearest_bars
    
    
def generates_placemarks(nearest_bars, coordinates):
    mapping_place = folium.Map(
    location=coordinates,
    zoom_start=12,
    )
    folium.Marker([coordinates[0], coordinates[1]], popup='<i>Ваше местоположение</i>', icon=folium.Icon(color='red')).add_to(mapping_place)
    for bar in nearest_bars:
        bar_name = bar['title']
        folium.Marker([bar['latitude'], bar['longitude']], popup=f'<i>{bar_name}</i>', icon=folium.Icon(color='green')).add_to(mapping_place)  
    mapping_place.save('mapping_place.html')


def shows_map():
    with open('mapping_place.html') as file:
        return file.read()


def bars_search(read_file, coordinates):
    moscow_bars = load_file(read_file)
    roster_bars = get_roster_bars(moscow_bars, coordinates)
    nearest_bars = get_nearest_bars(roster_bars, get_distance, NEAREST_BARS_AMOUNT)
    generates_placemarks(nearest_bars, coordinates)


if __name__ == '__main__':
    load_dotenv()
    apikey = os.getenv('API_KEY')
    location = input('Где вы находитесь? ')
    lat, lon = fetch_coordinates(apikey, location)
    coordinates = lon, lat
    used_file = "data-2897-2019-01-22.json"
    
    bars_search(used_file, coordinates)

    app = Flask(__name__)
    app.add_url_rule('/', 'location_bar', shows_map)
    app.run('0.0.0.0')
