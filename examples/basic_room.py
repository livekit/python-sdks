"""
LiveKit Basic Room Example

This example demonstrates connecting to a LiveKit room with audio capabilities.
It supports two audio modes:

1. PlatformAudio Mode (--platform-audio, RECOMMENDED):
   - Uses WebRTC's Audio Device Module (ADM) for microphone capture
   - Built-in echo cancellation (AEC), noise suppression (NS), auto gain control (AGC)
   - Automatic speaker playout for received audio
   - No external audio libraries needed
   - Cannot access raw audio frames (ADM sends directly to WebRTC)

2. Synthetic Mode (default, for advanced use):
   - Manual audio frame capture via AudioSource.capture_frame()
   - Requires external audio libraries (e.g., sounddevice, pyaudio)
   - Full control over audio processing pipeline
   - Access to raw audio frames for custom processing
   - No built-in AEC/NS/AGC - must implement yourself or use AudioProcessingModule
   - Must handle speaker playout manually

Usage:
    # List available audio devices
    python basic_room.py --list-devices

    # Connect with PlatformAudio (recommended)
    python basic_room.py --platform-audio --room my-room

    # Connect with PlatformAudio and specific devices
    python basic_room.py --platform-audio --mic-id "device-guid" --speaker-id "device-guid"

    # Publish a WAV file instead of microphone
    python basic_room.py --file audio.wav --room my-room

    # Publish both microphone and WAV file
    python basic_room.py --platform-audio --file audio.wav --room my-room

Environment variables:
    LIVEKIT_URL - LiveKit server URL (e.g., ws://localhost:7880)
    LIVEKIT_API_KEY - API key for token generation
    LIVEKIT_API_SECRET - API secret for token generation
"""

import argparse
import asyncio
import logging
import os
import struct
import wave
from signal import SIGINT, SIGTERM
from typing import Optional

from livekit import api, rtc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="LiveKit Basic Room Example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List available audio devices and exit",
    )

    parser.add_argument(
        "--platform-audio",
        action="store_true",
        help="Use PlatformAudio (WebRTC ADM) for microphone capture. "
        "Provides built-in AEC, NS, AGC. Recommended for most use cases.",
    )

    parser.add_argument(
        "--file",
        type=str,
        metavar="WAV_PATH",
        help="Publish audio from a WAV file. Can be combined with --platform-audio "
        "to publish both microphone and file audio.",
    )

    parser.add_argument(
        "--room",
        type=str,
        default="my-room",
        help="Room name to join (default: my-room)",
    )

    parser.add_argument(
        "--mic-id",
        type=str,
        metavar="DEVICE_ID",
        help="Select microphone by device ID (from --list-devices). "
        "Only used with --platform-audio.",
    )

    parser.add_argument(
        "--speaker-id",
        type=str,
        metavar="DEVICE_ID",
        help="Select speaker by device ID (from --list-devices). Only used with --platform-audio.",
    )

    return parser.parse_args()


def list_audio_devices() -> None:
    """List available audio devices using PlatformAudio."""
    try:
        platform_audio = rtc.PlatformAudio()
    except rtc.PlatformAudioError as e:
        print(f"Failed to initialize PlatformAudio: {e}")
        return

    print("\nRecording devices (microphones):")
    recording_devices = platform_audio.recording_devices()
    if not recording_devices:
        print("  (none)")
    else:
        for device in recording_devices:
            print(f"  [{device.index}] {device.name}")
            print(f"      ID: {device.id}")

    print("\nPlayout devices (speakers):")
    playout_devices = platform_audio.playout_devices()
    if not playout_devices:
        print("  (none)")
    else:
        for device in playout_devices:
            print(f"  [{device.index}] {device.name}")
            print(f"      ID: {device.id}")

    print("\nUse --mic-id or --speaker-id with the device ID to select a specific device.")


def load_wav_file(path: str) -> tuple[bytes, int, int, int]:
    """Load a WAV file and return (samples, sample_rate, channels, bits_per_sample)."""
    with wave.open(path, "rb") as wav:
        sample_rate = wav.getframerate()
        channels = wav.getnchannels()
        bits_per_sample = wav.getsampwidth() * 8
        frames = wav.readframes(wav.getnframes())

        # Convert to 16-bit signed integers if needed
        if bits_per_sample == 8:
            # Convert unsigned 8-bit to signed 16-bit
            samples = struct.unpack(f"{len(frames)}B", frames)
            samples = [(s - 128) * 256 for s in samples]
            frames = struct.pack(f"{len(samples)}h", *samples)
            bits_per_sample = 16
        elif bits_per_sample == 24:
            # Convert 24-bit to 16-bit (drop lower 8 bits)
            samples = []
            for i in range(0, len(frames), 3):
                # 24-bit little-endian: sign-extend to 32-bit, then take upper 16 bits
                # If high bit (bit 23) is set, the sample is negative - extend with 0xFF
                sign_byte = b"\xff" if frames[i + 2] & 0x80 else b"\x00"
                sample = struct.unpack("<i", frames[i : i + 3] + sign_byte)[0] >> 8
                samples.append(sample)
            frames = struct.pack(f"{len(samples)}h", *samples)
            bits_per_sample = 16
        elif bits_per_sample == 32:
            # Convert 32-bit to 16-bit
            samples = struct.unpack(f"<{len(frames) // 4}i", frames)
            samples = [s >> 16 for s in samples]
            frames = struct.pack(f"{len(samples)}h", *samples)
            bits_per_sample = 16

        return frames, sample_rate, channels, bits_per_sample


async def publish_wav_file(room: rtc.Room, wav_path: str, running: asyncio.Event) -> None:
    """Publish audio from a WAV file using synthetic mode (AudioSource).

    This demonstrates synthetic mode where you manually push audio frames.
    Use this approach when you need to:
    - Process audio before publishing
    - Generate synthetic audio
    - Play audio files
    """
    logging.info(f"Loading WAV file: {wav_path}")
    try:
        audio_data, sample_rate, channels, _ = load_wav_file(wav_path)
    except Exception as e:
        logging.error(f"Failed to load WAV file: {e}")
        return

    logging.info(f"WAV file: {sample_rate}Hz, {channels} channels, {len(audio_data)} bytes")

    # Create AudioSource for synthetic mode
    # SYNTHETIC MODE LIMITATION: You must manually capture frames in a loop.
    # There is no built-in AEC/NS/AGC - audio is sent exactly as provided.
    source = rtc.AudioSource(
        sample_rate=sample_rate,
        num_channels=channels,
        queue_size_ms=100,  # Small queue for file playback
    )

    track = rtc.LocalAudioTrack.create_audio_track("audio-file", source)

    # Publish the track
    publication = await room.local_participant.publish_track(
        track,
        rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_UNKNOWN),
    )
    logging.info(f"Published file audio track: {publication.sid}")

    # Convert audio data to samples
    num_samples = len(audio_data) // 2  # 16-bit = 2 bytes per sample
    samples = list(struct.unpack(f"<{num_samples}h", audio_data))

    # Play audio in 10ms frames (standard WebRTC frame size)
    samples_per_frame = (sample_rate * channels) // 100  # 10ms worth of samples
    position = 0
    frame_count = 0

    logging.info("Starting WAV playback loop...")

    while running.is_set():
        # Get next frame of samples
        end = min(position + samples_per_frame, len(samples))
        frame_samples = samples[position:end]

        # Pad with silence if we don't have enough samples
        if len(frame_samples) < samples_per_frame:
            frame_samples = frame_samples + [0] * (samples_per_frame - len(frame_samples))

        # Create AudioFrame
        frame = rtc.AudioFrame(
            data=bytes(struct.pack(f"<{len(frame_samples)}h", *frame_samples)),
            sample_rate=sample_rate,
            num_channels=channels,
            samples_per_channel=samples_per_frame // channels,
        )

        # Capture frame (this queues it for sending)
        await source.capture_frame(frame)

        position += samples_per_frame
        frame_count += 1

        # Loop the file
        if position >= len(samples):
            position = 0
            logging.info("WAV file looping...")

        # Wait ~10ms before next frame
        await asyncio.sleep(0.01)

    logging.info(f"WAV playback stopped after {frame_count} frames")


async def main(room: rtc.Room, args: argparse.Namespace) -> None:
    running = asyncio.Event()
    running.set()

    # Setup room event handlers
    @room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant) -> None:
        logging.info(f"Participant connected: {participant.identity} ({participant.sid})")

    @room.on("participant_disconnected")
    def on_participant_disconnected(participant: rtc.RemoteParticipant) -> None:
        logging.info(f"Participant disconnected: {participant.identity}")

    @room.on("track_subscribed")
    def on_track_subscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ) -> None:
        logging.info(f"Track subscribed: {track.kind} from {participant.identity}")
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            # When using PlatformAudio, received audio is automatically played
            # through the selected speaker. No manual handling needed.
            #
            # For synthetic mode or custom processing, you would create an
            # AudioStream and iterate over frames:
            #   audio_stream = rtc.AudioStream(track)
            #   async for frame_event in audio_stream:
            #       process(frame_event.frame)
            logging.info("Audio track subscribed - audio will play through speaker")

    @room.on("track_unsubscribed")
    def on_track_unsubscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ) -> None:
        logging.info(f"Track unsubscribed: {track.kind} from {participant.identity}")

    @room.on("connection_state_changed")
    def on_connection_state_changed(state: rtc.ConnectionState) -> None:
        logging.info(f"Connection state: {state}")

    @room.on("disconnected")
    def on_disconnected() -> None:
        logging.info("Disconnected from room")
        running.clear()

    # Initialize PlatformAudio if requested
    platform_audio: Optional[rtc.PlatformAudio] = None
    if args.platform_audio:
        try:
            platform_audio = rtc.PlatformAudio()
            logging.info("PlatformAudio initialized")

            # Select microphone if specified
            if args.mic_id:
                try:
                    platform_audio.set_recording_device(args.mic_id)
                    logging.info(f"Selected microphone: {args.mic_id}")
                except rtc.PlatformAudioError as e:
                    logging.warning(f"Failed to select microphone: {e}")

            # Select speaker if specified
            if args.speaker_id:
                try:
                    platform_audio.set_playout_device(args.speaker_id)
                    logging.info(f"Selected speaker: {args.speaker_id}")
                except rtc.PlatformAudioError as e:
                    logging.warning(f"Failed to select speaker: {e}")

        except rtc.PlatformAudioError as e:
            logging.error(f"Failed to initialize PlatformAudio: {e}")
            logging.info("Falling back to no microphone capture")
            platform_audio = None

    # Generate access token
    token = (
        api.AccessToken()
        .with_identity("python-bot")
        .with_name("Python Bot")
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=args.room,
            )
        )
        .to_jwt()
    )

    # Connect to room
    url = os.getenv("LIVEKIT_URL")
    if not url:
        logging.error("LIVEKIT_URL environment variable not set")
        return

    logging.info(f"Connecting to room '{args.room}'...")
    await room.connect(url, token)
    logging.info(f"Connected to room: {room.name}")

    # Publish microphone using PlatformAudio
    if platform_audio:
        # PLATFORMAUDIO MODE: The ADM captures audio from the microphone and sends
        # it directly to WebRTC. You cannot access the raw audio frames.
        # Benefits: Built-in AEC, NS, AGC. Automatic speaker playout.
        source = platform_audio.create_audio_source(
            rtc.PlatformAudioOptions(
                echo_cancellation=True,
                noise_suppression=True,
                auto_gain_control=True,
            )
        )
        mic_track = rtc.LocalAudioTrack.create_audio_track("microphone", source)

        publication = await room.local_participant.publish_track(
            mic_track,
            rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE),
        )
        logging.info(f"Published microphone track: {publication.sid}")

    # Publish WAV file if specified
    wav_task: Optional[asyncio.Task] = None
    if args.file:
        wav_task = asyncio.create_task(publish_wav_file(room, args.file, running))

    # Keep running until disconnected
    logging.info("Listening for events... Press Ctrl+C to exit")
    await asyncio.sleep(2)
    await room.local_participant.publish_data("hello from python!")

    while running.is_set():
        await asyncio.sleep(1)

    # Cleanup
    if wav_task:
        wav_task.cancel()
        try:
            await wav_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("basic_room.log"),
            logging.StreamHandler(),
        ],
    )

    args = parse_args()

    # Handle --list-devices
    if args.list_devices:
        list_audio_devices()
        exit(0)

    # Validate arguments
    if args.mic_id and not args.platform_audio:
        logging.warning("--mic-id requires --platform-audio, ignoring")
    if args.speaker_id and not args.platform_audio:
        logging.warning("--speaker-id requires --platform-audio, ignoring")

    loop = asyncio.get_event_loop()
    room = rtc.Room(loop=loop)

    async def cleanup():
        await room.disconnect()
        loop.stop()

    asyncio.ensure_future(main(room, args))

    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, lambda: asyncio.ensure_future(cleanup()))

    try:
        loop.run_forever()
    finally:
        loop.close()
