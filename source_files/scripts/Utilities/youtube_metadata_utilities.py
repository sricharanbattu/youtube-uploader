import os
import json
from datetime import datetime
import pytz  # install with: pip install pytz









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
        "defaultAudioLanguage": metadata.get("defaultAudioLanguage")
    }

