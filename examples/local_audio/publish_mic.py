"""
Publish microphone audio using PlatformAudio.

This example demonstrates:
- Using PlatformAudio for microphone capture with built-in voice processing (AEC, NS, AGC)
- Monitoring microphone dB levels via AudioStream
- Device enumeration and selection

Usage:
    python publish_mic.py
    python publish_mic.py --list-devices
    python publish_mic.py --mic-id "device-guid"
"""

import argparse
import asyncio
import logging
import os
import queue
import threading

try:
    from dotenv import find_dotenv, load_dotenv

    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False

from livekit import api, rtc

from db_meter import calculate_db_level, display_single_db_meter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish microphone using PlatformAudio")
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List available audio devices and exit",
    )
    parser.add_argument(
        "--mic-id",
        type=str,
        help="Select microphone by device ID (from --list-devices)",
    )
    return parser.parse_args()


def list_audio_devices() -> None:
    """List available audio devices using PlatformAudio."""
    try:
        platform_audio = rtc.PlatformAudio()
    except rtc.PlatformAudioError as e:
        print(f"Failed to initialize PlatformAudio: {e}")
        return

    try:
        print("\nRecording devices (microphones):")
        for device in platform_audio.recording_devices():
            print(f"  [{device.index}] {device.name}")
            print(f"      ID: {device.id}")

        print()
    finally:
        platform_audio.close()


async def main(args: argparse.Namespace) -> None:
    logging.basicConfig(level=logging.INFO)

    # Load environment variables from a .env file if present
    if HAS_DOTENV:
        load_dotenv(find_dotenv())

    url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    if not url or not api_key or not api_secret:
        raise RuntimeError(
            "LIVEKIT_URL and LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set in env"
        )

    # Initialize PlatformAudio for microphone capture
    # PlatformAudio provides built-in AEC, NS, and AGC
    try:
        platform_audio = rtc.PlatformAudio()
        logging.info("PlatformAudio initialized")
    except rtc.PlatformAudioError as e:
        logging.error(f"Failed to initialize PlatformAudio: {e}")
        return

    # Select microphone if specified
    if args.mic_id:
        try:
            platform_audio.set_recording_device(args.mic_id)
            logging.info(f"Selected microphone: {args.mic_id}")
        except rtc.PlatformAudioError as e:
            logging.warning(f"Failed to select microphone: {e}")

    room = rtc.Room()
    source = None

    # dB level monitoring
    mic_db_queue: queue.Queue[float] = queue.Queue()

    token = (
        api.AccessToken(api_key, api_secret)
        .with_identity("local-audio")
        .with_name("Local Audio")
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room="local-audio",
            )
        )
        .to_jwt()
    )

    try:
        await room.connect(url, token)
        logging.info("connected to room %s", room.name)

        # Create audio source with voice processing enabled
        source = platform_audio.create_audio_source(
            rtc.PlatformAudioOptions(
                echo_cancellation=True,
                noise_suppression=True,
                auto_gain_control=True,
            )
        )
        track = rtc.LocalAudioTrack.create_audio_track("mic", source)

        pub_opts = rtc.TrackPublishOptions()
        pub_opts.source = rtc.TrackSource.SOURCE_MICROPHONE
        await room.local_participant.publish_track(track, pub_opts)
        logging.info("published local microphone with PlatformAudio")

        # Start dB meter display in a separate thread
        meter_thread = threading.Thread(
            target=display_single_db_meter, args=(mic_db_queue, "Mic: "), daemon=True
        )
        meter_thread.start()

        # Monitor microphone dB levels via AudioStream
        async def monitor_mic_db():
            mic_stream = rtc.AudioStream(track, sample_rate=48000, num_channels=1)
            try:
                async for frame_event in mic_stream:
                    frame = frame_event.frame
                    # Convert frame data to list of samples
                    samples = list(frame.data)
                    db_level = calculate_db_level(samples)
                    # Update queue with latest value (non-blocking)
                    try:
                        mic_db_queue.put_nowait(db_level)
                    except queue.Full:
                        pass  # Drop if queue is full
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
            finally:
                await mic_stream.aclose()

        asyncio.create_task(monitor_mic_db())

        # Run until Ctrl+C
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        try:
            await room.disconnect()
        except Exception:
            pass
        # Clean up PlatformAudio resources
        if source is not None:
            source.close()
        platform_audio.close()


if __name__ == "__main__":
    args = parse_args()

    if args.list_devices:
        list_audio_devices()
    else:
        asyncio.run(main(args))
