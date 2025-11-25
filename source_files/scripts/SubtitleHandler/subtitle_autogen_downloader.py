import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

from Utilities.get_credentials import get_credentials
from Utilities.youtube_set_get import set_video_privacy_status, get_video_privacy_status
from Utilities.youtube_metadata_utilities import extract_metadata


# Assume you've already set up OAuth2 credentials with youtube.force-ssl scope
default_creds = get_credentials()
default_youtube = build("youtube", "v3", credentials=default_creds)

# -------------------------------
# Transcript Polling (youtube-transcript-api)
# -------------------------------
def poll_for_autogen_transcript(video_id, language="te", max_wait=600, interval=30):
    waited = 0

    while waited < max_wait:
        try:
            transcripts = YouTubeTranscriptApi().list(video_id=video_id)
            transcript = transcripts.find_generated_transcript([language]).fetch()
            print("Transcript found!")
            return transcript
        except Exception as e:
            print(f"No transcript yet ({e}), waiting {interval}s...")
            time.sleep(interval)
            waited += interval
    print("Timed out waiting for transcript.")
    return None
# -------------------------------
# Save Transcript to SRT
# -------------------------------
def save_transcript_as_srt(transcript, output_file="captions.srt"):
    """
    Save transcript entries into an SRT file.
    """
    def format_time(seconds):
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{hrs:02}:{mins:02}:{secs:02},{ms:03}"

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            for i, entry in enumerate(transcript, start=1):
                # Use attributes instead of dict keys
                start_time = format_time(entry.start)
                end_time = format_time(entry.start + entry.duration)
                text = entry.text
                f.write(f"{i}\n{start_time} --> {end_time}\n{text}\n\n")
        print(f"Transcript saved to {output_file}")
    except Exception as e:
        print(f"Error saving transcript: {e}")
# -------------------------------
# Orchestrator
# -------------------------------
def get_autogen_subs(creds, video_id, language="te", output_file="captions.srt", metadata=None):
    """
    Orchestrates privacy toggle and transcript fetching for a given video ID.
    """
    youtube = build("youtube", "v3", credentials=creds)
    scheduleTime = metadata.get("publishAt") if metadata else None
    

    # Step 1: Set video to unlisted to allow transcript generation
    currentPrivacyStatus = get_video_privacy_status(video_id, youtube=youtube)
    if currentPrivacyStatus == "private":
        set_video_privacy_status(video_id, privacy_status="unlisted", youtube=youtube, publish_time=None)

    # Step 2: Poll for transcript
    transcript = poll_for_autogen_transcript(video_id, language=language)

    # Step 3: Save transcript if available
    if transcript:
        save_transcript_as_srt(transcript, output_file)
    else:
        print("No auto-generated transcript found or an error occurred.")

    # Step 4: Set video back to private (optionally schedule)
    set_video_privacy_status(video_id, privacy_status=currentPrivacyStatus, youtube=youtube, publish_time=scheduleTime)
