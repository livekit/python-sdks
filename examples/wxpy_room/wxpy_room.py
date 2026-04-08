import asyncio
import configparser
import logging
import os
import threading

import numpy as np

# pip install wxPython
import wx
import wx.lib.newevent

from livekit import rtc

logger = logging.getLogger(__name__)

# Custom event for video frame updates (posted from async thread to wx main thread)
VideoFrameEvent, EVT_VIDEO_FRAME = wx.lib.newevent.NewEvent()
# Custom event for room state changes
RoomStateEvent, EVT_ROOM_STATE = wx.lib.newevent.NewEvent()
# Custom event for participant list updates (used to sync video grid)
ParticipantEvent, EVT_PARTICIPANT = wx.lib.newevent.NewEvent()
# Custom event for audio spectrum band updates
AudioBandsEvent, EVT_AUDIO_BANDS = wx.lib.newevent.NewEvent()
# Custom event for incoming chat messages
ChatMessageEvent, EVT_CHAT_MESSAGE = wx.lib.newevent.NewEvent()

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wxpy_room_cfg.ini")

CODEC_MAP = {
    "VP8": rtc.VideoCodec.VP8,
    "VP9": rtc.VideoCodec.VP9,
    "AV1": rtc.VideoCodec.AV1,
    "H264": rtc.VideoCodec.H264,
    #"H265": rtc.VideoCodec.H265,
}


class Configure:
    """Read and save room configuration from wxpy_room_cfg.ini."""

    SECTION = "room"

    DEFAULTS = {
        "url": "ws://localhost:7880",
        "token": "",
        "e2ee_enabled": "false",
        "e2ee_key": "",
        "simulcast_enabled": "false",
        "video_codec": "VP8",
    }

    def __init__(self, path=CONFIG_FILE):
        self.path = path
        self.url = self.DEFAULTS["url"]
        self.token = self.DEFAULTS["token"]
        self.e2ee_enabled = False
        self.e2ee_key = self.DEFAULTS["e2ee_key"]
        self.simulcast_enabled = False
        self.video_codec = self.DEFAULTS["video_codec"]

    def load(self):
        if not os.path.exists(self.path):
            return
        parser = configparser.ConfigParser()
        parser.read(self.path, encoding="utf-8")
        if not parser.has_section(self.SECTION):
            return
        self.url = parser.get(self.SECTION, "url", fallback=self.DEFAULTS["url"])
        self.token = parser.get(self.SECTION, "token", fallback=self.DEFAULTS["token"])
        self.e2ee_enabled = parser.getboolean(self.SECTION, "e2ee_enabled", fallback=False)
        self.e2ee_key = parser.get(self.SECTION, "e2ee_key", fallback=self.DEFAULTS["e2ee_key"])
        self.simulcast_enabled = parser.getboolean(self.SECTION, "simulcast_enabled", fallback=False)
        self.video_codec = parser.get(self.SECTION, "video_codec", fallback=self.DEFAULTS["video_codec"])

    def save(self):
        parser = configparser.ConfigParser()
        parser.add_section(self.SECTION)
        parser.set(self.SECTION, "url", self.url)
        parser.set(self.SECTION, "token", self.token)
        parser.set(self.SECTION, "e2ee_enabled", str(self.e2ee_enabled).lower())
        parser.set(self.SECTION, "e2ee_key", self.e2ee_key)
        parser.set(self.SECTION, "simulcast_enabled", str(self.simulcast_enabled).lower())
        parser.set(self.SECTION, "video_codec", self.video_codec)
        with open(self.path, "w", encoding="utf-8") as f:
            parser.write(f)


class RoomManager:
    """Manages the LiveKit room connection and events in an asyncio thread."""

    def __init__(self, wx_target):
        self.wx_target = wx_target
        self.room = None  # created in the async thread with the correct event loop
        self.loop = None
        self._thread = None
        self._video_streams = {}  # participant_identity -> VideoStream
        self._audio_streams = {}  # participant_identity -> AudioStream
        self._track_to_participant = {}  # track_sid -> participant_identity
        self._disconnecting = False  # True when _async_disconnect is in progress
        self._test_video_task = None  # asyncio.Task for test video publishing
        self._test_video_track = None  # LocalVideoTrack
        self._test_video_source = None  # VideoSource
        self._test_audio_task = None
        self._test_audio_track = None  # LocalAudioTrack
        self._test_audio_source = None  # AudioSource
        self._video_codec = rtc.VideoCodec.VP8
        self._simulcast = False

    def connect(self, url, token, e2ee_enabled=False, e2ee_key="",
                simulcast=False, video_codec="VP8"):
        self._video_codec = CODEC_MAP.get(video_codec, rtc.VideoCodec.VP8)
        self._simulcast = simulcast
        self._thread = threading.Thread(
            target=self._run_loop,
            args=(url, token, e2ee_enabled, e2ee_key),
            daemon=True,
        )
        self._thread.start()

    def disconnect(self):
        if self.room and self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._async_disconnect(), self.loop)

    def send_data(self, text):
        if self.room and self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.room.local_participant.publish_data(text.encode("utf-8"), topic="chat"),
                self.loop,
            )

    def toggle_test_video(self):
        """Start or stop publishing a test video track. Returns True if starting."""
        if self._test_video_task and not self._test_video_task.cancelled():
            self._test_video_task.cancel()
            return False
        if self.loop and self.loop.is_running():
            self._test_video_task = asyncio.run_coroutine_threadsafe(
                self._publish_test_video(), self.loop
            )
            return True
        return False

    async def _publish_test_video(self):
        WIDTH, HEIGHT, FPS = 640, 480, 24
        try:
            self._test_video_source = rtc.VideoSource(WIDTH, HEIGHT)
            self._test_video_track = rtc.LocalVideoTrack.create_video_track(
                "test-video", self._test_video_source
            )
            await self.room.local_participant.publish_track(
                self._test_video_track,
                rtc.TrackPublishOptions(
                    source=rtc.TrackSource.SOURCE_CAMERA,
                    video_encoding=rtc.VideoEncoding(
                        max_framerate=FPS, max_bitrate=2_000_000
                    ),
                    video_codec=self._video_codec,
                    simulcast=self._simulcast,
                ),
            )
            logger.info("Test video track published")
            fc = 0
            while True:
                frame_data = np.zeros((HEIGHT, WIDTH, 4), dtype=np.uint8)
                offset = int((fc / FPS) * 100) % WIDTH
                for x in range(WIDTH):
                    band = ((x + offset) % WIDTH // 80) % 3
                    frame_data[:, x, band] = 255
                frame_data[:, :, 3] = 255
                self._test_video_source.capture_frame(
                    rtc.VideoFrame(
                        width=WIDTH, height=HEIGHT,
                        type=rtc.VideoBufferType.RGBA,
                        data=frame_data.tobytes(),
                    )
                )
                fc += 1
                await asyncio.sleep(1.0 / FPS)
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("Test video error")
        finally:
            if self._test_video_track and self.room and self.room.isconnected():
                try:
                    await self.room.local_participant.unpublish_track(
                        self._test_video_track.sid
                    )
                except Exception:
                    logger.exception("Failed to unpublish test video track")
            self._test_video_track = None
            self._test_video_source = None
            logger.info("Test video track stopped")

    def toggle_test_audio(self):
        """Start or stop publishing a test audio track. Returns True if starting."""
        if self._test_audio_task and not self._test_audio_task.cancelled():
            self._test_audio_task.cancel()
            return False
        if self.loop and self.loop.is_running():
            self._test_audio_task = asyncio.run_coroutine_threadsafe(
                self._publish_test_audio(), self.loop
            )
            return True
        return False

    async def _publish_test_audio(self):
        SAMPLE_RATE = 48000
        NUM_CHANNELS = 1
        FRAME_DURATION_MS = 10  # 10ms per frame
        SAMPLES_PER_FRAME = SAMPLE_RATE * FRAME_DURATION_MS // 1000
        FREQUENCY = 500.0  # 500 Hz sine wave
        AMPLITUDE = 16000  # ~half of int16 max
        try:
            self._test_audio_source = rtc.AudioSource(SAMPLE_RATE, NUM_CHANNELS)
            self._test_audio_track = rtc.LocalAudioTrack.create_audio_track(
                "test-audio", self._test_audio_source
            )
            await self.room.local_participant.publish_track(
                self._test_audio_track,
                rtc.TrackPublishOptions(
                    source=rtc.TrackSource.SOURCE_MICROPHONE,
                ),
            )
            logger.info("Test audio track published (500 Hz sine)")
            phase = 0.0
            phase_inc = 2.0 * np.pi * FREQUENCY / SAMPLE_RATE
            while True:
                t = np.arange(SAMPLES_PER_FRAME) * phase_inc + phase
                samples = (np.sin(t) * AMPLITUDE).astype(np.int16)
                phase = t[-1] + phase_inc
                frame = rtc.AudioFrame(
                    data=samples.tobytes(),
                    sample_rate=SAMPLE_RATE,
                    num_channels=NUM_CHANNELS,
                    samples_per_channel=SAMPLES_PER_FRAME,
                )
                await self._test_audio_source.capture_frame(frame)
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("Test audio error")
        finally:
            if self._test_audio_track and self.room and self.room.isconnected():
                try:
                    await self.room.local_participant.unpublish_track(
                        self._test_audio_track.sid
                    )
                except Exception:
                    logger.exception("Failed to unpublish test audio track")
            self._test_audio_track = None
            self._test_audio_source = None
            logger.info("Test audio track stopped")

    def _run_loop(self, url, token, e2ee_enabled, e2ee_key):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Create Room inside this thread so it uses the correct event loop
        self.room = rtc.Room(loop=self.loop)
        self.room.on("track_subscribed")(self._on_track_subscribed)
        self.room.on("track_unsubscribed")(self._on_track_unsubscribed)
        self.room.on("local_track_published")(self._on_local_track_published)
        self.room.on("local_track_unpublished")(self._on_local_track_unpublished)
        self.room.on("participant_connected")(self._on_participant_connected)
        self.room.on("participant_disconnected")(self._on_participant_disconnected)
        self.room.on("data_received")(self._on_data_received)
        self.room.on("e2ee_state_changed")(self._on_e2ee_state_changed)
        self.room.on("disconnected")(self._on_disconnected)

        try:
            self.loop.run_until_complete(
                self._async_connect(url, token, e2ee_enabled, e2ee_key)
            )
            self.loop.run_forever()
        finally:
            # Ensure room.disconnect() is called before closing the loop so the
            # FFI queue subscription is removed — otherwise the Rust callback
            # thread will call_soon_threadsafe on a closed loop.
            if self.room and self.room.isconnected():
                try:
                    self.loop.run_until_complete(self.room.disconnect())
                except Exception:
                    pass
            self.loop.close()
            self.loop = None

    async def _async_connect(self, url, token, e2ee_enabled, e2ee_key):
        
        options = rtc.RoomOptions(
            auto_subscribe=True,
        )

        if e2ee_enabled and e2ee_key:
            options.encryption = rtc.E2EEOptions(
                key_provider_options=rtc.KeyProviderOptions(
                    shared_key=e2ee_key.encode("utf-8"),
                )
            )
            logger.info("E2EE enabled with key length=%d, encryption_type=%s",
                        len(e2ee_key), options.encryption.encryption_type)
        else:
            logger.info("E2EE disabled (enabled=%s, key=%r)", e2ee_enabled, bool(e2ee_key))

        try:
            await self.room.connect(url, token, options=options)
            logger.info("Connected. E2EE manager enabled=%s", self.room.e2ee_manager.enabled)
            self._post_state("connected")
            self._post_participants()
        except Exception as e:
            self._post_state("error", str(e))

    async def _async_disconnect(self):
        self._disconnecting = True
        try:
            # Stop test tracks if running
            if self._test_video_task and not self._test_video_task.cancelled():
                self._test_video_task.cancel()
            if self._test_audio_task and not self._test_audio_task.cancelled():
                self._test_audio_task.cancel()
            for stream in list(self._video_streams.values()):
                await stream.aclose()
            self._video_streams.clear()
            for stream in list(self._audio_streams.values()):
                await stream.aclose()
            self._audio_streams.clear()
            self._track_to_participant.clear()
            await self.room.disconnect()
        except Exception:
            logger.exception("Error during room disconnect")
        finally:
            self._disconnecting = False
            self._post_state("disconnected")
            if self.loop:
                self.loop.call_soon(self.loop.stop)

    def _on_track_subscribed(self, track, publication, participant):
        logger.info("Track subscribed: %s (kind=%s) from %s", track.sid, track.kind, participant.identity)
        identity = participant.identity
        if track.kind == rtc.TrackKind.KIND_VIDEO:
            # Close previous video stream for this participant if any
            old_stream = self._video_streams.pop(identity, None)
            if old_stream:
                asyncio.ensure_future(old_stream.aclose())
            stream = rtc.VideoStream(track, format=rtc.VideoBufferType.RGBA)
            self._video_streams[identity] = stream
            self._track_to_participant[track.sid] = identity
            if self.loop:
                asyncio.ensure_future(self._receive_video(identity, stream))
        elif track.kind == rtc.TrackKind.KIND_AUDIO:
            old_stream = self._audio_streams.pop(identity, None)
            if old_stream:
                asyncio.ensure_future(old_stream.aclose())
            stream = rtc.AudioStream(track, sample_rate=48000, num_channels=1)
            self._audio_streams[identity] = stream
            self._track_to_participant[track.sid] = identity
            if self.loop:
                asyncio.ensure_future(self._receive_audio(identity, stream))

    def _on_track_unsubscribed(self, track, publication, participant):
        logger.info("Track unsubscribed: %s from %s", track.sid, participant.identity)
        identity = self._track_to_participant.pop(track.sid, None)
        if identity:
            if track.kind == rtc.TrackKind.KIND_VIDEO:
                stream = self._video_streams.pop(identity, None)
                if stream:
                    asyncio.ensure_future(stream.aclose())
            elif track.kind == rtc.TrackKind.KIND_AUDIO:
                stream = self._audio_streams.pop(identity, None)
                if stream:
                    asyncio.ensure_future(stream.aclose())

    def _on_local_track_published(self, publication, track):
        logger.info("Local track published: %s (kind=%s)", publication.sid, track.kind)
        if track.kind == rtc.TrackKind.KIND_VIDEO:
            identity = self.room.local_participant.identity
            old_stream = self._video_streams.pop(identity, None)
            if old_stream:
                asyncio.ensure_future(old_stream.aclose())
            stream = rtc.VideoStream(track, format=rtc.VideoBufferType.RGBA)
            self._video_streams[identity] = stream
            self._track_to_participant[track.sid] = identity
            self._post_participants()
            if self.loop:
                asyncio.ensure_future(self._receive_video(identity, stream))

    def _on_local_track_unpublished(self, publication):
        logger.info("Local track unpublished: %s", publication.sid)
        identity = self.room.local_participant.identity
        track_sid = publication.sid
        self._track_to_participant.pop(track_sid, None)
        stream = self._video_streams.pop(identity, None)
        if stream:
            asyncio.ensure_future(stream.aclose())
        self._post_participants()

    def _on_participant_connected(self, participant):
        logger.info("Participant connected: %s (%s)", participant.identity, participant.name)
        self._post_participants()

    def _on_participant_disconnected(self, participant):
        logger.info("Participant disconnected: %s (%s)", participant.identity, participant.name)
        identity = participant.identity
        stream = self._video_streams.pop(identity, None)
        if stream:
            asyncio.ensure_future(stream.aclose())
        stream = self._audio_streams.pop(identity, None)
        if stream:
            asyncio.ensure_future(stream.aclose())
        self._track_to_participant = {
            k: v for k, v in self._track_to_participant.items() if v != identity
        }
        self._post_participants()

    def _on_disconnected(self, reason):
        logger.info("Room disconnected: %s", reason)
        if self._disconnecting:
            # _async_disconnect is driving the shutdown — let it handle cleanup and loop.stop
            return
        # Server-initiated disconnect: clean up and stop the loop ourselves
        for stream in list(self._video_streams.values()):
            asyncio.ensure_future(stream.aclose())
        self._video_streams.clear()
        for stream in list(self._audio_streams.values()):
            asyncio.ensure_future(stream.aclose())
        self._audio_streams.clear()
        self._track_to_participant.clear()
        self._post_state("disconnected", str(reason))
        if self.loop and self.loop.is_running():
            self.loop.call_soon(self.loop.stop)

    def _on_e2ee_state_changed(self, participant, state):
        logger.info("E2EE state changed: participant=%s state=%s", participant.identity, state)

    def _on_data_received(self, data_packet):
        sender = data_packet.participant.identity if data_packet.participant else "server"
        try:
            text = data_packet.data.decode("utf-8")
        except UnicodeDecodeError:
            text = f"[binary {len(data_packet.data)} bytes]"
        logger.info("Data received from %s: %s", sender, text)
        evt = ChatMessageEvent(sender=sender, message=text)
        wx.PostEvent(self.wx_target, evt)

    async def _receive_video(self, identity, stream):
        logger.info("Start receiving video for participant: %s", identity)
        frame_count = 0
        try:
            async for frame_event in stream:
                frame = frame_event.frame
                w, h = frame.width, frame.height
                frame_count += 1
                if frame_count == 1:
                    logger.info("First frame from %s: %dx%d", identity, w, h)
                elif frame_count % 300 == 0:
                    logger.debug("Received %d frames from %s (%dx%d)", frame_count, identity, w, h)
                data = bytes(frame.data)
                evt = VideoFrameEvent(
                    identity=identity,
                    width=w,
                    height=h,
                    data=data,
                )
                wx.PostEvent(self.wx_target, evt)
        except Exception as e:
            logger.error("Video stream error for %s: %s", identity, e)
        finally:
            logger.info("Stopped receiving video for %s (total frames: %d)", identity, frame_count)

    async def _receive_audio(self, identity, stream):
        logger.info("Start receiving audio for participant: %s", identity)
        # FFT band edges (Hz) for 5 bars: sub-bass, bass, mid, upper-mid, treble
        band_edges = [0, 300, 800, 2000, 6000, 24000]
        frame_count = 0
        try:
            async for frame_event in stream:
                frame = frame_event.frame
                frame_count += 1
                # Log spectrum every ~50ms
                if frame_count % 5 != 0:
                    continue
                samples = np.frombuffer(frame.data, dtype=np.int16).astype(np.float32)
                if len(samples) == 0:
                    continue
                # Apply Hanning window and compute FFT
                window = np.hanning(len(samples))
                spectrum = np.abs(np.fft.rfft(samples * window))
                freqs = np.fft.rfftfreq(len(samples), d=1.0 / frame.sample_rate)
                # Compute energy for each of the 5 bands
                bands = []
                for i in range(5):
                    mask = (freqs >= band_edges[i]) & (freqs < band_edges[i + 1])
                    if np.any(mask):
                        energy = np.sqrt(np.mean(spectrum[mask] ** 2))
                    else:
                        energy = 0.0
                    bands.append(energy)
                # Normalize to 0..1 range (int16 max FFT magnitude)
                max_val = 32768.0 * np.sqrt(len(samples) / 2)
                bands = [min(b / max_val, 1.0) for b in bands]
                evt = AudioBandsEvent(identity=identity, bands=bands)
                wx.PostEvent(self.wx_target, evt)
        except Exception as e:
            logger.error("Audio stream error for %s: %s", identity, e)
        finally:
            logger.info("Stopped receiving audio for %s (total frames: %d)", identity, frame_count)

    def _post_state(self, state, message="", **kwargs):
        evt = RoomStateEvent(state=state, message=message, **kwargs)
        wx.PostEvent(self.wx_target, evt)

    def _post_participants(self):
        # participants: list of (identity, display_name, is_local)
        participants = []
        if self.room.local_participant:
            lp = self.room.local_participant
            participants.append((lp.identity, lp.name or lp.identity, True))
        for p in self.room.remote_participants.values():
            participants.append((p.identity, p.name or p.identity, False))
        evt = ParticipantEvent(participants=participants)
        wx.PostEvent(self.wx_target, evt)


class VideoPanel(wx.Panel):
    """Single video stream panel with participant name overlay."""

    ASPECT_RATIO = 16 / 9

    def __init__(self, parent, label="", bg_color=None):
        super().__init__(parent, style=wx.BORDER_SIMPLE)
        self.label = label
        self.video_width = 0
        self.video_height = 0
        self.audio_bands = [0.0] * 5  # 5 frequency band levels (0..1)
        self.bitmap = None
        self.bg_color = bg_color or wx.Colour(30, 30, 30)
        self.SetBackgroundColour(self.bg_color)
        self.SetMinSize((160, 90))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)  # suppress default erase
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def DoGetBestSize(self):
        w, _ = self.GetParent().GetSize()
        h = int(w / self.ASPECT_RATIO)
        return wx.Size(w, h)

    def on_size(self, event):
        self.Refresh()
        event.Skip()

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        w, h = self.GetSize()
        dc.SetBackground(wx.Brush(self.bg_color))
        dc.Clear()

        if self.bitmap and self.bitmap.IsOk():
            bw, bh = self.bitmap.GetSize()
            scale = min(w / bw, h / bh)
            new_w, new_h = int(bw * scale), int(bh * scale)
            img = self.bitmap.ConvertToImage().Scale(new_w, new_h, wx.IMAGE_QUALITY_BILINEAR)
            bmp = wx.Bitmap(img)
            x = (w - new_w) // 2
            y = (h - new_h) // 2
            dc.DrawBitmap(bmp, x, y)
        else:
            # Draw placeholder
            dc.SetTextForeground(wx.Colour(100, 100, 100))
            dc.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            text = self.label or "No Video"
            tw, th = dc.GetTextExtent(text)
            dc.DrawText(text, (w - tw) // 2, (h - th) // 2)

        # Draw participant name overlay
        if self.label:
            overlay_text = self.label
            if self.video_width > 0 and self.video_height > 0:
                overlay_text += f" {self.video_width}x{self.video_height}"
            dc.SetTextForeground(wx.WHITE)
            dc.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            tw, th = dc.GetTextExtent(overlay_text)
            pad = 4
            dc.SetBrush(wx.Brush(wx.Colour(0, 0, 0, 160)))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRectangle(pad, h - th - pad * 3, tw + pad * 2, th + pad * 2)
            dc.DrawText(overlay_text, pad * 2, h - th - pad * 2)

        # Draw audio spectrum visualizer bars at top-right corner
        if any(b > 0 for b in self.audio_bands):
            bar_w = 4
            bar_max_h = 30
            gap = 2
            margin = 8
            num_bars = len(self.audio_bands)
            total_w = num_bars * bar_w + (num_bars - 1) * gap
            x0 = w - margin - total_w
            y0 = margin
            # Background pill
            dc.SetBrush(wx.Brush(wx.Colour(0, 0, 0, 140)))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRoundedRectangle(x0 - 4, y0 - 4, total_w + 8, bar_max_h + 8, 4)
            # Bars
            bar_color = wx.Colour(34, 197, 94)
            dc.SetPen(wx.TRANSPARENT_PEN)
            for i, level in enumerate(self.audio_bands):
                bar_h = max(2, int(level * bar_max_h))
                bx = x0 + i * (bar_w + gap)
                by = y0 + bar_max_h - bar_h
                dc.SetBrush(wx.Brush(bar_color))
                dc.DrawRoundedRectangle(bx, by, bar_w, bar_h, 1)

    def update_frame(self, bitmap, label=None):
        """Update the video frame. bitmap should be a wx.Bitmap."""
        self.bitmap = bitmap
        if label is not None:
            self.label = label
        self.Refresh()

    def update_rgba_frame(self, width, height, rgba_data):
        """Convert RGBA video frame data to wx.Bitmap and render."""
        self.video_width = width
        self.video_height = height
        rgba = np.frombuffer(rgba_data, dtype=np.uint8).reshape(height, width, 4)
        rgb = rgba[:, :, :3].astype(np.uint8).tobytes()
        img = wx.Image(width, height, rgb)
        self.bitmap = wx.Bitmap(img)
        self.Refresh()

    def update_audio_bands(self, bands):
        """Update the 5-band audio spectrum levels (list of floats 0..1).
        Does not trigger a repaint — the next video frame refresh will draw them.
        Falls back to explicit refresh only when no video is active."""
        self.audio_bands = bands
        if self.bitmap is None:
            self.Refresh()


class VideoGridPanel(wx.Panel):
    """Multi-video stream grid layout."""

    def __init__(self, parent):
        super().__init__(parent)
        self.SetBackgroundColour(wx.Colour(50, 50, 50))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.video_panels = {}  # track_sid -> VideoPanel
        self.Bind(wx.EVT_SIZE, self._on_resize)

    def _on_resize(self, event):
        self._resize_panels()
        event.Skip()

    def add_video(self, track_sid, label="", bg_color=None):
        if track_sid in self.video_panels:
            return self.video_panels[track_sid]
        panel = VideoPanel(self, label=label, bg_color=bg_color)
        self.video_panels[track_sid] = panel
        self._relayout()
        return panel

    def remove_video(self, track_sid):
        panel = self.video_panels.pop(track_sid, None)
        if panel:
            panel.Destroy()
            self._relayout()

    def update_video_rgba(self, identity, width, height, rgba_data):
        """Update a participant's video panel with RGBA frame data."""
        panel = self.video_panels.get(identity)
        if panel:
            panel.update_rgba_frame(width, height, rgba_data)

    def update_audio_bands(self, identity, bands):
        """Update a participant's audio spectrum visualizer."""
        panel = self.video_panels.get(identity)
        if panel:
            panel.update_audio_bands(bands)

    def update_video(self, identity, bitmap, label=None):
        panel = self.video_panels.get(identity)
        if panel:
            panel.update_frame(bitmap, label)

    def clear_all(self):
        for panel in self.video_panels.values():
            panel.Destroy()
        self.video_panels.clear()
        self.Refresh()

    def _get_cols(self, count):
        if count <= 1:
            return 1
        if count <= 2:
            return 2
        if count <= 4:
            return 2
        if count <= 9:
            return 3
        return 4

    def _relayout(self):
        self._resize_panels()

    def _resize_panels(self):
        count = len(self.video_panels)
        if count == 0:
            self.Layout()
            return

        gap = 2
        cols = self._get_cols(count)
        rows = (count + cols - 1) // cols

        grid_w, grid_h = self.GetClientSize()
        if grid_w <= 0 or grid_h <= 0:
            return

        cell_w = (grid_w - gap * (cols - 1)) // cols
        cell_h = int(cell_w / VideoPanel.ASPECT_RATIO)

        # If total height exceeds available space, fit by height instead
        total_h = cell_h * rows + gap * (rows - 1)
        if total_h > grid_h:
            cell_h = (grid_h - gap * (rows - 1)) // rows
            cell_w = int(cell_h * VideoPanel.ASPECT_RATIO)

        # Center the grid
        actual_grid_w = cell_w * cols + gap * (cols - 1)
        actual_grid_h = cell_h * rows + gap * (rows - 1)
        offset_x = (grid_w - actual_grid_w) // 2
        offset_y = (grid_h - actual_grid_h) // 2

        for i, panel in enumerate(self.video_panels.values()):
            r, c = divmod(i, cols)
            x = offset_x + c * (cell_w + gap)
            y = offset_y + r * (cell_h + gap)
            panel.SetSize(x, y, cell_w, cell_h)

        # Use no sizer — manual positioning
        if self.GetSizer():
            self.SetSizer(None, False)


class LoginPanel(wx.Panel):
    """Left-side login panel with URL and token inputs."""

    def __init__(self, parent):
        super().__init__(parent)
        self.SetBackgroundColour(wx.Colour(245, 245, 245))
        self.SetMinSize((280, -1))

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        title = wx.StaticText(self, label="LiveKit Connect")
        title.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        main_sizer.Add(title, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 20)

        # URL input
        url_label = wx.StaticText(self, label="Server URL")
        url_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        main_sizer.Add(url_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 20)

        self.url_input = wx.TextCtrl(self, value="ws://localhost:7880", size=(-1, 30))
        main_sizer.Add(self.url_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)

        main_sizer.AddSpacer(10)

        # Token input
        token_label = wx.StaticText(self, label="Token")
        token_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        main_sizer.Add(token_label, 0, wx.LEFT | wx.RIGHT, 20)

        self.token_input = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(-1, 80))
        self.token_input.SetHint("Paste your access token here...")
        main_sizer.Add(self.token_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)

        main_sizer.AddSpacer(10)

        # E2EE checkbox
        self.e2ee_checkbox = wx.CheckBox(self, label="Enable E2EE")
        self.e2ee_checkbox.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        main_sizer.Add(self.e2ee_checkbox, 0, wx.LEFT | wx.RIGHT, 20)

        main_sizer.AddSpacer(5)

        # E2EE key input
        self.e2ee_key_label = wx.StaticText(self, label="E2EE Shared Key")
        self.e2ee_key_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.e2ee_key_label.Enable(False)
        main_sizer.Add(self.e2ee_key_label, 0, wx.LEFT | wx.RIGHT, 20)

        self.e2ee_key_input = wx.TextCtrl(self, size=(-1, 30))
        self.e2ee_key_input.SetHint("Enter shared encryption key...")
        self.e2ee_key_input.Enable(False)
        main_sizer.Add(self.e2ee_key_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)

        main_sizer.AddSpacer(10)

        # Simulcast checkbox
        self.simulcast_checkbox = wx.CheckBox(self, label="Enable Simulcast")
        self.simulcast_checkbox.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        main_sizer.Add(self.simulcast_checkbox, 0, wx.LEFT | wx.RIGHT, 20)

        main_sizer.AddSpacer(5)

        # Video Codec selection
        codec_label = wx.StaticText(self, label="Video Codec")
        codec_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        main_sizer.Add(codec_label, 0, wx.LEFT | wx.RIGHT, 20)

        codecs = ["VP8", "VP9", "AV1", "H264", "H265"]
        self.codec_choice = wx.Choice(self, choices=codecs, size=(-1, 30))
        self.codec_choice.SetSelection(0)  # default VP8
        main_sizer.Add(self.codec_choice, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)

        main_sizer.AddSpacer(20)

        # Connect button
        self.connect_btn = wx.Button(self, label="Connect", size=(-1, 36))
        self.connect_btn.SetBackgroundColour(wx.Colour(59, 130, 246))
        self.connect_btn.SetForegroundColour(wx.WHITE)
        self.connect_btn.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        main_sizer.Add(self.connect_btn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)

        main_sizer.AddSpacer(10)

        # Disconnect button
        self.disconnect_btn = wx.Button(self, label="Disconnect", size=(-1, 36))
        self.disconnect_btn.Enable(False)
        main_sizer.Add(self.disconnect_btn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)

        main_sizer.AddSpacer(20)

        # Status
        self.status_label = wx.StaticText(self, label="Status: Disconnected")
        self.status_label.SetForegroundColour(wx.Colour(120, 120, 120))
        main_sizer.Add(self.status_label, 0, wx.LEFT | wx.RIGHT, 20)

        self.SetSizer(main_sizer)

    def load_config(self, cfg):
        """Apply Configure values to UI controls."""
        self.url_input.SetValue(cfg.url)
        self.token_input.SetValue(cfg.token)
        self.e2ee_checkbox.SetValue(cfg.e2ee_enabled)
        self.e2ee_key_label.Enable(cfg.e2ee_enabled)
        self.e2ee_key_input.Enable(cfg.e2ee_enabled)
        self.e2ee_key_input.SetValue(cfg.e2ee_key)
        self.simulcast_checkbox.SetValue(cfg.simulcast_enabled)
        codecs = [self.codec_choice.GetString(i) for i in range(self.codec_choice.GetCount())]
        if cfg.video_codec in codecs:
            self.codec_choice.SetSelection(codecs.index(cfg.video_codec))

    def save_config(self, cfg):
        """Save current UI values to Configure."""
        cfg.url = self.url_input.GetValue().strip()
        cfg.token = self.token_input.GetValue().strip()
        cfg.e2ee_enabled = self.e2ee_checkbox.IsChecked()
        cfg.e2ee_key = self.e2ee_key_input.GetValue()
        cfg.simulcast_enabled = self.simulcast_checkbox.IsChecked()
        cfg.video_codec = self.codec_choice.GetString(self.codec_choice.GetSelection())
        cfg.save()

    def _on_e2ee_toggle(self, event):
        enabled = self.e2ee_checkbox.IsChecked()
        self.e2ee_key_label.Enable(enabled)
        self.e2ee_key_input.Enable(enabled)

    def set_status(self, text, color=None):
        self.status_label.SetLabel(f"Status: {text}")
        if color:
            self.status_label.SetForegroundColour(color)
        self.Layout()

    def set_connected(self, connected):
        self.connect_btn.Enable(not connected)
        self.disconnect_btn.Enable(connected)
        self.url_input.Enable(not connected)
        self.token_input.Enable(not connected)
        self.e2ee_checkbox.Enable(not connected)
        self.e2ee_key_label.Enable(not connected and self.e2ee_checkbox.IsChecked())
        self.e2ee_key_input.Enable(not connected and self.e2ee_checkbox.IsChecked())
        self.simulcast_checkbox.Enable(not connected)
        self.codec_choice.Enable(not connected)
        if connected:
            self.set_status("Connected", wx.Colour(34, 197, 94))
        else:
            self.set_status("Disconnected", wx.Colour(120, 120, 120))


class RightPanel(wx.Panel):
    """Right-side panel with test buttons and text chat."""

    def __init__(self, parent):
        super().__init__(parent)
        self.SetBackgroundColour(wx.Colour(245, 245, 245))
        self.SetMinSize((280, -1))

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # --- Test buttons area ---
        btn_label = wx.StaticText(self, label="Test Actions")
        btn_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        main_sizer.Add(btn_label, 0, wx.ALL, 10)

        btn_sizer = wx.BoxSizer(wx.VERTICAL)
        self.pub_video_btn = wx.Button(self, label="Publish Test Video", size=(-1, 30))
        btn_sizer.Add(self.pub_video_btn, 0, wx.EXPAND | wx.BOTTOM, 4)

        self.pub_audio_btn = wx.Button(self, label="Publish Test Audio", size=(-1, 30))
        btn_sizer.Add(self.pub_audio_btn, 0, wx.EXPAND | wx.BOTTOM, 4)

        main_sizer.Add(btn_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        main_sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 10)

        # --- Text Chat area ---
        chat_label = wx.StaticText(self, label="Text Chat")
        chat_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        main_sizer.Add(chat_label, 0, wx.LEFT | wx.RIGHT, 10)

        self.chat_log = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2,
        )
        self.chat_log.SetBackgroundColour(wx.WHITE)
        self.chat_log.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        main_sizer.Add(self.chat_log, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # Input row: text input + send button
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.chat_input = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, size=(-1, 30))
        self.chat_input.SetHint("Type a message...")
        input_sizer.Add(self.chat_input, 1, wx.EXPAND | wx.RIGHT, 4)

        self.chat_send_btn = wx.Button(self, label="Send", size=(60, 30))
        input_sizer.Add(self.chat_send_btn, 0)

        main_sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(main_sizer)

    def append_chat(self, sender, message):
        """Append a chat message to the log."""
        self.chat_log.AppendText(f"{sender}: {message}\n")

    def set_connected(self, connected):
        self.pub_video_btn.Enable(connected)
        self.pub_audio_btn.Enable(connected)
        self.chat_send_btn.Enable(connected)
        self.chat_input.Enable(connected)


class MainFrame(wx.Frame):
    """Main application frame: left login (fixed), center video grid (flex), right panel (fixed)."""

    LOGIN_PANEL_WIDTH = 280
    RIGHT_PANEL_WIDTH = 280

    def __init__(self):
        super().__init__(None, title="LiveKit Video Room", size=(1200, 700))
        self.SetMinSize((800, 500))

        main_panel = wx.Panel(self)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)

        self.login_panel = LoginPanel(main_panel)
        self.login_panel.SetMinSize((self.LOGIN_PANEL_WIDTH, -1))
        self.login_panel.SetMaxSize((self.LOGIN_PANEL_WIDTH, -1))
        hsizer.Add(self.login_panel, 0, wx.EXPAND)

        self.video_grid = VideoGridPanel(main_panel)
        hsizer.Add(self.video_grid, 1, wx.EXPAND)

        self.right_panel = RightPanel(main_panel)
        self.right_panel.SetMinSize((self.RIGHT_PANEL_WIDTH, -1))
        self.right_panel.SetMaxSize((self.RIGHT_PANEL_WIDTH, -1))
        hsizer.Add(self.right_panel, 0, wx.EXPAND)

        main_panel.SetSizer(hsizer)

        # Load config
        self.config = Configure()
        self.config.load()
        self.login_panel.load_config(self.config)

        # Room manager
        self.room_mgr = RoomManager(self)

        # Bind button events
        self.login_panel.connect_btn.Bind(wx.EVT_BUTTON, self.on_connect)
        self.login_panel.disconnect_btn.Bind(wx.EVT_BUTTON, self.on_disconnect)
        self.login_panel.e2ee_checkbox.Bind(wx.EVT_CHECKBOX, self.on_e2ee_toggle)

        # Right panel buttons
        self.right_panel.pub_video_btn.Bind(wx.EVT_BUTTON, self.on_toggle_test_video)
        self.right_panel.pub_audio_btn.Bind(wx.EVT_BUTTON, self.on_toggle_test_audio)
        self.right_panel.chat_send_btn.Bind(wx.EVT_BUTTON, self.on_chat_send)
        self.right_panel.chat_input.Bind(wx.EVT_TEXT_ENTER, self.on_chat_send)
        self.right_panel.set_connected(False)

        # Bind custom events from RoomManager
        self.Bind(EVT_VIDEO_FRAME, self.on_video_frame)
        self.Bind(EVT_ROOM_STATE, self.on_room_state)
        self.Bind(EVT_PARTICIPANT, self.on_participant_update)
        self.Bind(EVT_AUDIO_BANDS, self.on_audio_bands)
        self.Bind(EVT_CHAT_MESSAGE, self.on_chat_message)

        self.Centre()

    def on_e2ee_toggle(self, event):
        self.login_panel._on_e2ee_toggle(event)

    def on_connect(self, event):
        url = self.login_panel.url_input.GetValue().strip()
        token = self.login_panel.token_input.GetValue().strip()

        if not url:
            wx.MessageBox("Please enter a server URL.", "Error", wx.OK | wx.ICON_ERROR)
            return
        if not token:
            wx.MessageBox("Please enter a token.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Save config before connecting
        self.login_panel.save_config(self.config)

        self.login_panel.set_status("Connecting...", wx.Colour(234, 179, 8))
        self.login_panel.connect_btn.Enable(False)

        e2ee_enabled = self.login_panel.e2ee_checkbox.IsChecked()
        e2ee_key = self.login_panel.e2ee_key_input.GetValue()
        simulcast = self.login_panel.simulcast_checkbox.IsChecked()
        video_codec = self.login_panel.codec_choice.GetString(
            self.login_panel.codec_choice.GetSelection()
        )

        self.room_mgr.connect(
            url, token,
            e2ee_enabled=e2ee_enabled,
            e2ee_key=e2ee_key,
            simulcast=simulcast,
            video_codec=video_codec,
        )

    def on_disconnect(self, event):
        self.login_panel.set_status("Disconnecting...", wx.Colour(234, 179, 8))
        self.room_mgr.disconnect()

    def on_toggle_test_video(self, event):
        started = self.room_mgr.toggle_test_video()
        if started:
            self.right_panel.pub_video_btn.SetLabel("Stop Test Video")
        else:
            self.right_panel.pub_video_btn.SetLabel("Publish Test Video")

    def on_toggle_test_audio(self, event):
        started = self.room_mgr.toggle_test_audio()
        if started:
            self.right_panel.pub_audio_btn.SetLabel("Stop Test Audio")
        else:
            self.right_panel.pub_audio_btn.SetLabel("Publish Test Audio")

    def on_chat_send(self, event):
        text = self.right_panel.chat_input.GetValue().strip()
        if not text:
            return
        self.right_panel.chat_input.Clear()
        self.right_panel.append_chat("Me", text)
        self.room_mgr.send_data(text)

    def on_audio_bands(self, event):
        """Handle audio spectrum bands from async thread."""
        self.video_grid.update_audio_bands(event.identity, event.bands)

    def on_chat_message(self, event):
        self.right_panel.append_chat(event.sender, event.message)

    def on_video_frame(self, event):
        """Handle video frame from async thread — delegate to VideoPanel for rendering."""
        self.video_grid.update_video_rgba(
            event.identity, event.width, event.height, event.data
        )

    def on_room_state(self, event):
        """Handle room state changes from RoomManager."""
        state = event.state

        if state == "connected":
            self.login_panel.set_connected(True)
            self.right_panel.set_connected(True)

        elif state == "disconnected":
            self.video_grid.clear_all()
            self.login_panel.set_connected(False)
            self.right_panel.set_connected(False)
            self.right_panel.pub_video_btn.SetLabel("Publish Test Video")
            self.right_panel.pub_audio_btn.SetLabel("Publish Test Audio")
            if event.message:
                self.login_panel.set_status(
                    f"Disconnected: {event.message}", wx.Colour(120, 120, 120)
                )
            # Create a new RoomManager for the next connection
            self.room_mgr = RoomManager(self)

        elif state == "error":
            self.login_panel.set_status(f"Error: {event.message}", wx.Colour(239, 68, 68))
            self.login_panel.connect_btn.Enable(True)
            self.room_mgr = RoomManager(self)

    def on_participant_update(self, event):
        """Sync video grid based on participant list."""
        participants = event.participants  # list of (identity, display_name, is_local)

        # Sync video grid: add new participants, remove departed ones
        current_identities = {identity for identity, _, _ in participants}
        existing_identities = set(self.video_grid.video_panels.keys())

        # Remove panels for participants who left
        for identity in existing_identities - current_identities:
            self.video_grid.remove_video(identity)

        # Add panels for new participants
        for identity, name, is_local in participants:
            if identity not in existing_identities:
                self.video_grid.add_video(identity, label=name)


def main():
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
