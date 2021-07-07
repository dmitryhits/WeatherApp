import bdb

import flask_sqlalchemy
from flask import Flask
from flask import render_template
from flask import request, redirect, url_for, flash
import requests
import sys
import os

WEATHER_KEY = os.environ['WEATHER_KEY']

app = Flask(__name__)
# Set the secret key to some random bytes. Keep this really secret!
# app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = flask_sqlalchemy.SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f'City of {self.name}'


db.create_all()


@app.route('/')
def index():
    cities = City.query.all()
    print(type(cities))
    cities_dict = {}
    for city in cities:
        print(type(city))
        print(f'name: {city.name}')
        print(f'id: {city.id}')
        weather = get_weather(city.name)
        cities_dict[city.id] = weather
    return render_template('index.html', cities=cities_dict)


def get_weather(cityname):
    weather_dict = {"degree": 0, "state": "", "city": cityname, "time": "day", "icon": "01d"}
    params = {'q': cityname,
              'appid': WEATHER_KEY}
    # print("requesting weather", params)
    r = requests.get("http://api.openweathermap.org/data/2.5/weather", params=params)
    print(r.status_code)
    print(r.json())
    if not r.status_code == 404:
        weather_dict["degree"] = round(r.json()['main']["temp"] - 273.15, 1)
        weather_dict["state"] = r.json()['weather'][0]["main"]
        weather_dict["icon"] = r.json()['weather'][0]["icon"]
        weather_dict["name"] = r.json()['name']

        return weather_dict
    else:
        return 404


@app.route('/add', methods=['GET', 'POST'])
def add_city():
    city_name = request.form['city_name']
    if get_weather(city_name) == 404:
        flash("The city doesn't exist!")
        # print(city_name)
        return redirect(url_for('index'))
    elif not City.query.filter_by(name=city_name).first():
        city = City(name=city_name)
        db.session.add(city)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        flash('The city has already been added to the list!')
        return redirect(url_for('index'))


@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    city = City.query.filter_by(id=city_id).first()
    db.session.delete(city)
    db.session.commit()
    return redirect(url_for('index'))


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
