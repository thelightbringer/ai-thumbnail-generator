# Gmail Cleaning Tool Backend

This Flask application handles Gmail OAuth and provides endpoints to search,
delete, archive and group emails.

## Setup

```bash
cd server
pip install -r requirements.txt
flask run
```

Environment variables:
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI` (defaults to `http://localhost:5000/oauth2callback`)
- `SECRET_KEY` (any random string)

