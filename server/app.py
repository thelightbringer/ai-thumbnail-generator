import os
from flask import Flask, session, request, redirect, jsonify
from flask_session import Session
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.environ.get(
    "GOOGLE_REDIRECT_URI", "http://localhost:5000/oauth2callback"
)


def credentials_to_dict(creds: Credentials):
    return {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }


def get_flow(state=None):
    return Flow(
        client_config={
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        state=state,
        redirect_uri=REDIRECT_URI,
    )


def get_service():
    if "credentials" not in session:
        return None
    creds = Credentials(**session["credentials"])
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        session["credentials"] = credentials_to_dict(creds)
    return build("gmail", "v1", credentials=creds)


@app.route("/auth-url")
def auth_url():
    flow = get_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )
    session["state"] = state
    return jsonify({"auth_url": authorization_url})


@app.route("/oauth2callback")
def oauth2callback():
    state = session.get("state")
    flow = get_flow(state=state)
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    session["credentials"] = credentials_to_dict(creds)
    return redirect("/")


@app.route("/messages/search", methods=["POST"])
def search_messages():
    service = get_service()
    if not service:
        return jsonify({"error": "Unauthorized"}), 401
    query = request.json.get("query", "")
    result = service.users().messages().list(userId="me", q=query).execute()
    messages = []
    for msg in result.get("messages", []):
        m = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=msg["id"],
                format="metadata",
                metadataHeaders=["Subject", "From", "Date"],
            )
            .execute()
        )
        headers = {h["name"]: h["value"] for h in m["payload"].get("headers", [])}
        messages.append(
            {
                "id": m["id"],
                "subject": headers.get("Subject", ""),
                "from": headers.get("From", ""),
                "date": headers.get("Date", ""),
            }
        )
    return jsonify({"messages": messages})


@app.route("/messages/delete", methods=["POST"])
def delete_messages():
    service = get_service()
    if not service:
        return jsonify({"error": "Unauthorized"}), 401
    ids = request.json.get("ids", [])
    if ids:
        service.users().messages().batchDelete(
            userId="me", body={"ids": ids}
        ).execute()
    return jsonify({"status": "deleted", "count": len(ids)})


@app.route("/messages/archive", methods=["POST"])
def archive_messages():
    service = get_service()
    if not service:
        return jsonify({"error": "Unauthorized"}), 401
    ids = request.json.get("ids", [])
    if ids:
        service.users().messages().batchModify(
            userId="me", body={"ids": ids, "removeLabelIds": ["INBOX"]}
        ).execute()
    return jsonify({"status": "archived", "count": len(ids)})


@app.route("/messages/group", methods=["POST"])
def group_messages():
    service = get_service()
    if not service:
        return jsonify({"error": "Unauthorized"}), 401
    query = request.json.get("query", "")
    group_by = request.json.get("group_by", "from")
    result = service.users().messages().list(userId="me", q=query).execute()
    groups = {}
    for msg in result.get("messages", []):
        m = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=msg["id"],
                format="metadata",
                metadataHeaders=["Subject", "From", "Date"],
            )
            .execute()
        )
        headers = {h["name"]: h["value"] for h in m["payload"].get("headers", [])}
        key = headers.get({"from": "From", "date": "Date", "subject": "Subject"}[group_by], "")
        groups.setdefault(key, []).append(
            {
                "id": m["id"],
                "subject": headers.get("Subject", ""),
                "from": headers.get("From", ""),
                "date": headers.get("Date", ""),
            }
        )
    return jsonify(groups)


if __name__ == "__main__":
    app.run(debug=True)

