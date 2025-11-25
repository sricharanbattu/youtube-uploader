import os
import google.genai as genai
from SubtitleHandler.validate_generated_subtitlefile import clean_and_validate_srt

def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def generate_subtitles_with_model(
    model_name,
    srt_file,
    lyrics_file,
    prompt_file,
    output_file="final_subs.srt"
):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY in your environment first")

    client = genai.Client(api_key=api_key)

    # Validate chosen model
    '''available_models = {m.name: m.supported_actions for m in client.models.list()}
    if model_name not in available_models:
        raise ValueError(f"Model '{model_name}' not found. Available models: {list(available_models.keys())}")

    if "generateContent" not in available_models[model_name]:
        raise ValueError(f"Model '{model_name}' does not support generateContent. Supported actions: {available_models[model_name]}")
    '''
    print(f"Using model: {model_name}")

    # Load inputs
    srt_text = load_file(srt_file)
    print("Loaded SRT file.")
    lyrics_text = load_file(lyrics_file)
    print("Loaded lyrics file.")
    prompt_text = load_file(prompt_file)
    print("Loaded prompt file.")

    # Build full prompt
    full_prompt = f"""
You are a subtitle generator. Follow these rules:
{prompt_text}

Inputs:
1. Original auto-generated Telugu SRT:
{srt_text}

2. Lyrics with English meaning:
{lyrics_text}

Task:
- Create a new SRT file.
- Each block should contain one lyric (merge/split smartly).
- Include IAST transcription + English meaning.
- Remove bogus entries like [music], [aaa].
- Output must be valid SRT format.
    """
    print("Generated full prompt for Gemini.")
    # Call Gemini
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=full_prompt
        )
    except Exception as e:
        raise RuntimeError(f"Error generating subtitles: {e}")

    raw_output = response.text
    validated_output = clean_and_validate_srt(raw_output)

    #Save the validated output
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(validated_output)

    print(f"Validated subtitles saved to {output_file}")

    


# Example usage
if __name__ == "__main__":
    generate_subtitles_with_model(
        model_name="models/gemini-2.5-flash",   # explicitly chosen model
        srt_file="auto_telugu.srt",
        lyrics_file="lyrics_meaning.txt",
        prompt_file="prompt_instructions.txt",
        output_file="iast_english_subs.srt"
    )
