# Flask-Geonames
Flask REST API service to provide information about cities from Geonames dump

## Data
RU.txt file from http://download.geonames.org/export/dump/RU.zip

## How to start
`python3 main.py`

## API
Methods collection is on https://api.postman.com/collections/24561193-a7bf5a2e-a0de-4187-bdd1-5490b9507dd8?access_key=PMAT-01GNE7GSW6V5MXHA9P5B9R0H07

## Methods
* get_city: http://localhost:8000/city, can be accessed via POST, JSON {"geonameid": "ID_here"}. Also GET: http://localhost:8000/city/geonameid.
* filter_cities_by_amount: http://localhost:8000/filter?amount=amount
* get_cities_by_name: http://localhost:8000/twocities?city1=city1&city2=city2, city names need to be in Russian
* display_suggestions: http://localhost:8000/suggestions?name=partial_name, partial name needs to be in Russian
