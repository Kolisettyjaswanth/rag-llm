from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Transcript:
    guest: str
    title: str
    youtube_url: str
    video_id: str
    publish_date: str
    description: str
    duration_seconds: float | None
    duration: str
    view_count: int | None
    channel: str
    keywords: list[str]
    transcript: str
    source_path: str


def load_transcript(file_path: Path) -> Transcript:
    content = file_path.read_text(encoding="utf-8")

    if not content.startswith("---"):
        raise ValueError(f"Missing YAML front matter: {file_path}")

    parts = content.split("---", 2)

    if len(parts) != 3:
        raise ValueError(f"Invalid transcript format: {file_path}")

    metadata = yaml.safe_load(parts[1]) or {}
    transcript_text = parts[2].strip()

    return Transcript(
        guest=str(metadata.get("guest", "")),
        title=str(metadata.get("title", "")),
        youtube_url=str(metadata.get("youtube_url", "")),
        video_id=str(metadata.get("video_id", "")),
        publish_date=str(metadata.get("publish_date", "")),
        description=str(metadata.get("description", "")),
        duration_seconds=(
            float(metadata["duration_seconds"])
            if metadata.get("duration_seconds") is not None
            else None
        ),
        duration=str(metadata.get("duration", "")),
        view_count=(
            int(metadata["view_count"])
            if metadata.get("view_count") is not None
            else None
        ),
        channel=str(metadata.get("channel", "")),
        keywords=[
            str(keyword)
            for keyword in metadata.get("keywords", [])
        ],
        transcript=transcript_text,
        source_path=str(file_path),
    )


def find_transcript_files(transcripts_root: Path) -> list[Path]:
    return sorted(transcripts_root.glob("episodes/*/transcript.md"))


def load_all_transcripts(transcripts_root: Path) -> list[Transcript]:
    return [
        load_transcript(file_path)
        for file_path in find_transcript_files(transcripts_root)
    ]