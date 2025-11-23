import os
import json
import argparse
import google.auth.exceptions
from datetime import datetime
import pytz  # install with: pip install pytz

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Scope defines the level of access we request.
# Here: permission to upload videos to YouTube.
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

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

# -------------------------------
# Time Conversion
# -------------------------------
def convert_ist_to_utc(ist_time_str):
    """
    Convert IST datetime string (YYYY-MM-DDTHH:MM:SS) to UTC ISO 8601 format.
    Example: "2025-11-24T10:00:00" (IST) → "2025-11-24T04:30:00Z" (UTC)
    """
    try:
        ist = pytz.timezone("Asia/Kolkata")
        ist_dt = datetime.strptime(ist_time_str, "%Y-%m-%dT%H:%M:%S")
        ist_dt = ist.localize(ist_dt)
        utc_dt = ist_dt.astimezone(pytz.utc)
        return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        print("❌ Error converting IST to UTC:", e)
        return None

# -------------------------------
# Metadata Extraction
# -------------------------------
def extract_metadata(metadata_file, data_rel_dir):
    """
    Reads metadata from JSON file.
    - Supports external description file for long descriptions
    - Converts IST publish time to UTC if provided
    - Returns a dictionary with title, description, tags, categoryId, privacyStatus, publishAt, defaultLanguage
    """
    try:
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    except FileNotFoundError:
        print(f"❌ Metadata file {metadata_file} not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing metadata JSON: {e}")
        return None

    # Load description
    description = metadata.get("description", "")
    if "description_file" in metadata:
        try:
            with open(os.path.join(data_rel_dir, metadata["description_file"]), "r", encoding="utf-8") as desc_file:
                description = desc_file.read()
        except FileNotFoundError:
            print(f"⚠️ Description file {metadata['description_file']} not found. Using empty description.")
            description = ""

    # Handle IST scheduling
    publishAt = None
    if "publishAtIST" in metadata:
        publishAt = convert_ist_to_utc(metadata["publishAtIST"])

    return {
        "title": metadata.get("title", "Untitled Video"),
        "description": description,
        "tags": metadata.get("tags", []),
        "categoryId": metadata.get("categoryId", "22"),  # Default: People & Blogs
        "privacyStatus": metadata.get("privacyStatus", "private"),
        "publishAt": publishAt,
        "defaultLanguage": metadata.get("defaultLanguage")
    }

# -------------------------------
# Upload Function
# -------------------------------
def upload_video(video_path, metadata_file, data_rel_dir):
    """
    Uploads a video to YouTube using metadata.
    - Handles missing files and API errors gracefully
    - Supports scheduling via IST → UTC conversion
    - Supports setting default video language
    """
    metadata = extract_metadata(metadata_file, data_rel_dir)
    if not metadata:
        return

    creds = get_credentials()
    if not creds:
        return

    try:
        youtube = build("youtube", "v3", credentials=creds)

        # Build request body
        body = {
            "snippet": {
                "title": metadata["title"],
                "description": metadata["description"],
                "tags": metadata["tags"],
                "categoryId": metadata["categoryId"],
                "defaultLanguage": metadata.get("defaultLanguage")
            },
            "status": {
                "privacyStatus": metadata["privacyStatus"]
            }
        }

        # Add scheduling if publishAt is provided
        if metadata.get("publishAt"):
            body["status"]["publishAt"] = metadata["publishAt"]

        # Prepare upload request
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
        )

        # Execute upload
        response = request.execute()
        print("✅ Upload complete. Video ID:", response["id"])

    except FileNotFoundError:
        print(f"❌ Video file {video_path} not found.")
    except HttpError as e:
        print("❌ YouTube API error:", e)
    except Exception as e:
        print("❌ Unexpected error:", e)

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a video to YouTube with metadata.")
    parser.add_argument("song_name", help="Path to the song (e.g., output.mp4)")
    parser.add_argument("video_name", help="Path to the video file (e.g., output.mp4)")
    parser.add_argument("metadata_file_name", help="Path to the metadata JSON file (e.g., video_metadata.json)")
    args = parser.parse_args()

    output_rel_dir = os.path.join('..', '..', 'output', args.song_name)
    data_rel_dir = os.path.join('..', '..', 'data', args.song_name)
    video_path = os.path.join(output_rel_dir, args.video_name)
    metadata_file = os.path.join(data_rel_dir, args.metadata_file_name)
    upload_video(video_path=video_path, metadata_file=metadata_file, data_rel_dir=data_rel_dir)