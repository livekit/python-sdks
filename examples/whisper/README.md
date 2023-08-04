## Whisper example

Whisper is not really suited for realtime applications. 
The input requires to have 30s of data.
The way we can workaround this is by filling our data using silence

## Run the demo

Change the URL and TOKEN inside the script

Clone whisper.cpp inside this directory

### Build a sharted lib:

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