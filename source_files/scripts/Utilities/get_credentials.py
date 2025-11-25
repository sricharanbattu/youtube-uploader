import os
import google.auth.exceptions


from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scope defines the level of access we request.
# Here: permission to upload videos to YouTube.
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]

# -------------------------------
# Authentication
# -------------------------------
def get_credentials():
    """
    Handles authentication with Google OAuth.
    - Reuses token.json if available
    - Refreshes expired tokens
    - Falls back to browser login if needed
    """
    creds = None
    try:
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                print("🔄 Token refreshed")
            else:
                flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
                creds = flow.run_local_server(port=0)
                print("🌐 Logged in via browser")

            with open("token.json", "w") as token_file:
                token_file.write(creds.to_json())
                print("💾 token.json saved")

    except google.auth.exceptions.GoogleAuthError as e:
        print("❌ Authentication error:", e)
        return None

    return creds


