from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Union
from .audio_frame import AudioFrame
from .video_frame import VideoFrame


T = TypeVar("T", bound=Union[AudioFrame, VideoFrame])


class FrameProcessor(Generic[T], ABC):
    @property
    @abstractmethod
    def is_enabled(self) -> bool: ...

    @abstractmethod
    def set_enabled(self, enable: bool): ...

    def _update_stream_info(
        self,
        *,
        room_name: str,
        participant_identity: str,
        publication_sid: str,
    ): ...

    def _update_credentials(self, *, token: str, url: str): ...

    @abstractmethod
    def _process(self, frame: T) -> T: ...

    @abstractmethod
    def _close(self): ...
