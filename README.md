# Bank Analyzer API

Референс-бэкенд для фронтенда **Bank-analyzer-ui**. Живёт отдельным
репозиторием/сервисом; фронт общается с ним только по HTTP и знает лишь его
базовый URL. Схема БД повторяет структуру моков фронта, поэтому графики работают
без правок в UI.

Используйте его как эталон, чтобы **подстроить ваши существующие эндпоинты под
контракт** ниже, либо запустите как есть.

## Стек

Flask + Flask-SQLAlchemy + PostgreSQL (драйвер psycopg 3).

## Запуск

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # пропишите DATABASE_URL
createdb bank                 # или создайте БД вручную
python seed.py                # создаёт таблицы и наполняет данными
python app.py                 # http://localhost:5000
```

Проверка: `curl "http://localhost:5000/api/overview?user=0&period=M"`

Порт 5000 совпадает с `server.proxy` во фронте (`vite.config.js`), поэтому в dev
фронт и бэк работают на одном origin и CORS не нужен. Если бэкенд крутится на
другом домене без прокси — раскомментируйте `flask-cors` в `requirements.txt` и
добавьте в `app.py`:

```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
```

## Контракт (это и есть «связка» с фронтом)

Единственное, что связывает два репозитория — форма ответов. Меняете бэкенд —
сохраняйте её, и фронт менять не придётся.

### `GET /api/accounts`

```json
[
  { "id": 0, "name": "Вы (Иван Соколов)", "initials": "ИС", "balance": 482340.0 }
]
```

### `GET /api/overview?user=<id>&period=<D|N|M|K|G|V>`

```json
{
  "period": "M",
  "datePrefix": "",
  "axis": ["1-5", "6-10", "11-15", "16-20", "21-25", "26-30"],
  "balance": 482340.0,
  "debt": 15200.0,
  "netBalance": 467140.0,
  "income": 178450.9,
  "expense": 129680.45,
  "incomeShape": [0.4, 0.62, 0.5, 0.78, 0.68, 0.9],
  "expenseShape": [0.5, 0.48, 0.58, 0.52, 0.6, 0.55],
  "debtShape": [0.4, 0.45, 0.5, 0.55, 0.6, 0.65],
  "incomeMax": 42000.0,
  "expenseMax": 33000.0,
  "debtMax": 20520.0,
  "assets": [
    { "label": "Вклады", "amount": 217053.0, "color": "hsl(150, 30%, 46%)" },
    { "label": "Дебетовые счета", "amount": 120585.0, "color": "hsl(95, 26%, 52%)" },
    { "label": "Инвестиции", "amount": 144702.0, "color": "hsl(210, 35%, 55%)" },
    { "label": "Кредиторская задолженность", "amount": 210000.0, "color": "hsl(8, 42%, 50%)" }
  ]
}
```

Правила формы:

- `*Shape` — нормализованные ряды `0..1` (форма линии графика), длиной как `axis`.
- `*Max` — масштаб ряда в рублях; реальное значение точки = `shape[i] * max`.
- `period` — один из `D N M K G V` (день, неделя, месяц, квартал, год, весь период).
- Все денежные числа отдавайте как **number**, не строкой. Из PostgreSQL
  `NUMERIC/Decimal` приводите к `float`, иначе `jsonify` вернёт строку и графики
  сломаются.
