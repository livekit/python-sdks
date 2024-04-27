from typing import List
from dataclasses import dataclass


@dataclass
class Transcription:
    participant_identity: str
    track_id: str
    segments: List["TranscriptionSegment"]
    language: str


@dataclass
class TranscriptionSegment:
    id: str
    text: str
    start_time: int
    end_time: int
    final: bool
