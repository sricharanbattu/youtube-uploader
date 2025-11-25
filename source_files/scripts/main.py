import sys
import os
import argparse
from ImageProcesser.image_resize import convert_image_for_youtube
from VideoGenerate.video_generate import create_video
from YouTubeUpload.youtube_upload import upload_video
from SubtitleHandler.subtitle_autogen_downloader import get_autogen_subs
from Utilities.get_credentials import get_credentials
from Utilities.youtube_metadata_utilities import extract_metadata



def main():
    parser = argparse.ArgumentParser(description="Upload a video to YouTube with metadata.")
    parser.add_argument("song_name", help="The name of the video upload, to help with data and output paths.")
    parser.add_argument("audio_file_name", help="Name of the  audio file (e.g., input.mp3)")
    parser.add_argument("image_file_name", help="Name of the image file (e.g., input.jpg)")
    parser.add_argument("metadata_file_name", help="Name of the json meta data file for youtube upload (e.g., video_metadata.json)")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    rel_data_dir = os.path.join(script_dir, '..', 'data', args.song_name)
    rel_output_dir = os.path.join(script_dir, '..', 'output', args.song_name)
    os.makedirs(rel_output_dir, exist_ok=True)
    base_audio_name = os.path.splitext(os.path.basename(args.audio_file_name))[0]
    base_image_name = os.path.splitext(os.path.basename(args.image_file_name))[0]

    # Set full paths for input data
    args.input_audio_file = os.path.join(rel_data_dir, args.audio_file_name)
    args.input_image_file = os.path.join(rel_data_dir, args.image_file_name)
    args.input_metadata_file = os.path.join(rel_data_dir, args.metadata_file_name)

    # Set full paths for output data
    output_image_name = f"{base_image_name}_yt.jpg"
    args.output_image_file = os.path.join(rel_output_dir, output_image_name )
    
    output_video_name = f"{base_audio_name}.mp4"
    output_video_file = os.path.join(rel_output_dir, output_video_name)
    downloaded_captions_file = os.path.join(rel_output_dir, f"{base_audio_name}_downloaded_captions.srt")


    # Step 1: Convert image for YouTube
    convert_image_for_youtube(input_image=args.input_image_file, output_image=args.output_image_file)
    # Step 2: Create video from image and audio
    create_video(image_path=args.output_image_file, audio_path=args.input_audio_file, output_path=output_video_file, extra_seconds=2)
    # Step 3: Upload video to YouTube
    creds = get_credentials()
    metadata = extract_metadata(metadata_file=args.input_metadata_file, data_rel_dir=rel_data_dir)
    response = upload_video(video_path=output_video_file, metadata=metadata, creds=creds)


    # Step 4: Download auto-generated subtitles
    if response and "id" in response:
        video_id = response["id"]
        get_autogen_subs(creds, video_id=video_id, language="te", output_file=downloaded_captions_file, metadata=metadata)
    else:
        print("Video upload failed; skipping subtitle download.")

    


if __name__ == "__main__":
   ''' try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
    '''
   main()