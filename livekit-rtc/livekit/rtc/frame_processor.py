from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Union
from .audio_frame import AudioFrame
from .video_frame import VideoFrame


T = TypeVar("T", bound=Union[AudioFrame, VideoFrame])


class FrameProcessor(Generic[T], ABC):
    @property
    @abstractmethod
    def enabled(self) -> bool: ...

    @enabled.setter
    @abstractmethod
    def enabled(self, value: bool) -> None: ...

    def _on_stream_info_updated(
        self,
        *,
        room_name: str,
        participant_identity: str,
        publication_sid: str,
    ) -> None: ...

    def _on_credentials_updated(self, *, token: str, url: str) -> None: ...

    @abstractmethod
    def _process(self, frame: T) -> T: ...

    @abstractmethod
    def _close(self) -> None: ...
