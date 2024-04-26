from dataclasses import dataclass


@dataclass
class TranscriptionSegment:
    id: str
    text: str
    start_time: int
    end_time: int
    final: bool
