from flask import Flask, jsonify, request
from datetime import datetime
from pytz import timezone
from dateutil.relativedelta import relativedelta

app = Flask(__name__)


@app.route("/", methods=["GET"])
def main_page():
    return "Привет, GitHub!"


# инф. о городе по его id
def get_city_info(geonameid=None):
    if not geonameid:
        return "Не указан идентификатор города", 400
    with open("RU.txt", "r") as f:
        for line in f:
            fields = line.split("\t")
            if fields[0] == geonameid:
                return fields
    return None


# поиск и ввод в массив заданного количества городов
def get_cities(num):
    cities = []
    with open("RU.txt", "r") as f:
        for i, line in enumerate(f):
            if i >= num:
                break
            fields = line.split("\t")
            cities.append(fields)
    return cities


# инф. о городе с наибольшим населением по русскому названию
def get_city_info_by_name(name):
    with open("RU.txt", "r", encoding="utf8") as f:
        highest_pop_city = {}
        for line in f:
            fields = line.split("\t")
            names = fields[3].split(",")
            for n in names:
                if n.strip() == name:
                    population = int(fields[14])
                    if name in highest_pop_city:
                        if population > int(highest_pop_city[name][14]):
                            highest_pop_city[name] = fields
                    else:
                        highest_pop_city[name] = fields
    return highest_pop_city.get(name)


# поиск наиболее северного города
def find_northernmost_city(city_info1, city_info2):
    latitude1 = float(city_info1[4])
    city1 = city_info1[1]
    latitude2 = float(city_info2[4])
    city2 = city_info2[1]
    if latitude1 > latitude2:
        return city1
    elif latitude2 > latitude1:
        return city2
    else:
        return "Both"


# сравнение временных зон на совпадение
def compare_timezones_boolean(city_info1, city_info2):
    timezone1 = city_info1[17]
    timezone2 = city_info2[17]
    return timezone1 == timezone2


# сравнение временных зон по часам (на момент запуска сервера)
def compare_timezones_by_hours(city_info1, city_info2):
    timezone1 = city_info1[17]
    timezone2 = city_info2[17]
    utcnow = timezone("utc").localize(datetime.utcnow())
    place1 = utcnow.astimezone(timezone(f"{timezone1}")).replace(tzinfo=None)
    place2 = utcnow.astimezone(timezone(f"{timezone2}")).replace(tzinfo=None)

    offset = relativedelta(place1, place2)
    return offset.hours


# список возможных городов по частичному названию
def get_suggested_cities(partial_name):
    suggested_names = []
    with open("RU.txt", "r", encoding="utf8") as f:
        for line in f:
            fields = line.split("\t")
            names = fields[3].split(",")
            for name in names:
                if name.startswith(partial_name):
                    if name not in suggested_names:
                        suggested_names.append(name)
    return suggested_names


"""
инф. о городе через POST
(нужно отправить JSON на /city c параметром geonameid для ответа)
вывод в JSON
"""


@app.route("/city", methods=["POST"])
def get_city():
    data = request.get_json()
    geonameid = data.get("geonameid")
    city_info = get_city_info(geonameid)
    if city_info:
        return jsonify(city_info)
    else:
        return "Такого города нет", 404


# инф. о городе через GET, вывод JSON
@app.route("/city/<geonameid>", methods=["GET"])
def get_city_alt(geonameid):
    city_info = get_city_info(geonameid)
    if city_info:
        return jsonify(city_info)
    else:
        return "Такого города нет", 404


# вывод заданного кол-ва городов в JSON
@app.route("/filter", methods=["GET"])
def filter_cities_by_amount():
    num = request.args.get("amount")
    if not num:
        return "Не указан параметр amount. Пример: добавить ?amount=50 к URL", 400
    try:
        num = int(num)
    except (TypeError, ValueError):
        return "Неверный параметр amount", 400
    cities = get_cities(num)
    return jsonify(cities)


# вывод информации о двух городах в JSON
@app.route("/twocities", methods=["GET"])
def get_cities_by_name():
    city1 = request.args.get("city1")
    city2 = request.args.get("city2")
    if not city1 or not city2:
        return (
            "Не указаны имена городов. Пример: добавить ?city1=Томск&city2=Северск к URL",
            400,
        )
    city_info1 = get_city_info_by_name(city1)
    city_info2 = get_city_info_by_name(city2)

    if not city_info1 or not city_info2:
        return "Информация об одном или обоих городах не найдена", 404
    northernmost_city = find_northernmost_city(city_info1, city_info2)
    timezone_comparison = compare_timezones_boolean(city_info1, city_info2)
    time_difference = compare_timezones_by_hours(city_info1, city_info2)

    return jsonify(
        {
            "cities": [city_info1, city_info2],
            "northernmost_city": northernmost_city,
            "same_timezones": timezone_comparison,
            "time difference (h)": time_difference,
        }
    )


@app.route("/suggestions", methods=["GET"])
def display_suggestions():
    partial_name = request.args.get("name")
    if not partial_name:
        return "Не указано частичное название. Пример: добавить ?name=То к URL", 400
    suggested_names = get_suggested_cities(partial_name)

    return jsonify(suggested_names)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
