# URL Shortener

A simple URL shortener built with Django. It supports random short codes, custom aliases, link expiry, click tracking, a stats page and a JSON API.

## Features

- Random 6-character short codes
- Custom aliases (3-32 characters: letters, numbers, `-`, `_`)
- Optional expiry: 1 hour, 1 day, 7 days or 30 days
- Click counting and last-click time
- Stats page for every link
- JSON API for creating links and reading stats, with an optional API key
- Django admin for managing links
- Expired links return `410 Gone`

## Requirements

- Python 3.10+
- Django (see `requirements.txt`)

## Setup

```
git clone https://github.com/engineer25joe/url_shortener.git
cd URLShortener

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.(This is only  valid on locaal machine if deploying to a server, you need to change the settings.py file and add your server host to the ALLOWED_HOSTS list  )

## Usage

| URL | What it does |
|-----|--------------|
| `/` | Shorten form and recent links |
| `/<code>` | Redirects to the destination and counts a click |
| `/stats/<code>` | Stats page for a link |
| `/admin/` | Admin site (log in with your superuser) |

## JSON API

### API key (optional)

Set the `SHORTENER_API_KEY` environment variable before starting the server to protect `POST /api/shorten`. Clients must then send the key in the `X-API-Key` header.

```
python -c "import secrets; print(secrets.token_urlsafe(32))"

set SHORTENER_API_KEY=your-key-here        # Windows cmd
# export SHORTENER_API_KEY=your-key-here   # macOS / Linux
python manage.py runserver
```

If the variable is not set, the API is open. This is convenient for local development, but always set it on a public server.

### Create a link

`POST /api/shorten`

Body (JSON):

| Field | Required | Description |
|-------|----------|-------------|
| `url` | yes | The http(s) URL to shorten |
| `alias` | no | Custom code, 3-32 characters (letters, numbers, `-`, `_`) |
| `expires` | no | One of `1h`, `1d`, `7d`, `30d`. Leave out for never |

Example:

```
curl -X POST http://127.0.0.1:8000/api/shorten \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key-here" \
  -d '{"url": "https://python.org", "alias": "pyorg", "expires": "1d"}'
```

Response `201 Created`:

```json
{
  "code": "pyorg",
  "short_url": "http://127.0.0.1:8000/pyorg",
  "url": "https://python.org",
  "clicks": 0,
  "created_at": "2026-10-22T12:00:00+00:00",
  "expires_at": "2026-10-23T12:00:00+00:00",
  "last_clicked": null,
  "expired": false
}
```

### Get link stats

`GET /api/links/<code>`

Returns the same object as above, or `404` if the code doesn't exist. No API key needed.

### Errors

| Status | Meaning |
|--------|---------|
| `400` | Invalid JSON or failed validation. Details are in `fields` |
| `401` | Missing or invalid API key (only when a key is configured) |
| `404` | Link not found |
| `405` | Wrong HTTP method |
| `409` | Alias was taken at the same moment |

Example validation error:

```json
{
  "error": "Validation failed.",
  "fields": {"alias": ["That alias is already taken."]}
}
```

## Project structure

```
URLShortener/
├── manage.py
├── requirements.txt
├── LICENSE
├── URLShortener/          # project settings and root URLs
└── links/                 # the app
    ├── models.py          # Link model
    ├── forms.py           # validation shared by web and API
    ├── views.py           # home, redirect, stats pages
    ├── api.py             # JSON API views
    ├── urls.py
    ├── admin.py
    └── templates/links/
        ├── home.html
        └── stats.html
```

## Notes

- Stats pages and `GET /api/links/<code>` are public. Anyone who knows a code can read its stats.
- The web form has no login or rate limit. Add them before exposing the site on the internet.
- This project uses development settings (`DEBUG = True`, SQLite). Change the settings before deploying publicly.

## License

MIT. See the `LICENSE` file.