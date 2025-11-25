import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from Utilities.get_credentials import get_credentials
from Utilities.youtube_metadata_utilities import extract_metadata
from Utilities.get_credentials import set_video_privacy

# Assume you've already set up OAuth2 credentials with youtube.force-ssl scope
default_creds = get_credentials()
default_youtube = build("youtube", "v3", credentials=default_creds)

def poll_for_autogen_captions(video_id, language="te", max_wait=600, interval=30, youtube=default_youtube):
    """
    Poll until auto-generated captions are available.
    Returns caption_id if found, else None.
    """
    waited = 0
    try:
        while waited < max_wait:
            try:
                captions_list = youtube.captions().list(
                    part="snippet", videoId=video_id
                ).execute()
            except HttpError as e:
                print(f"API error while listing captions: {e}")
                return None

            print(captions_list)
            for item in captions_list.get("items", []):
                snippet = item.get("snippet", {})
                print(snippet.get("language"), snippet.get("trackKind"))
                if snippet.get("language") == language and snippet.get("trackKind") == "ASR":
                    print("Found auto-generated captions:", item["id"])
                    return item["id"]

            print(f"No auto-generated captions yet, waiting {interval}s...")
            time.sleep(interval)
            waited += interval

        print("Timed out waiting for auto-generated captions.")
        return None
    except Exception as e:
        print(f"Unexpected error while polling captions: {e}")
        return None

def download_captions(caption_id, output_file="captions.srt", youtube=default_youtube):
    """
    Download captions by caption_id and save to file.
    """
    try:
        caption_request = youtube.captions().download(id=caption_id)
        caption_response = caption_request.execute()

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(caption_response)

        print(f"Captions saved to {output_file}")
    except HttpError as e:
        print(f"API error while downloading captions: {e}")
    except IOError as e:
        print(f"File write error: {e}")
    except Exception as e:
        print(f"Unexpected error while downloading captions: {e}")

def get_autogen_subs(creds, video_id, language="te", output_file="captions.srt", scheduleTime=None):
    #your_credentials = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)
    """
    Orchestrates polling and downloading auto-generated captions for a given video ID.
    """
    #set you tube privacyStatus to unlisted to enable caption download
    set_video_privacy(video_id, privacy_status="unlisted", youtube=youtube, publish_time=None)

    caption_id = poll_for_autogen_captions(video_id, language=language, youtube=youtube)
    if caption_id:
        download_captions(caption_id, output_file, youtube=youtube)
    else:
        print("No auto-generated captions found or an error occurred.")

    set_video_privacy(video_id, privacy_status="private", youtube=youtube, publish_time=scheduleTime)
