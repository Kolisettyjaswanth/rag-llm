import re


def clean_transcript(text: str) -> str:
    text = re.sub(r"\(\d{2}:\d{2}:\d{2}\)", "", text)

    lines = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        lines.append(line)

    return "\n".join(lines)