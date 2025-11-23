import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def test_auth():
    creds = None

    # 1. Check if token.json already exists
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # 2. If no valid credentials, go through OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired token
            creds.refresh(Request())
            print("🔄 Token refreshed from refresh_token")
        else:
            # First-time login via browser
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
            print("🌐 Logged in via browser")

        # Save credentials for next run
        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())
            print("💾 token.json saved")

    print("✅ Authentication successful!")
    print("Access token:", creds.token[:20] + "...")  # show only first part
    print("Refresh token available:", creds.refresh_token is not None)

if __name__ == "__main__":
    test_auth()
