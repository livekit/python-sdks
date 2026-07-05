# Copyright 2026 LiveKit, Inc.
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

"""API tests that drive the unified LiveKitAPI against the mock LiveKit server
(livekit/livekit cmd/test-server). Point them at a running instance with
LK_TEST_SERVER_URL (default http://127.0.0.1:9999); they skip when no server is
reachable.

Because the mock enforces the same per-method grants as the real server, a call
that succeeds also proves the SDK attached the right grants automatically. The
smoke tests fully populate each request so they double as a reference for a
complete call and exercise field serialization. Mock directives are passed via
the X-Lk-Mock header, set as a default header on the session (the public service
methods don't expose per-call headers).
"""

import asyncio
import contextlib
import json
import os
import urllib.request
from typing import Optional

import aiohttp
import pytest
from google.protobuf.duration_pb2 import Duration

import livekit.api as api
from livekit.api import SipCallError, ServerError
from livekit.protocol.rtc import SessionDescription

BASE = os.getenv("LK_TEST_SERVER_URL", "http://127.0.0.1:9999")
# devkey/secret match `livekit-server --dev`, which the mock verifies against.
KEY, SECRET = "devkey", "secret"


def _server_up() -> bool:
    try:
        with urllib.request.urlopen(f"{BASE}/settings/regions", timeout=1) as r:
            return r.status == 200
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _server_up(), reason=f"mock test server not reachable at {BASE}"
)


@contextlib.asynccontextmanager
async def _api(mock: Optional[dict] = None):
    """A LiveKitAPI whose session carries the given X-Lk-Mock directives (if any)
    as a default header on every request."""
    headers = {"X-Lk-Mock": json.dumps(mock)} if mock else None
    async with aiohttp.ClientSession(headers=headers) as session:
        yield api.LiveKitAPI(BASE, KEY, SECRET, session=session)


def _mp4(path: str) -> api.EncodedFileOutput:
    return api.EncodedFileOutput(file_type=api.EncodedFileType.MP4, filepath=path)


# -- smoke: fully-populated calls across every service ------------------------


async def _room_smoke():
    async with _api() as lk:
        await lk.room.create_room(
            api.CreateRoomRequest(
                name="test-room",
                empty_timeout=300,
                departure_timeout=60,
                max_participants=50,
                metadata='{"scene":"lobby"}',
                min_playout_delay=100,
                max_playout_delay=2000,
                sync_streams=True,
                agents=[api.RoomAgentDispatch(agent_name="greeter", metadata='{"lang":"en"}')],
            )
        )
        await lk.room.list_rooms(api.ListRoomsRequest(names=["test-room", "lobby"]))
        await lk.room.delete_room(api.DeleteRoomRequest(room="test-room"))
        await lk.room.list_participants(api.ListParticipantsRequest(room="test-room"))
        await lk.room.get_participant(
            api.RoomParticipantIdentity(room="test-room", identity="participant-42")
        )
        await lk.room.remove_participant(
            api.RoomParticipantIdentity(room="test-room", identity="participant-42")
        )
        await lk.room.forward_participant(
            api.ForwardParticipantRequest(
                room="test-room", identity="participant-42", destination_room="overflow-room"
            )
        )
        await lk.room.move_participant(
            api.MoveParticipantRequest(
                room="test-room", identity="participant-42", destination_room="breakout-room"
            )
        )
        await lk.room.mute_published_track(
            api.MuteRoomTrackRequest(
                room="test-room", identity="participant-42", track_sid="TR_video1", muted=True
            )
        )
        await lk.room.update_participant(
            api.UpdateParticipantRequest(
                room="test-room",
                identity="participant-42",
                name="Alice",
                metadata='{"role":"host"}',
                attributes={"seat": "1A"},
                permission=api.ParticipantPermission(
                    can_subscribe=True,
                    can_publish=True,
                    can_publish_data=True,
                    can_publish_sources=[api.TrackSource.MICROPHONE, api.TrackSource.CAMERA],
                    can_update_metadata=True,
                ),
            )
        )
        await lk.room.update_subscriptions(
            api.UpdateSubscriptionsRequest(
                room="test-room",
                identity="participant-42",
                track_sids=["TR_video1"],
                subscribe=True,
                participant_tracks=[
                    api.ParticipantTracks(participant_sid="PA_xyz789", track_sids=["TR_video1"])
                ],
            )
        )
        await lk.room.update_room_metadata(
            api.UpdateRoomMetadataRequest(room="test-room", metadata='{"scene":"intro"}')
        )
        await lk.room.send_data(
            api.SendDataRequest(
                room="test-room",
                data=b"hello world",
                kind=api.DataPacket.RELIABLE,
                destination_identities=["participant-42"],
                topic="chat",
            )
        )


async def _egress_smoke():
    async with _api() as lk:
        await lk.egress.start_room_composite_egress(
            api.RoomCompositeEgressRequest(
                room_name="test-room", layout="grid", file_outputs=[_mp4("room.mp4")]
            )
        )
        await lk.egress.start_web_egress(
            api.WebEgressRequest(
                url="https://example.com/scene",
                stream_outputs=[
                    api.StreamOutput(
                        protocol=api.StreamProtocol.RTMP, urls=["rtmps://a.example.com/live/key"]
                    )
                ],
            )
        )
        await lk.egress.start_participant_egress(
            api.ParticipantEgressRequest(
                room_name="test-room",
                identity="participant-42",
                screen_share=True,
                file_outputs=[_mp4("participant.mp4")],
            )
        )
        await lk.egress.start_track_composite_egress(
            api.TrackCompositeEgressRequest(
                room_name="test-room",
                audio_track_id="TR_audio1",
                video_track_id="TR_video1",
                file_outputs=[_mp4("track-composite.mp4")],
            )
        )
        await lk.egress.start_track_egress(
            api.TrackEgressRequest(
                room_name="test-room",
                track_id="TR_video1",
                file=api.DirectFileOutput(filepath="track.mp4"),
            )
        )
        await lk.egress.update_layout(
            api.UpdateLayoutRequest(egress_id="EG_abc123", layout="speaker")
        )
        await lk.egress.update_stream(
            api.UpdateStreamRequest(
                egress_id="EG_abc123",
                add_output_urls=["rtmps://b.example.com/live/key"],
                remove_output_urls=["rtmps://a.example.com/live/key"],
            )
        )
        await lk.egress.list_egress(
            api.ListEgressRequest(room_name="test-room", egress_id="EG_abc123", active=True)
        )
        await lk.egress.stop_egress(api.StopEgressRequest(egress_id="EG_abc123"))


async def _ingress_smoke():
    async with _api() as lk:
        await lk.ingress.create_ingress(
            api.CreateIngressRequest(
                input_type=api.IngressInput.RTMP_INPUT,
                name="stream-input",
                room_name="test-room",
                participant_identity="ingress-bot",
                participant_name="Live Stream",
                participant_metadata='{"source":"rtmp"}',
                enable_transcoding=True,
                audio=api.IngressAudioOptions(
                    name="audio",
                    source=api.TrackSource.MICROPHONE,
                    preset=api.IngressAudioEncodingPreset.OPUS_STEREO_96KBPS,
                ),
                video=api.IngressVideoOptions(
                    name="video",
                    source=api.TrackSource.CAMERA,
                    preset=api.IngressVideoEncodingPreset.H264_1080P_30FPS_3_LAYERS,
                ),
            )
        )
        await lk.ingress.update_ingress(
            api.UpdateIngressRequest(
                ingress_id="IN_abc123",
                name="stream-input-v2",
                room_name="test-room",
                participant_identity="ingress-bot",
                participant_name="Live Stream",
                enable_transcoding=True,
            )
        )
        await lk.ingress.list_ingress(
            api.ListIngressRequest(room_name="test-room", ingress_id="IN_abc123")
        )
        await lk.ingress.delete_ingress(api.DeleteIngressRequest(ingress_id="IN_abc123"))


async def _sip_smoke():
    async with _api() as lk:
        await lk.sip.create_inbound_trunk(
            api.CreateSIPInboundTrunkRequest(
                trunk=api.SIPInboundTrunkInfo(
                    name="inbound",
                    metadata='{"provider":"telco"}',
                    numbers=["+15105550100"],
                    allowed_addresses=["203.0.113.0/24"],
                    allowed_numbers=["+15105550111"],
                    auth_username="sip-user",
                    auth_password="sip-pass",
                    krisp_enabled=True,
                )
            )
        )
        await lk.sip.create_outbound_trunk(
            api.CreateSIPOutboundTrunkRequest(
                trunk=api.SIPOutboundTrunkInfo(
                    name="outbound",
                    address="sip.telco.example.com",
                    transport=api.SIPTransport.SIP_TRANSPORT_TLS,
                    destination_country="US",
                    numbers=["+15105550100"],
                    auth_username="sip-user",
                    auth_password="sip-pass",
                )
            )
        )
        await lk.sip.update_inbound_trunk(
            "ST_abc123",
            api.SIPInboundTrunkInfo(name="inbound-v2", numbers=["+15105550100"]),
        )
        await lk.sip.update_outbound_trunk(
            "ST_abc123",
            api.SIPOutboundTrunkInfo(
                name="outbound-v2",
                address="sip.telco.example.com",
                transport=api.SIPTransport.SIP_TRANSPORT_TLS,
                numbers=["+15105550100"],
            ),
        )
        await lk.sip.list_inbound_trunk(
            api.ListSIPInboundTrunkRequest(trunk_ids=["ST_abc123"], numbers=["+15105550100"])
        )
        await lk.sip.list_outbound_trunk(api.ListSIPOutboundTrunkRequest(trunk_ids=["ST_abc123"]))
        await lk.sip.delete_trunk(api.DeleteSIPTrunkRequest(sip_trunk_id="ST_abc123"))
        await lk.sip.create_dispatch_rule(
            api.CreateSIPDispatchRuleRequest(
                dispatch_rule=api.SIPDispatchRuleInfo(
                    name="direct-to-support",
                    metadata='{"team":"support"}',
                    trunk_ids=["ST_abc123"],
                    rule=api.SIPDispatchRule(
                        dispatch_rule_direct=api.SIPDispatchRuleDirect(
                            room_name="support", pin="1234"
                        )
                    ),
                )
            )
        )
        await lk.sip.update_dispatch_rule(
            "SDR_abc123",
            api.SIPDispatchRuleInfo(
                name="individual-v2",
                rule=api.SIPDispatchRule(
                    dispatch_rule_individual=api.SIPDispatchRuleIndividual(room_prefix="call-")
                ),
            ),
        )
        await lk.sip.list_dispatch_rule(
            api.ListSIPDispatchRuleRequest(
                dispatch_rule_ids=["SDR_abc123"], trunk_ids=["ST_abc123"]
            )
        )
        await lk.sip.delete_dispatch_rule(
            api.DeleteSIPDispatchRuleRequest(sip_dispatch_rule_id="SDR_abc123")
        )


async def _connector_smoke():
    offer = SessionDescription(type="offer", sdp="v=0\r\no=- 0 0 IN IP4 127.0.0.1\r\n")
    answer = SessionDescription(type="answer", sdp="v=0\r\no=- 0 0 IN IP4 127.0.0.1\r\n")
    async with _api() as lk:
        await lk.connector.dial_whatsapp_call(
            api.DialWhatsAppCallRequest(
                whatsapp_phone_number_id="123456789012345",
                whatsapp_to_phone_number="+15105550100",
                whatsapp_api_key="wa-secret-key",
                whatsapp_cloud_api_version="23.0",
                room_name="test-room",
                participant_identity="whatsapp-caller",
                participant_name="WhatsApp Caller",
                destination_country="US",
                ringing_timeout=Duration(seconds=30),
            )
        )
        await lk.connector.accept_whatsapp_call(
            api.AcceptWhatsAppCallRequest(
                whatsapp_phone_number_id="123456789012345",
                whatsapp_api_key="wa-secret-key",
                whatsapp_cloud_api_version="23.0",
                whatsapp_call_id="wacid.HBgLABC",
                sdp=answer,
                room_name="test-room",
                participant_identity="whatsapp-callee",
            )
        )
        await lk.connector.connect_whatsapp_call(
            api.ConnectWhatsAppCallRequest(whatsapp_call_id="wacid.HBgLABC", sdp=offer)
        )
        await lk.connector.disconnect_whatsapp_call(
            api.DisconnectWhatsAppCallRequest(
                whatsapp_call_id="wacid.HBgLABC",
                whatsapp_api_key="wa-secret-key",
                disconnect_reason=api.DisconnectWhatsAppCallRequest.BUSINESS_INITIATED,
            )
        )
        await lk.connector.connect_twilio_call(
            api.ConnectTwilioCallRequest(
                twilio_call_direction=api.ConnectTwilioCallRequest.TWILIO_CALL_DIRECTION_INBOUND,
                room_name="test-room",
                participant_identity="twilio-caller",
                destination_country="US",
            )
        )


async def _agent_dispatch_smoke():
    async with _api() as lk:
        await lk.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                room="test-room", agent_name="inbound-agent", metadata='{"lang":"en"}'
            )
        )
        await lk.agent_dispatch.get_dispatch("AD_abc123", "test-room")
        await lk.agent_dispatch.list_dispatch("test-room")
        await lk.agent_dispatch.delete_dispatch("AD_abc123", "test-room")


def test_room_smoke():
    asyncio.run(_room_smoke())


def test_egress_smoke():
    asyncio.run(_egress_smoke())


def test_ingress_smoke():
    asyncio.run(_ingress_smoke())


def test_sip_smoke():
    asyncio.run(_sip_smoke())


def test_connector_smoke():
    asyncio.run(_connector_smoke())


def test_agent_dispatch_smoke():
    asyncio.run(_agent_dispatch_smoke())


# -- deep: create_room round-trip + error propagation -------------------------


async def _create_room_echo():
    async with _api() as lk:
        req = api.CreateRoomRequest(
            name="echo-room", metadata='{"scene":"lobby"}', empty_timeout=300, max_participants=50
        )
        room = await lk.room.create_room(req)
        assert room.name == "echo-room"
        assert room.metadata == '{"scene":"lobby"}'
        assert room.empty_timeout == 300
        assert room.max_participants == 50
        assert room.sid != ""  # placeholder assigned by the mock


def test_create_room_echoes_fields():
    asyncio.run(_create_room_echo())


async def _create_room_error():
    mock = {"failRegions": [0], "failStatus": 400, "failTwirpCode": "invalid_argument"}
    async with _api(mock) as lk:
        with pytest.raises(ServerError) as exc:
            await lk.room.create_room(api.CreateRoomRequest(name="test-room"))
    assert exc.value.code == "invalid_argument"


def test_create_room_propagates_twirp_error():
    asyncio.run(_create_room_error())


# -- deep: SIP participant (delayMs:0 skips the mock's answer wait) ------------


async def _sip_participant():
    async with _api() as lk:
        p = await lk.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                sip_trunk_id="ST_abc123",
                sip_call_to="+15105550100",
                room_name="test-room",
                participant_identity="sip-caller",
                participant_name="SIP Caller",
                participant_metadata='{"source":"pstn"}',
                dtmf="1234#",
                play_dialtone=True,
                max_call_duration=Duration(seconds=3600),
            )
        )
        assert p.room_name == "test-room"
        assert p.participant_identity == "sip-caller"

    async with _api({"delayMs": 0}) as lk:
        await lk.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                sip_trunk_id="ST_abc123",
                sip_call_to="+15105550100",
                room_name="test-room",
                wait_until_answered=True,
                ringing_timeout=Duration(seconds=2),
            )
        )
        await lk.sip.transfer_sip_participant(
            api.TransferSIPParticipantRequest(
                room_name="test-room",
                participant_identity="sip-caller",
                transfer_to="tel:+15105550122",
                ringing_timeout=Duration(seconds=2),
            )
        )


def test_sip_participant():
    asyncio.run(_sip_participant())


# -- cross-cutting: token auth ------------------------------------------------


async def _token_auth():
    token = api.AccessToken(KEY, SECRET).with_grants(api.VideoGrants(room_create=True)).to_jwt()
    async with api.LiveKitAPI.with_token(token, BASE) as lk:
        room = await lk.room.create_room(api.CreateRoomRequest(name="token-room"))
        assert room.name == "token-room"


def test_token_auth():
    asyncio.run(_token_auth())


# -- cross-cutting: SIP call errors surface as SipCallError -------------------


async def _sip_call_error(sip: dict, *, wait: bool = False):
    create = api.CreateSIPParticipantRequest(
        sip_trunk_id="ST_abc123", sip_call_to="+15105550100", room_name="test-room"
    )
    if wait:
        create.wait_until_answered = True
        create.ringing_timeout.CopyFrom(Duration(seconds=2))
    async with _api({"delayMs": 0, "sipStatus": sip}) as lk:
        with pytest.raises(SipCallError) as exc:
            await lk.sip.create_sip_participant(create)
    return exc.value


def test_sip_busy():
    err = asyncio.run(_sip_call_error({"code": 486, "status": "Busy Here"}))
    assert isinstance(err, ServerError)
    assert err.code == "resource_exhausted"
    assert err.sip_status_code == 486
    assert err.sip_status == "Busy Here"
    # printable representation makes the failure clear
    assert "486" in str(err) and "Busy Here" in str(err)


def test_sip_declined():
    err = asyncio.run(_sip_call_error({"code": 603, "status": "Decline"}))
    assert err.code == "permission_denied"
    assert err.sip_status_code == 603


def test_sip_no_answer():
    # Callee doesn't pick up within ringing_timeout -> SIP 408 Request Timeout.
    err = asyncio.run(_sip_call_error({"code": 408, "status": "Request Timeout"}, wait=True))
    assert err.code == "deadline_exceeded"
    assert err.sip_status_code == 408


# -- cross-cutting: client-side dial timeout ----------------------------------


async def _sip_dial_timeout():
    # ringing 1s -> ~3s dial budget; the mock delays the answer past it.
    async with _api({"delayMs": 4000}) as lk:
        await lk.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                sip_trunk_id="ST_abc123",
                sip_call_to="+15105550100",
                room_name="test-room",
                wait_until_answered=True,
                ringing_timeout=Duration(seconds=1),
            )
        )


def test_sip_dial_timeout():
    with pytest.raises((asyncio.TimeoutError, TimeoutError)):
        asyncio.run(_sip_dial_timeout())
