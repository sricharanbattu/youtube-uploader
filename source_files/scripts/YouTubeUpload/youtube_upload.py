import os
import argparse


from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from Utilities.get_credentials import get_credentials
from Utilities.youtube_metadata_utilities import extract_metadata

# Scope defines the level of access we request.
# Here: permission to upload videos to YouTube.

# -------------------------------
# Upload Function
# -------------------------------
def upload_video(video_path, metadata, creds):
    """
    Uploads a video to YouTube using metadata.
    - Handles missing files and API errors gracefully
    - Supports scheduling via IST → UTC conversion
    - Supports setting default video language
    """
    
    #if not metadata:
    #    return

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
                "defaultAudioLanguage": metadata.get("defaultAudioLanguage")
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


    return response

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
    creds = get_credentials()
    metadata = extract_metadata(metadata_file=metadata_file, data_rel_dir=data_rel_dir)
    upload_video(video_path=video_path, metadata=metadata, creds=creds)
    #upload_video(video_path=video_path, metadata_file=metadata_file, data_rel_dir=data_rel_dir)