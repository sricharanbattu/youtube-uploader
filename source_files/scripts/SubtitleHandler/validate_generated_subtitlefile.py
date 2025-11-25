import re

def clean_and_validate_srt(raw_text):
    """
    Clean Gemini output and enforce valid SRT structure.
    """
    blocks = []
    current_index = 1

    # Split by double newlines (SRT block separator)
    raw_blocks = re.split(r"\n\s*\n", raw_text.strip())

    for block in raw_blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue

        # Remove bogus filler lines
        lines = [line for line in lines if not re.match(r"\[.*?\]", line)]

        # Skip empty after cleaning
        if not lines:
            continue

        # Ensure timestamp line exists
        timestamp_line = None
        text_lines = []
        for line in lines:
            if "-->" in line:
                timestamp_line = line
            else:
                text_lines.append(line)

        if not timestamp_line or not text_lines:
            continue

        # Validate timestamp format HH:MM:SS,mmm
        match = re.match(
            r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})",
            timestamp_line,
        )
        if not match:
            continue

        # Rebuild block with sequential index
        block_text = "\n".join(text_lines)
        blocks.append(f"{current_index}\n{timestamp_line}\n{block_text}\n")
        current_index += 1

    # Join blocks with double newlines
    return "\n".join(blocks)
