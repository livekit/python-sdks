from __future__ import annotations

from typing import Optional, Union

from livekit.protocol.connector_whatsapp import AcceptWhatsAppCallRequest
from livekit.protocol.sip import CreateSIPParticipantRequest, TransferSIPParticipantRequest

# Requests that carry wait_until_answered / ringing_timeout and share the
# phone-dialing timeout behavior.
DialRequest = Union[
    CreateSIPParticipantRequest,
    TransferSIPParticipantRequest,
    AcceptWhatsAppCallRequest,
]
"""@private"""

# Ring window (seconds) assumed when a request doesn't set ringing_timeout;
# matches the server default. A dialing request must outlast it.
DEFAULT_RINGING_TIMEOUT = 30.0
"""@private"""

# A dialing request must outlast the ringing window, or it would abort before
# the call can be answered. Keep the request timeout at least this many seconds
# above the ringing timeout.
RINGING_TIMEOUT_MARGIN = 2.0
"""@private"""


def pin_ringing_timeout(request: DialRequest) -> None:
    """Set the ring window explicitly on a dialing request when the caller left it
    unset, so the derived request timeout doesn't depend on the server's default
    (which could change out from under us).

    @private
    """
    if not request.HasField("ringing_timeout"):
        request.ringing_timeout.seconds = int(DEFAULT_RINGING_TIMEOUT)


def dial_timeout(user_timeout: Optional[float], request: DialRequest) -> float:
    """Request timeout (seconds) for a phone-dialing call: the ring window plus a
    margin, so the request doesn't abort before the call can be answered. The
    ring window is the request's ringing_timeout when set, else
    DEFAULT_RINGING_TIMEOUT. A longer user_timeout is honored; a shorter one is
    raised to the floor.

    @private
    """
    if request.HasField("ringing_timeout"):
        ring: float = request.ringing_timeout.seconds
    else:
        ring = DEFAULT_RINGING_TIMEOUT
    floor = ring + RINGING_TIMEOUT_MARGIN
    return max(user_timeout if user_timeout else floor, floor)
