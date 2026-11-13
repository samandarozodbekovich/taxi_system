# Taxi System

A taxi ordering platform built on Telegram:

- **Client Mini App** - the client picks the pickup point and destination on a map, sees the price, and follows the driver live.
- **Client bot** - registration, opening the Mini App, order history, referral bonuses.
- **Driver bot + driver panel (Mini App)** - login, going online, receiving and accepting offers, trip status, balance, trip history.
- **Backend** - Django + DRF + Channels (WebSocket) + Celery, PostgreSQL/PostGIS, Redis.

## How an order flows

1. The client orders in the Mini App → `POST /api/orders/create/` returns immediately.
2. Celery (`dispatch_new_order`) finds the 5 nearest online drivers (PostGIS + one OSRM table request), creates offers (`OrderDispatch`) and sends them a Telegram message. A wave whose radius holds nobody new widens at once (3 → 5 → 8 → 12 km); only if nobody is within 12 km (e.g. locations unknown) does every online driver get the offer. When the offers expire (`DRIVER_OFFER_TIMEOUT_SECONDS`) or all of those drivers reject, the next wave goes to drivers not offered yet, with a wider radius (3 → 5 → 8 → 12 km).
3. The driver accepts in the panel (only offered drivers can) → `ACCEPTED` → `WAITING` → `IN_PROGRESS` → `COMPLETED`. The client sees each step and the driver's position over WebSocket.
4. On completion the commission is charged from the driver's wallet; the referral bonus is paid if this was an invited client's first trip.
5. If nobody accepts within `ORDER_SEARCH_TIMEOUT_SECONDS`, Celery marks the order `NO_DRIVER`.

## Project layout

```
backend/            Django project (config/ = settings, urls, asgi, celery)
  apps/clients/     clients, Telegram initData auth
  apps/drivers/     drivers, token auth, driver panel
  apps/orders/      orders, status machine, dispatch, WebSocket consumer, Celery tasks
  apps/dispatch/    order offers to drivers
  apps/wallet/      driver wallets and transactions
  apps/referrals/   referral bonuses
  apps/settings_app/ admin-editable settings (prices, commission, ...)
  services/         OSRM routing
  templates/        client Mini App, driver panel, admin
bots/client_bot/    client Telegram bot (aiogram)
bots/driver_bot/    driver Telegram bot (aiogram)
```

Code convention: one class or function per file, grouped in folders by kind (`views/`, `functions/`, `serializers/`, `authentication/`, `permissions/`, `mixins/`, `tasks/`, `tests/`). Each folder's `__init__.py` re-exports its contents.

## Running locally

Requirements: Python 3.12, PostgreSQL 16 with PostGIS, Redis, and on Windows GDAL from [OSGeo4W](https://trac.osgeo.org/osgeo4w/) in `C:\OSGeo4W` (the path is set in `settings.py`).

```bash
python -m venv venv
venv\Scripts\activate            # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt

# Settings: copy the examples and fill them in
copy backend\.env.example backend\.env
copy bots\client_bot\.env.example bots\client_bot\.env
copy bots\driver_bot\.env.example bots\driver_bot\.env

cd backend
python manage.py migrate
python manage.py createsuperuser
```

Run each in its own terminal (Redis must be running):

```bash
# backend (HTTP + WebSocket)
cd backend && daphne -b 0.0.0.0 -p 8000 config.asgi:application

# Celery worker (offers, Telegram notifications, search timeout)
cd backend && celery -A config worker --loglevel=info -P eventlet -c 1000   # -P eventlet on Windows only

# bots
cd bots/client_bot && python main.py
cd bots/driver_bot && python main.py
```

Telegram Mini Apps need HTTPS - for local development expose port 8000 with ngrok and put the ngrok domain in `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `DRIVER_WEBAPP_URL` and the client bot's `WEBAPP_URL`.

## Tests

```bash
cd backend
python manage.py test
```

Tests need PostgreSQL (a temporary test database is created), not Redis.

## Docker

```bash
docker compose --env-file backend/.env up -d --build
```

Starts PostGIS, Redis, the backend (migrations run on start), the Celery worker and both bots. Inside Docker the database and Redis hosts are set automatically (`db`, `redis`); the bots reach the backend at `http://backend:8000`.

Caddy sits in front on ports 80/443: it gets a Let's Encrypt certificate for `DOMAIN` (point the domain's DNS at the server first), redirects HTTP to HTTPS, adds HSTS, proxies HTTP and WebSocket to the backend and serves uploaded files from `/media/`. Port 8000 is bound to `127.0.0.1` only. Without `DOMAIN` it serves `https://localhost` with a self-signed certificate.

## Production checklist

- `DJANGO_DEBUG=False`, a strong `DJANGO_SECRET_KEY`, a real `DB_PASSWORD`.
- `DOMAIN`, `DJANGO_ALLOWED_HOSTS` / `DJANGO_CSRF_TRUSTED_ORIGINS` = your domain (`DJANGO_NUM_PROXIES=1` is set by Docker Compose; set it yourself behind any other proxy).
- Restrict `YANDEX_FRONTEND_MAP_KEY` to your domain (HTTP Referer) in the Yandex developer console.
- Run your own OSRM (the public demo server forbids production use):

  ```bash
  # in a folder with uzbekistan-latest.osm.pbf from download.geofabrik.de/asia
  docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-extract -p /opt/car.lua /data/uzbekistan-latest.osm.pbf
  docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-partition /data/uzbekistan-latest.osrm
  docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-customize /data/uzbekistan-latest.osrm
  docker run -d -p 5000:5000 -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-routed --algorithm mld /data/uzbekistan-latest.osrm
  ```

  then set `OSRM_BASE_URL=http://localhost:5000`.
- Don't log full URLs at the proxy: the order WebSocket carries initData/tokens in the query string.

## Admin tasks

- **Approve drivers** - Drivers → select → "Approve selected drivers". New drivers can't log in or get orders until approved.
- **Top up / fine a driver** - Wallet transactions → Add → `TOPUP` / `PENALTY`. Balances can only change through transactions, so every change is logged.
- **Settings** (System settings, key → value):

| Key | Default | Meaning |
|---|---|---|
| `MIN_PRICE` | 5000 | Base fare (UZS) |
| `PRICE_PER_KM` | 2000 | Price per km |
| `FREE_WAITING_TIME` | 3 | Free waiting minutes |
| `WAITING_PRICE_PER_MINUTE` | 500 | Price per paid waiting minute |
| `COMMISSION_PERCENT` | 10 | Commission charged from the driver |
| `ORDER_SEARCH_TIMEOUT_SECONDS` | 180 | Search time before `NO_DRIVER` |
| `DRIVER_OFFER_TIMEOUT_SECONDS` | 45 | Time a driver has to answer an offer (also the panel timer) |
| `REFERRAL_BONUS` | 5000 | Bonus for an invited client's first trip |

## API

Authentication: client - `Authorization: tma <initData>` (Mini App) or `X-Bot-Secret` + `client_telegram_id` (client bot); driver bot - `X-Bot-Secret`, then `Authorization: Bearer <token>` from login; driver panel - the HttpOnly `driver_token` cookie set by login (the token never reaches JavaScript), plus `X-Requested-With: driver-panel` on changing requests (CSRF). WebSockets are accepted only from pages on `DJANGO_ALLOWED_HOSTS`.

| Method | Path | Who | What |
|---|---|---|---|
| POST | `/api/orders/route/` | client | Route and price between two points (60/min per client) |
| POST | `/api/orders/create/` | client | Create an order |
| GET | `/api/orders/active/` | client | Current order |
| GET | `/api/orders/history/` | client | Latest orders |
| POST | `/api/orders/<id>/cancel/` | client | Cancel own order |
| GET | `/api/clients/bonus/` | client | Bonus balance and referral code |
| GET | `/api/clients/check/<tg_id>/` | client bot | Look up a client |
| POST | `/api/clients/register/` | client bot | Register a client |
| POST | `/api/drivers/register/` | driver bot | Driver registration (needs admin approval) |
| POST | `/api/drivers/login/` | anyone | Driver login → token (lockout per code + Telegram user / IP) |
| POST | `/api/drivers/logout/` | driver | End every session (bot and panel) |
| GET | `/api/drivers/me/` | driver | Profile and current status |
| POST | `/api/drivers/<id>/status/` | driver | Online / offline |
| POST | `/api/drivers/<id>/location/` | driver | GPS position |
| GET | `/api/orders/available/` | driver | Open offers |
| GET | `/api/orders/<id>/detail/` | driver | Offered / own order details |
| POST | `/api/orders/<id>/action/` | driver | `accept`, `reject`, `arrive`, `start`, `complete`, `cancel` |
| GET | `/api/orders/driver/active/` | driver | Current trip |
| GET | `/api/orders/driver/history/` | driver | Latest trips |
| GET | `/api/wallet/info/` | driver | Balance and totals |
| WS | `/ws/order/<id>/?tma=<initData>` | client | Live order status and driver position |
| WS | `/ws/order/<id>/` + `driver_token` cookie | driver | Live status of the driver's current order |
