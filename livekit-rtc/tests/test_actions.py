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

"""Unit tests for the actions catalog and describe wire formats. No server required."""

from __future__ import annotations

import json

from livekit.rtc.actions import (
    ActionEntry,
    ActionSummary,
    parse_actions,
    parse_describe,
    serialize_actions,
    serialize_describe,
)


def test_catalog_omits_empty_summary() -> None:
    raw = serialize_actions(
        [ActionSummary("read_file", "Read a file"), ActionSummary("ping"), ActionSummary("x", "")]
    )
    assert json.loads(raw) == [
        {"name": "read_file", "summary": "Read a file"},
        {"name": "ping"},
        {"name": "x"},
    ]


def test_catalog_round_trip() -> None:
    summaries = [ActionSummary("read_file", "Read a file"), ActionSummary("ping")]
    assert parse_actions(serialize_actions(summaries)) == summaries


def test_parse_actions_ignores_malformed() -> None:
    assert parse_actions(None) == []
    assert parse_actions("not json") == []
    assert parse_actions('{"name": "a"}') == []
    assert parse_actions('[{"summary": "no name"}, {"name": "a"}]') == [ActionSummary("a")]


def test_describe_round_trip() -> None:
    entries = [
        ActionEntry("write_file", "Write a file", {"type": "object"}, "confirm"),
        ActionEntry("read_file", "Read a file"),
    ]
    raw = serialize_describe(entries)
    assert json.loads(raw)["actions"][0] == {
        "name": "write_file",
        "description": "Write a file",
        "parameters": {"type": "object"},
        "consent": "confirm",
    }
    assert parse_describe(raw) == entries
