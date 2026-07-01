from __future__ import annotations

from typing import Optional

# Calls that dial a phone (SIP CreateSIPParticipant with wait_until_answered and
# TransferSIPParticipant; WhatsApp AcceptWhatsAppCall with wait_until_answered)
# take longer than a normal request.
DIAL_TIMEOUT = 30.0
"""@private"""

# A dialing request must outlast the ringing window, or it would abort before
# the call can be answered. Keep the request timeout at least this many seconds
# above the request's ringing_timeout.
RINGING_TIMEOUT_MARGIN = 2.0
"""@private"""


def dial_timeout(user_timeout: Optional[float], request) -> float:
    """Request timeout (seconds) for a phone-dialing call: the user-supplied
    value (or the dial default) raised, when needed, to stay at least
    RINGING_TIMEOUT_MARGIN above the request's ringing_timeout.

    @private
    """
    effective = user_timeout if user_timeout else DIAL_TIMEOUT
    if request.HasField("ringing_timeout"):
        effective = max(effective, request.ringing_timeout.seconds + RINGING_TIMEOUT_MARGIN)
    return effective
