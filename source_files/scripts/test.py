import sys
import os
import google.genai as genai
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))





def test_get_captions_autogen():
    
    from Utilities.get_credentials import get_credentials
    from SubtitleHandler.subtitle_autogen_downloader import get_autogen_subs
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

def test_gemini_prompt():
    from Utilities.gemini_utilities import getGeminiApiKey

    client = genai.Client(api_key=getGeminiApiKey())

    for m in client.models.list():
        print(m.name, m.supported_actions)
    # Example call
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello Gemini, test prompt"
    )

    print("Gemini Response:", response.text)

def test_subtitle_generation():
    from SubtitleHandler.subtitle_generator import generate_subtitles_with_model

    model_name = "gemini-2.5-flash"
    srt_file = "data/test/captions.srt"
    lyrics_file = "data/test/english_for_telugu_lyrics.txt"
    prompt_file = "data/test/subtitle_generator_prompt.txt"
    output_file = "data/test/test_final_subs.srt"

    # Ensure previous test file is removed
    if os.path.exists(output_file):
        os.remove(output_file)

    generate_subtitles_with_model(
        model_name=model_name,
        srt_file=srt_file,
        lyrics_file=lyrics_file,
        prompt_file=prompt_file,
        output_file=output_file
    )

    # Check if the output file was created
    assert os.path.exists(output_file), "Final subtitle file was not created."

    # Optionally, check if the file is not empty
    assert os.path.getsize(output_file) > 0, "Final subtitle file is empty."

    # Clean up test file
    #os.remove(output_file)

if __name__ == "__main__":
    #test_get_captions_autogen()
    #test_gemini_prompt()
    test_subtitle_generation()
    print("All tests passed.")