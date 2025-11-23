import os
#from moviepy import editor
from moviepy.editor import ImageClip, AudioFileClip

def create_video(image_path, audio_path, output_path, extra_seconds=2):
    try:
        # Check if files exist
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Load audio
        try:
            audio_clip = AudioFileClip(audio_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load audio: {e}")

        # Load image and set duration
        try:
            image_clip = ImageClip(image_path).set_duration(audio_clip.duration + extra_seconds)
        except Exception as e:
            raise RuntimeError(f"Failed to load image: {e}")

        # Combine image and audio
        video_clip = image_clip.set_audio(audio_clip)

        # Export video
        try:
            video_clip.write_videofile(output_path, fps=24)
        except Exception as e:
            raise RuntimeError(f"Failed to write video: {e}")

        print(f"Video successfully created: {output_path}")

    except FileNotFoundError as fnf_error:
        print(f"File error: {fnf_error}")
    except RuntimeError as run_error:
        print(f"Processing error: {run_error}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Example usage
#create_video("input.jpg", "input.mp3", "output.mp4", extra_seconds=2)

def create_video_with_default_paths(video_dir, input_audio_file, input_image_file):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, '..', '..', 'data', video_dir)
    output_dir = os.path.join(base_dir, '..', '..', 'output', video_dir)
    os.makedirs(output_dir, exist_ok=True)
    input_audio_path = os.path.join(input_dir, input_audio_file)
    input_image_path = os.path.join(input_dir, input_image_file)

    base_name = os.path.splitext(os.path.basename(input_audio_file))[0]
    output_name = f"{base_name}.mp4"
    output_path = os.path.join(output_dir, output_name)
    create_video(input_image_path, input_audio_path, output_path, extra_seconds=2)

