"""
Audio dB meter utilities for LiveKit Python SDK examples.

This module provides functions to calculate and display audio levels in decibels (dB)
from raw audio samples, useful for monitoring microphone input and room audio levels.
"""

import math
import queue
import time
from typing import List

# dB meter configuration constants
DB_METER_UPDATE_INTERVAL_MS = 50  # Update every 50ms
MIC_METER_WIDTH = 25  # Width of the mic dB meter bar
ROOM_METER_WIDTH = 25  # Width of the room dB meter bar


def calculate_db_level(samples: List[int]) -> float:
    """
    Calculate decibel level from audio samples.

    Args:
        samples: List of 16-bit audio samples

    Returns:
        dB level as float. Returns -60.0 for silence/empty samples.
    """
    if not samples:
        return -60.0  # Very quiet

    # Calculate RMS (Root Mean Square)
    sum_squares = sum(
        (sample / 32767.0) ** 2  # Normalize to -1.0 to 1.0 range
        for sample in samples
    )

    rms = math.sqrt(sum_squares / len(samples))

    # Convert to dB (20 * log10(rms))
    if rms > 0.0:
        return 20.0 * math.log10(rms)
    else:
        return -60.0  # Very quiet


def get_meter_color(db_level: float, position_ratio: float) -> str:
    """
    Get ANSI color code based on dB level and position in meter.

    Args:
        db_level: Current dB level
        position_ratio: Position in meter (0.0 to 1.0)

    Returns:
        ANSI color code string
    """
    # Determine color based on both dB level and position in the meter
    if db_level > -6.0 and position_ratio > 0.85:
        return "\x1b[91m"  # Bright red - clipping/very loud
    elif db_level > -12.0 and position_ratio > 0.7:
        return "\x1b[31m"  # Red - loud
    elif db_level > -18.0 and position_ratio > 0.5:
        return "\x1b[93m"  # Bright yellow - medium-loud
    elif db_level > -30.0 and position_ratio > 0.3:
        return "\x1b[33m"  # Yellow - medium
    elif position_ratio > 0.1:
        return "\x1b[92m"  # Bright green - low-medium
    else:
        return "\x1b[32m"  # Green - low


def format_single_meter(db_level: float, meter_width: int, meter_label: str) -> str:
    """
    Format a single dB meter with colors.

    Args:
        db_level: dB level to display
        meter_width: Width of the meter bar in characters
        meter_label: Label text for the meter

    Returns:
        Formatted meter string with ANSI colors
    """
    # ANSI color codes
    COLOR_RESET = "\x1b[0m"
    COLOR_DIM = "\x1b[2m"

    db_clamped = max(-60.0, min(0.0, db_level))
    normalized = (db_clamped + 60.0) / 60.0  # Normalize to 0.0-1.0
    filled_width = int(normalized * meter_width)

    meter = meter_label

    # Add the dB value with appropriate color
    if db_level > -6.0:
        db_color = "\x1b[91m"  # Bright red
    elif db_level > -12.0:
        db_color = "\x1b[31m"  # Red
    elif db_level > -24.0:
        db_color = "\x1b[33m"  # Yellow
    else:
        db_color = "\x1b[32m"  # Green

    meter += f"{db_color}{db_level:>7.1f}{COLOR_RESET} "

    # Add the visual meter with colors
    meter += "["
    for i in range(meter_width):
        position_ratio = i / meter_width

        if i < filled_width:
            color = get_meter_color(db_level, position_ratio)
            meter += f"{color}█{COLOR_RESET}"  # Full block for active levels
        else:
            meter += f"{COLOR_DIM}░{COLOR_RESET}"  # Light shade for empty

    meter += "]"
    return meter


def format_dual_meters(mic_db: float, room_db: float) -> str:
    """
    Format both dB meters on the same line.

    Args:
        mic_db: Microphone dB level
        room_db: Room audio dB level

    Returns:
        Formatted dual meter string
    """
    mic_meter = format_single_meter(mic_db, MIC_METER_WIDTH, "Mic: ")
    room_meter = format_single_meter(room_db, ROOM_METER_WIDTH, "  Room: ")

    return f"{mic_meter}{room_meter}"


def display_dual_db_meters(mic_db_receiver, room_db_receiver, room_name: str = "Audio Levels Monitor") -> None:
    """
    Display dual dB meters continuously until interrupted.

    Args:
        mic_db_receiver: Queue or receiver for microphone dB levels
        room_db_receiver: Queue or receiver for room dB levels
        room_name: Name of the room to display as the title
    """
    try:
        last_update = time.time()
        current_mic_db = -60.0
        current_room_db = -60.0

        print()  # Start on a new line
        print(f"\x1b[92mRoom [{room_name}]\x1b[0m")
        print("\x1b[2m────────────────────────────────────────────────────────────────────────────────\x1b[0m")

        while True:
            # Check for new data (non-blocking)
            try:
                while True:  # Drain all available data
                    mic_db = mic_db_receiver.get_nowait()
                    current_mic_db = mic_db
            except queue.Empty:
                pass  # No more data available

            try:
                while True:  # Drain all available data
                    room_db = room_db_receiver.get_nowait()
                    current_room_db = room_db
            except queue.Empty:
                pass  # No more data available

            # Update display at regular intervals
            current_time = time.time()
            if current_time - last_update >= DB_METER_UPDATE_INTERVAL_MS / 1000.0:
                # Clear current line and display meters in place
                print(f"\r\x1b[K{format_dual_meters(current_mic_db, current_room_db)}", end="", flush=True)
                last_update = current_time

            # Small sleep to prevent busy waiting
            time.sleep(0.01)

    except KeyboardInterrupt:
        print()  # Move to next line after Ctrl+C


def display_single_db_meter(db_receiver, label: str = "Mic Level: ") -> None:
    """
    Display a single dB meter continuously until interrupted.

    Args:
        db_receiver: Queue or receiver for dB levels
        label: Label for the meter display
    """
    try:
        last_update = time.time()
        current_db = -60.0
        first_display = True

        if first_display:
            print()  # Start on a new line
            print(f"\x1b[92m{label}\x1b[0m")
            print("\x1b[2m────────────────────────────────────────\x1b[0m")
            first_display = False

        while True:
            # Check for new data (non-blocking)
            try:
                while True:  # Drain all available data
                    db_level = db_receiver.get_nowait()
                    current_db = db_level
            except queue.Empty:
                pass  # No more data available

            # Update display at regular intervals
            current_time = time.time()
            if current_time - last_update >= DB_METER_UPDATE_INTERVAL_MS / 1000.0:
                # Clear current line and display meter in place
                meter = format_single_meter(current_db, 40, label)
                print(f"\r\x1b[K{meter}", end="", flush=True)
                last_update = current_time

            # Small sleep to prevent busy waiting
            time.sleep(0.01)

    except KeyboardInterrupt:
        print()  # Move to next line after Ctrl+C


# Example usage and testing functions
def demo_db_meter() -> None:
    """Demo function to test dB meter functionality."""
    import random

    # Simulate some test data
    class MockReceiver:
        def __init__(self):
            self.data = []

        def get_nowait(self):
            if not self.data:
                # Generate random dB value between -60 and 0
                self.data.append(random.uniform(-60, 0))
            return self.data.pop(0)

    mic_receiver = MockReceiver()
    room_receiver = MockReceiver()

    print("Starting dB meter demo (Ctrl+C to stop)...")
    display_dual_db_meters(mic_receiver, room_receiver)


if __name__ == "__main__":
    demo_db_meter()
