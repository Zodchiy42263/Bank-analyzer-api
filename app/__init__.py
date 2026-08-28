"""
Bank Analyzer — референс-бэкенд под фронтенд Bank-analyzer-ui.

Отдельный сервис/репозиторий. Отдаёт данные в ТОЧНО такой форме, какую ждут
компоненты фронта (см. README → «Контракт»). Схема PostgreSQL повторяет структуру
моков фронтенда, поэтому графики работают без единой правки в UI.

Эндпоинты:
    GET  /api/accounts
    POST /api/account
    GET  /api/overview/balance
    GET  /api/overview/charts?period=<D|N|M|K|G|V>
    GET  /api/health
"""
import os

from flask import Flask, jsonify
from dotenv import load_dotenv

from app.extensions import db
from app.routes import BLUEPRINTS

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.secret_key = "your-secret-key"
    app.json.sort_keys = False
    
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/bank",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)


    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app
