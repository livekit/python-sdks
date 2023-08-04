## Whisper example

[Whisper](https://github.com/openai/whisper) is a speech-to-text model from OpenAI. It ordinarily requires 30s of input data for transcription, making it challenging to use in real-time applications. We work around this by limitation by padding shorter bursts of speech with silent audio packets.

## Run the demo

Change the URL and TOKEN inside the script

Clone whisper.cpp inside this directory

### Build a shared lib:

```
gcc -O3 -std=c11 -pthread -mavx -mavx2 -mfma -mf16c -fPIC -c ggml.c
g++ -O3 -std=c++11 -pthread --shared -fPIC -static-libstdc++ whisper.cpp ggml.o -o libwhisper.so
```

### Download a model you want to use:
./download-ggml-model.sh tiny.en

### Run whisper.py 
Run the script and connect another participant with a microphone:

You can use our Meet example or use the livekit-cli:
e.g: `livekit-cli load-test --room yourroom --audio-publishers 1`
