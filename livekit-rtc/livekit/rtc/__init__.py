# Copyright 2023 LiveKit, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""LiveKit SDK for Python
`pip install livekit`

See https://docs.livekit.io/home/client/connect/#installing-the-livekit-sdk for more information.
"""

from ._proto import stats_pb2 as stats
from ._proto.e2ee_pb2 import EncryptionState, EncryptionType
from ._proto.participant_pb2 import ParticipantKind, DisconnectReason
from ._proto.room_pb2 import (
    ConnectionQuality,
    ConnectionState,
    ContinualGatheringPolicy,
    DataPacketKind,
    IceServer,
    IceTransportType,
    TrackPublishOptions,
    VideoEncoding,
)
from ._proto.track_pb2 import (
    StreamState,
    TrackKind,
    TrackSource,
    ParticipantTrackPermission,
)
from ._proto.video_frame_pb2 import VideoBufferType, VideoCodec, VideoRotation
from .audio_frame import AudioFrame
from .audio_source import AudioSource
from .audio_stream import AudioFrameEvent, AudioStream, NoiseCancellationOptions
from .audio_filter import AudioFilter
from .e2ee import (
    E2EEManager,
    E2EEOptions,
    FrameCryptor,
    KeyProvider,
    KeyProviderOptions,
)
from .participant import (
    LocalParticipant,
    Participant,
    RemoteParticipant,
)
from .room import (
    ConnectError,
    DataPacket,
    Room,
    RoomOptions,
    RtcConfiguration,
    SipDTMF,
    RtcStats,
)
from .track import (
    AudioTrack,
    LocalAudioTrack,
    LocalTrack,
    LocalVideoTrack,
    RemoteAudioTrack,
    RemoteTrack,
    RemoteVideoTrack,
    Track,
    VideoTrack,
)
from .event_emitter import EventEmitter
from .track_publication import (
    LocalTrackPublication,
    RemoteTrackPublication,
    TrackPublication,
)
from .transcription import Transcription, TranscriptionSegment
from .version import __version__
from .video_frame import (
    VideoFrame,
)
from .video_source import VideoSource
from .video_stream import VideoFrameEvent, VideoStream
from .audio_resampler import AudioResampler, AudioResamplerQuality
from .audio_mixer import AudioMixer
from .apm import AudioProcessingModule
from .utils import combine_audio_frames
from .rpc import RpcError, RpcInvocationData
from .synchronizer import AVSynchronizer
from .data_stream import (
    TextStreamInfo,
    ByteStreamInfo,
    TextStreamReader,
    TextStreamWriter,
    ByteStreamWriter,
    ByteStreamReader,
)

__all__ = [
    "ConnectionQuality",
    "ConnectionState",
    "DataPacketKind",
    "TrackPublishOptions",
    "IceTransportType",
    "ContinualGatheringPolicy",
    "IceServer",
    "EncryptionType",
    "EncryptionState",
    "StreamState",
    "TrackKind",
    "TrackSource",
    "ParticipantTrackPermission",
    "VideoBufferType",
    "VideoRotation",
    "stats",
    "AudioFrame",
    "AudioSource",
    "AudioStream",
    "NoiseCancellationOptions",
    "AudioFilter",
    "AudioFrameEvent",
    "LocalParticipant",
    "Participant",
    "ParticipantKind",
    "DisconnectReason",
    "RemoteParticipant",
    "ConnectError",
    "Room",
    "RoomOptions",
    "RtcConfiguration",
    "SipDTMF",
    "RtcStats",
    "DataPacket",
    "LocalAudioTrack",
    "LocalVideoTrack",
    "RemoteAudioTrack",
    "RemoteVideoTrack",
    "Track",
    "LocalTrack",
    "RemoteTrack",
    "AudioTrack",
    "VideoTrack",
    "E2EEManager",
    "E2EEOptions",
    "KeyProviderOptions",
    "KeyProvider",
    "FrameCryptor",
    "LocalTrackPublication",
    "RemoteTrackPublication",
    "TrackPublication",
    "Transcription",
    "TranscriptionSegment",
    "VideoCodec",
    "VideoEncoding",
    "VideoFrame",
    "VideoFrameEvent",
    "VideoSource",
    "VideoStream",
    "AudioMixer",
    "AudioResampler",
    "AudioResamplerQuality",
    "RpcError",
    "RpcInvocationData",
    "EventEmitter",
    "combine_audio_frames",
    "AVSynchronizer",
    "TextStreamInfo",
    "ByteStreamInfo",
    "TextStreamReader",
    "TextStreamWriter",
    "ByteStreamReader",
    "ByteStreamWriter",
    "AudioProcessingModule",
    "__version__",
]
