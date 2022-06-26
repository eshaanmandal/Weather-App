from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import requests


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///city.db'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
db = SQLAlchemy(app)


url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=1abdc86acb461cba8ab8af0fb8d97a2e'


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<{self.name}>"


def isValid(city):
    return requests.get(url.format(city)).status_code == 200


def handle_post_requests():
    new_city = request.form.get('city')
    # Check if there is an input and the input is valid
    if len(new_city) > 0:
        if isValid(new_city):
            exists = City.query.filter_by(name= new_city).first()
            if exists is None:
                new_city_obj = City(name=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                flash('City Already Exists')
        else:
            flash('Invalid City name')

    else:
        flash('City added!')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        handle_post_requests()

    #cities = City.query.all()
    cities = City.query.all()
    weather_data = []
    for city in reversed(cities):
        req = requests.get(url.format(city.name))
        r = req.json()
        weather = {
            'city': city.name,
            'temperature': r['main']['temp'],
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon'],
            'feels_like': r['main']['feels_like'],
        }
        weather_data.append(weather)

    return render_template("home.html", weather_data=weather_data)


if __name__ == "__main__":
    app.run(debug=True)
