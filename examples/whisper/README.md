## Whisper example

[Whisper](https://github.com/openai/whisper) is a speech-to-text model from OpenAI. It ordinarily requires 30s of input data for transcription, making it challenging to use in real-time applications. We work around this by limitation by padding shorter bursts of speech with silent audio packets.

## Run the demo

Change the URL and TOKEN inside the script

### Install dependencies:

`pip install whispercpp numpy`

### Run whisper.py 
Run the script and connect another participant with a microphone:

You can use our Meet example or use the livekit-cli:
e.g: `livekit-cli load-test --room yourroom --audio-publishers 1`
