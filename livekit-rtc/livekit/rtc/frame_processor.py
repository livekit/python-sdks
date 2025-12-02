from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar, Union

if TYPE_CHECKING:
    from .audio_frame import AudioFrame
    from .video_frame import VideoFrame


T = TypeVar("T", bound=Union[AudioFrame, VideoFrame])


class SyncFrameProcessor(Generic[T], ABC):
    @property
    @abstractmethod
    def is_enabled(self) -> bool: ...

    @abstractmethod
    def set_enabled(self, enable: bool): ...

    @abstractmethod
    def _set_context(
        self,
        *,
        room_name: str,
        participant_identity: str,
        publication_sid: str,
    ): ...

    @abstractmethod
    def _process(self, frame: T) -> T: ...

    @abstractmethod
    def _close(self): ...
