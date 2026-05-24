import psycopg2
import os
from flask import Flask, render_template
from dotenv import load_dotenv


DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg.connect(DATABASE_URL)
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template("index.html")


