from livekit.rtc import MediaDevices


def main():
    # Create a MediaDevices instance
    devices = MediaDevices()

    # Get default devices
    default_input_idx = devices.default_input_device()
    default_output_idx = devices.default_output_device()

    # List input devices
    print("=== Input Devices ===")
    input_devices = devices.list_input_devices()
    if not input_devices:
        print("No input devices found")
    else:
        for dev in input_devices:
            default_marker = " (default)" if dev["index"] == default_input_idx else ""
            print(
                f"  [{dev['index']}] {dev['name']}{default_marker} - "
                f"{dev['max_input_channels']} channels @ {dev['default_samplerate']} Hz"
            )

    print()

    # List output devices
    print("=== Output Devices ===")
    output_devices = devices.list_output_devices()
    if not output_devices:
        print("No output devices found")
    else:
        for dev in output_devices:
            default_marker = " (default)" if dev["index"] == default_output_idx else ""
            print(
                f"  [{dev['index']}] {dev['name']}{default_marker} - "
                f"{dev['max_output_channels']} channels @ {dev['default_samplerate']} Hz"
            )


if __name__ == "__main__":
    main()
