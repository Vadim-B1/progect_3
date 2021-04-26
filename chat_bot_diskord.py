# импортируем все необходимые библиотеки
from discord.ext import commands
import requests
import datetime


# определяем константы
TOKEN = token
KEY_YANDEX_POGODA = key
bot = commands.Bot(command_prefix='!#')
sp_use_cities = []


# функция для игры в города
def find_city(city):
    global sp_use_cities
    col = 0
    a = -1
    eror1 = 'Назовите другой город'
    find_gorod = False
    # проверяем введеный город на его существование
    with open('cities.txt', 'r', encoding="utf-8") as fl_ct:
        for line in fl_ct:
            if city.upper() in line.upper():
                find_gorod = True
    # выбираем город
    if find_gorod:
        if city not in sp_use_cities:
            bukv = list(city.upper())[a]
            while abs(a) < len(city):
                with open('cities.txt', 'r', encoding="utf-8") as fl_ct:
                    for line in fl_ct:
                        if line.startswith(bukv) and line.strip() not in sp_use_cities:
                            col = 1
                            sp_use_cities.append(line.strip())
                            sp_use_cities.append(city)
                            return line.strip()
                a -= 1
                if col == 0:
                    bukv = list(city.upper())[a]
            else:
                return 'Назовите другой город'
        else:
            return eror1
    else:
        return eror1 + '. Такого города нет'


# функция для определения погоды
def get_weather(city):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": '40d1649f-0493-4b70-98ba-98533de7710b',
        "geocode": city,
        "format": "json"}
    response1 = requests.get(geocoder_api_server, params=geocoder_params).json()
    if len(response1["response"]["GeoObjectCollection"]["featureMember"]) > 0:
        sl = {'clear': 'ясно',
              'partly-cloudy': 'малооблачно',
              'cloudy': 'облачно с прояснениями',
              'overcast': 'пасмурно',
              'drizzle': 'морось',
              'light-rain': 'небольшой дождь',
              'rain': 'дождь',
              'moderate-rain': 'умеренно сильный дождь',
              'heavy-rain': 'сильный дождь',
              'continuous-heavy-rain': 'длительный сильный дождь',
              'showers': 'ливень',
              'wet-snow': 'дождь со снегом',
              'light-snow': 'небольшой снег',
              'snow': 'снег',
              'snow-showers': 'снегопад',
              'hail': 'град',
              'thunderstorm': 'гроза',
              'thunderstorm-with-rain': 'дождь с грозой',
              'thunderstorm-with-hail': 'гроза с градом'}
        toponym = response1["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        coords = toponym["Point"]["pos"].split(' ')
        weather_api_server = 'https://api.weather.yandex.ru/v1/forecast?'
        weather_params = {
            "lon": float(coords[0]),
            "lat": float(coords[1]),
            "lang": "ru_RU"}
        headers = {"X-Yandex-API-Key": KEY_YANDEX_POGODA}
        response = requests.get(weather_api_server, weather_params, headers=headers).json()
        fct = response["fact"]
        temperature = fct["temp"]
        tmpr_feels_like = fct["feels_like"]
        pressure = fct['pressure_mm']
        wind_speed = fct['wind_speed']
        wthr = fct['condition'].split('-and-')
        timestamp = fct['obs_time']
        time_now = datetime.datetime.fromtimestamp(timestamp)
        for i in range(len(wthr)):
            if wthr[i] in sl:
                wthr[i] = sl[wthr[i]]
        return f'''Температура воздуха в городе {city} {temperature}, ощущается как {tmpr_feels_like}.
Скорость ветра {wind_speed} м/с.
Давление {pressure} мм.
На улице {" и ".join(wthr)}.
Время измерений {time_now}'''
    else:
        return 'К сожалению информация об этом городе не найдена'


# функция возвращающая снимок области
def get_image(object, scale):
    geocoder_params = {
        "apikey": '40d1649f-0493-4b70-98ba-98533de7710b',
        "geocode": object,
        "format": "json"}
    rspns = requests.get("http://geocode-maps.yandex.ru/1.x/", params=geocoder_params).json()
    if len(rspns["response"]["GeoObjectCollection"]["featureMember"]) > 0:
        toponym = rspns["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        coords = toponym["Point"]["pos"].split(' ')
        return f"http://static-maps.yandex.ru/1.x/?ll={coords[0]},{coords[1]}&z={scale}&l=map"
    else:
        return 'Повторите попытку'


# бот игры в города
@bot.command(name='play_cities')
async def start_play_cities(ctx, city):
    await ctx.send(find_city(city))


# бот погоды
@bot.command(name='weather')
async def say_pogoda(ctx, city):
    await ctx.send(get_weather(city))


# бот снимка местности
@bot.command(name='picture')
async def see_map(ctx, city, scope):
    await ctx.send(get_image(city, scope))


# подключаем бота
bot.run(TOKEN)