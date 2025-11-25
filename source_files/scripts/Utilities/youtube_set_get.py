import os
import json
import argparse
import google.auth.exceptions


from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from Utilities.get_credentials import get_credentials


# Assume you've already set up OAuth2 credentials with youtube.upload scope
default_creds = get_credentials()
default_youtube = build("youtube", "v3", credentials=default_creds)

def set_video_privacy_status(video_id, privacy_status="public", publish_time=None, youtube=default_youtube):
    """
    Change the privacy status of a YouTube video.
    
    :param video_id: The YouTube video ID
    :param privacy_status: 'public', 'unlisted', or 'private'
    :param publish_time: Optional ISO 8601 datetime string (e.g. '2025-11-25T15:00:00Z')
                         Only used when privacy_status='private' to schedule publishing.
    """
    try:
        status_body = {"privacyStatus": privacy_status}
        
        # If scheduling is requested while private, include publishAt
        if privacy_status == "private" and publish_time:
            status_body["publishAt"] = publish_time
        
        request = youtube.videos().update(
            part="status",
            body={
                "id": video_id,
                "status": status_body
            }
        )
        response = request.execute()
        print(f"Video {video_id} updated: privacy={privacy_status}, publishAt={publish_time}")
        return response
    except HttpError as e:
        print(f"API error while updating video privacy: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")



def get_video_privacy_status(video_id, youtube=default_youtube):
    try:
        request = youtube.videos().list(
            part="status",
            id=video_id
        )
        response = request.execute()
        if "items" in response and len(response["items"]) > 0:
            privacy_status = response["items"][0]["status"]["privacyStatus"]
            print(f"Video {video_id} privacy status: {privacy_status}")
            return privacy_status
        else:
            print("No video found with that ID.")
            return None
    except HttpError as e:
        print(f"API error: {e}")
        return None


def set_video_language(video_id, youtube= default_youtube, language_code="te", LanguageSettingType="defaultAudioLanguage"):
    """
    Set the default language of a YouTube video.
    
    :param video_id: The YouTube video ID
    :param language_code: The language code to set (e.g., 'te' for Telugu)
    :param LanguageSettingType: The type of language setting ('defaultAudioLanguage' or 'defaultLanguage')
    """
    try:
        # Retrieve the current snippet
        video_response = youtube.videos().list(
            part="snippet",
            id=video_id
        ).execute()

        if "items" not in video_response or len(video_response["items"]) == 0:
            print("No video found with that ID.")
            return None

        snippet = video_response["items"][0]["snippet"]

        # Update the language setting
        snippet[LanguageSettingType] = language_code

        # Update the video with the new snippet
        update_response = youtube.videos().update(
            part="snippet",
            body={
                "id": video_id,
                "snippet": snippet
            }
        ).execute()

        print(f"Video {video_id} updated: {LanguageSettingType}={language_code}")
        return update_response

    except HttpError as e:
        print(f"API error while updating video language: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def get_video_language(video_id, youtube=default_youtube, LanguageSettingType="defaultAudioLanguage"):
    try:
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()
        if "items" in response and len(response["items"]) > 0:
            snippet = response["items"][0]["snippet"]
            language_code = snippet.get(LanguageSettingType, None)
            print(f"Video {video_id} {LanguageSettingType}: {language_code}")
            return language_code
        else:
            print("No video found with that ID.")
            return None
    except HttpError as e:
        print(f"API error: {e}")
        return None
    


def upload_subtitles(video_id, srt_file, language="en", name="English Subtitles", creds=default_creds):
    """
    Upload an SRT subtitle file to YouTube for a given video ID.
    """
    #creds = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    # Prepare metadata for the caption track
    body = {
        "snippet": {
            "videoId": video_id,
            "language": language,
            "name": name,
            "isDraft": False
        }
    }

    # Upload the SRT file
    media = MediaFileUpload(srt_file, mimetype="application/octet-stream")

    media = MediaFileUpload(srt_file, mimetype="application/octet-stream")

    try:
        request = youtube.captions().insert(
            part="snippet",
            body=body,
            media_body=media
        )
        response = request.execute()
        print("Uploaded subtitles:", response)

    except HttpError as e:
        # API-specific errors
        print(f"HTTP error {e.resp.status}: {e.error_details if hasattr(e, 'error_details') else e}")
        if e.resp.status == 403:
            print("Check your API quota or OAuth scopes.")
        elif e.resp.status == 404:
            print("Video not found or you lack permission.")
        elif e.resp.status == 400:
            print("Bad request — check file format and metadata.")
    except FileNotFoundError:
        print(f"Subtitle file {srt_file} not found.")
    except Exception as e:
        # Catch-all for unexpected issues
        print(f"Unexpected error: {e}")

# Example usage
if __name__ == "__main__":
    upload_subtitles(
        video_id="YOUR_VIDEO_ID",
        srt_file="iast_english_subs.srt",
        language="te",
        name="Telugu + English Meaning"
    )
