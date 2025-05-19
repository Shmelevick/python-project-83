from flask import Flask
from dotenv import load_dotenv
import os

from .routes import routes

load_dotenv()  # Загружает переменные из .env в os.environ

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Явно задаём ключ
# Остальные переменные (например, DATABASE_URL) импортируются там, где нужны

app.register_blueprint(routes)

if __name__ == '__main__':
    app.run(debug=True)
