import sys
import os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



from Utilities.get_credentials import get_credentials
from SubtitleHandler.subtitle_autogen_downloader import get_autogen_subs

def test_get_captions_autogen():
    

    creds = get_credentials()
    video_id = "5qGsfGZlRvk"  # Replace with a valid video ID that has auto-generated captions in 'te' language
    output_file = "test_captions.srt"

    # Ensure previous test file is removed
    if os.path.exists(output_file):
        os.remove(output_file)

    get_autogen_subs(creds, video_id=video_id, language='te', output_file=output_file)

    # Check if the output file was created
    assert os.path.exists(output_file), "Caption file was not created."

    # Optionally, check if the file is not empty
    assert os.path.getsize(output_file) > 0, "Caption file is empty."

    # Clean up test file
    #os.remove(output_file)

if __name__ == "__main__":
    test_get_captions_autogen()
    print("All tests passed.")