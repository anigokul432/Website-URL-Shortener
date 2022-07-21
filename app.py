from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import string
import random
import math

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACL_MODIFICATIONS'] = False

db = SQLAlchemy(app)

maxShortLen = 3

class Urls(db.Model):
    id_ = db.Column("id_", db.Integer, primary_key=True)
    long = db.Column("long", db.String())
    short = db.Column("short", db.String(maxShortLen))

    def __init__(self, long, short):
        self.long = long
        self.short = short

@app.before_first_request
def create_tables():
    db.create_all()

def shorten_url():
    allLetters = string.ascii_lowercase + string.ascii_uppercase
    iterations = math.floor(math.pow(len(allLetters), maxShortLen))
    for i in range(iterations):
        rand_letters = ""
        for j in range(maxShortLen): rand_letters += random.choice(allLetters)
        short_url = Urls.query.filter_by(short=rand_letters).first()
        if not short_url:
            return rand_letters
    # if no unique short is found     
    return None

@app.route('/', methods=['POST','GET'])
def home():
    if request.method == "POST":
        url_received = request.form["nm"]
        usr_received = request.form["usr"]

        # Perform query to see if long url already exists in database
        found_url = Urls.query.filter_by(long=url_received).first()
        if found_url:
            # return corresponding short
            return redirect(url_for("display_short_url", url=found_url.short))
        else:
            # create short url randomly or let user define it
            short_url = shorten_url()
            if usr_received:
                short_url = usr_received
            # add to database
            new_url = Urls(url_received, short_url)
            db.session.add(new_url)
            db.session.commit()
            return redirect(url_for("display_short_url", url=short_url))
    else:
        return render_template("home.html")

@app.route('/display/<url>')
def display_short_url(url):
    return render_template('shorturl.html', short_url_display=url)

@app.route('/<short_url>')
def redirection(short_url):
    long_url = Urls.query.filter_by(short=short_url).first()
    if long_url:
        return redirect(long_url.long)
    else:
        return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

if __name__ == '__main__':
    app.run(port=5000, debug=True)
