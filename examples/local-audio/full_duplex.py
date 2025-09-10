import os
import asyncio
import logging

from livekit import rtc


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    url = os.getenv("LIVEKIT_URL")
    token = os.getenv("LIVEKIT_TOKEN")
    if not url or not token:
        raise RuntimeError("LIVEKIT_URL and LIVEKIT_TOKEN must be set in env")

    room = rtc.Room()
    devices = rtc.MediaDevices()

    # Open microphone with AEC and prepare a player for remote audio feeding AEC reverse stream
    mic = devices.open_microphone(enable_aec=True)
    player = devices.open_output_player(apm_for_reverse=mic.apm)

    # Mixer for all remote audio streams
    mixer = rtc.AudioMixer(sample_rate=48000, num_channels=1)

    # Track stream bookkeeping for cleanup
    streams_by_pub: dict[str, rtc.AudioStream] = {}
    streams_by_participant: dict[str, set[rtc.AudioStream]] = {}

    async def _remove_stream(stream: rtc.AudioStream, participant_sid: str | None = None, pub_sid: str | None = None) -> None:
        try:
            mixer.remove_stream(stream)
        except Exception:
            pass
        try:
            await stream.aclose()
        except Exception:
            pass
        if participant_sid and participant_sid in streams_by_participant:
            streams_by_participant.get(participant_sid, set()).discard(stream)
            if not streams_by_participant.get(participant_sid):
                streams_by_participant.pop(participant_sid, None)
        if pub_sid is not None:
            streams_by_pub.pop(pub_sid, None)

    async def on_track_subscribed(track: rtc.Track, publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            stream = rtc.AudioStream(track, sample_rate=48000, num_channels=1)
            streams_by_pub[publication.sid] = stream
            streams_by_participant.setdefault(participant.sid, set()).add(stream)
            mixer.add_stream(stream)
            logging.info("subscribed to audio from %s", participant.identity)

    room.on("track_subscribed", on_track_subscribed)

    def on_track_unsubscribed(track: rtc.Track, publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
        stream = streams_by_pub.get(publication.sid)
        if stream is not None:
            asyncio.create_task(_remove_stream(stream, participant.sid, publication.sid))
            logging.info("unsubscribed from audio of %s", participant.identity)

    room.on("track_unsubscribed", on_track_unsubscribed)

    def on_track_unpublished(publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
        stream = streams_by_pub.get(publication.sid)
        if stream is not None:
            asyncio.create_task(_remove_stream(stream, participant.sid, publication.sid))
            logging.info("track unpublished: %s from %s", publication.sid, participant.identity)

    room.on("track_unpublished", on_track_unpublished)

    def on_participant_disconnected(participant: rtc.RemoteParticipant):
        streams = list(streams_by_participant.pop(participant.sid, set()))
        for stream in streams:
            # Best-effort discover publication sid
            pub_sid = None
            for k, v in list(streams_by_pub.items()):
                if v is stream:
                    pub_sid = k
                    break
            asyncio.create_task(_remove_stream(stream, participant.sid, pub_sid))
        logging.info("participant disconnected: %s", participant.identity)

    room.on("participant_disconnected", on_participant_disconnected)

    try:
        await room.connect(url, token)
        logging.info("connected to room %s", room.name)

        # Publish microphone
        track = rtc.LocalAudioTrack.create_audio_track("mic", mic.source)
        pub_opts = rtc.TrackPublishOptions()
        pub_opts.source = rtc.TrackSource.SOURCE_MICROPHONE
        await room.local_participant.publish_track(track, pub_opts)
        logging.info("published local microphone")

        # Start playing mixed remote audio
        asyncio.create_task(player.play(mixer))

        # Run until Ctrl+C
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        await mic.aclose()
        await mixer.aclose()
        await player.aclose()
        try:
            await room.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())


