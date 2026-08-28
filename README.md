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

Нужен **Python 3.10+** и запущенный сервер **PostgreSQL** (проще всего поднять
через Docker — см. шаг 1).

### 1. База данных через Docker (рекомендуется)

В репозитории есть `docker-compose.yml` с параметрами под строку подключения по
умолчанию, поэтому база `bank` создаётся сама и `.env` не нужен:

```bash
docker compose up -d      # поднять PostgreSQL (БД "bank" создаётся автоматически)
docker ps                 # у контейнера bank-pg статус должен стать healthy
```

Остановить — `docker compose down`, сбросить данные — `docker compose down -v`.
(Нужен установленный и запущенный Docker Desktop.)

### 2. Приложение на Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # активировать venv — слева появится "(.venv)"
pip install -r requirements.txt

python seed.py                 # создаёт таблицы и наполняет данными
python app.py                  # http://localhost:5000
```

Если PowerShell откажется выполнять скрипт активации
(`running scripts is disabled on this system`), разрешите скрипты для текущего
окна и повторите активацию:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

venv активируется только для текущего окна и не сохраняется между окнами — **в
каждом новом окне** перед `python ...` снова выполняйте
`.\.venv\Scripts\Activate.ps1` (в том числе там, где запущен `app.py`). В `cmd`
вместо этого: `.venv\Scripts\activate.bat`.

### 3. Приложение на Linux/macOS

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python seed.py
python app.py
```

Проверка (в отдельном окне):
`curl "http://localhost:5000/api/overview/charts?period=M"` (после `POST /api/account`)

### Своя база (без Docker)

Если поднимаете PostgreSQL сами, создайте базу `bank` и укажите строку
подключения через переменную окружения `DATABASE_URL` **до** запуска (файл
`.env` приложение само не читает):

```powershell
# Windows PowerShell
$env:DATABASE_URL = "postgresql+psycopg://postgres:ВАШ_ПАРОЛЬ@localhost:5432/bank"
```

```bash
# Linux/macOS
export DATABASE_URL="postgresql+psycopg://postgres:ВАШ_ПАРОЛЬ@localhost:5432/bank"
```

### Если что-то не запускается

- `ModuleNotFoundError: No module named 'flask'` — не активирован venv. Признак:
  в приглашении PowerShell нет префикса `(.venv)`. Выполните
  `.\.venv\Scripts\Activate.ps1` в этом окне.
- `404 user или period не найдены` — база пустая или сервер смотрит не в ту БД.
  Убедитесь, что контейнер поднят, и заново выполните `python seed.py` (он
  пересоздаёт таблицы). Пользователи нумеруются с `0`, как ждёт фронт.
- Ошибка подключения (`connection refused` / `password authentication failed`) —
  не запущен PostgreSQL или не совпадает пароль. Проверьте `docker ps` и
  `DATABASE_URL`.

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
  { "id": 0, "name": "Вы (Иван Соколов)", "initials": "ИС" }
]
```

Баланса здесь нет и не будет — таблица `accounts` его не хранит.

### `POST /api/account`

Кладёт выбранного пользователя в сессию. Первый запрос в цепочке.

```json
{ "account_id": 0 }
```

Ответ: `{ "status": "connected" }`

### `GET /api/overview/balance`

Второй запрос. Считает баланс и чистый баланс по таблицам с деньгами
и задолженностью (сейчас — заглушка `calc_balance` в
`app/routes/overviews.py`).

```json
{
  "balance": 482340.0,
  "netBalance": 467140.0
}
```

### `GET /api/overview/charts?period=<D|N|M|K|G|V>`

Третий запрос. Доходы, расходы и задолженность (то, что раньше жило
в блоке общего баланса) отдаются здесь, вместе с рядами графиков.
Баланс для разбивки активов берётся из расчёта баланса, а не из
данных аккаунта.

```json
{
  "period": "M",
  "datePrefix": "",
  "axis": ["1-5", "6-10", "11-15", "16-20", "21-25", "26-30"],
  "income": 178450.9,
  "expense": 129680.45,
  "debt": 15200.0,
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

Порядок запросов на фронте: `POST /api/account` → `GET /api/overview/balance`
→ `GET /api/overview/charts`.

Правила формы:

- `*Shape` — нормализованные ряды `0..1` (форма линии графика), длиной как `axis`.
- `*Max` — масштаб ряда в рублях; реальное значение точки = `shape[i] * max`.
- `period` — один из `D N M K G V` (день, неделя, месяц, квартал, год, весь период).
- Пользователь берётся из сессии (`POST /api/account`), а не из query-параметра.
- Все денежные числа отдавайте как **number**, не строкой. Из PostgreSQL
  `NUMERIC/Decimal` приводите к `float`, иначе `jsonify` вернёт строку и графики
  сломаются.
