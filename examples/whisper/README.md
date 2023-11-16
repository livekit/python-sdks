## Whisper example

[Whisper](https://github.com/openai/whisper) is a speech-to-text model from OpenAI. It ordinarily requires 30s of input data for transcription, making it challenging to use in real-time applications. We work around this limitation by padding shorter bursts of speech with silent audio packets.

## How to run the demo

### Step 1:
Change the URL and TOKEN inside the whisper.py script to use your LiveKit websocket URL and a valid session token

### Step 2:
Clone [whisper.cpp](https://github.com/ggerganov/whisper.cpp) inside this directory

### Step 3:
Build a shared library:
```
cd whisper.cpp
gcc -O3 -std=c11 -pthread -mavx -mavx2 -mfma -mf16c -fPIC -c ggml.c
g++ -O3 -std=c++11 -pthread --shared -fPIC -static-libstdc++ whisper.cpp ggml.o -o libwhisper.so
```

### Step 4: 
Download a model you want to use, for example:
```
./models/download-ggml-model.sh tiny.en
```

### Step 5: 
Rename the shared object library if you're on Windows or macOS:
1. If Windows, rename `libwhisper.so` to `libwhisper.dll`
2. If macOS, rename `libwhisper.so` to `libwhisper.dylib`

### Step 6:
Run the whisper.py script:
```
python3 whisper.py
```

### Step 7:
Connect another participant to the room and publish a microphone stream. To do this quickly, you can use our [Meet example](https://meet.livekit.io/?tab=custom) or use the [livekit-cli](https://github.com/livekit/livekit-cli):
```
livekit-cli load-test --room yourroom --audio-publishers 1
```
