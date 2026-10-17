from typing import List
from dataclasses import dataclass, field


@dataclass
class Transcription:
    participant_identity: str
    track_sid: str
    segments: List["TranscriptionSegment"]


@dataclass
class TranscriptionSegment:
    id: str
    text: str
    start_time: int
    end_time: int
    language: str
    final: bool
    words: List[dict] = field(default_factory=list)
