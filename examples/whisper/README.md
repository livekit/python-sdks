## Whisper<>LiveKit example

Whisper is not really suited for realtime applications. 
The input requires to have 30s of data.
The way we can workaround this is by filling our data using silence

## Getting started

Clone whisper.cpp inside this directory

Build a sharted lib:

```
gcc -O3 -std=c11   -pthread -mavx -mavx2 -mfma -mf16c -fPIC -c ggml.c
g++ -O3 -std=c++11 -pthread --shared -fPIC -static-libstdc++ whisper.cpp ggml.o -o libwhisper
```

Download a model you want to use:
./download-ggml-model.sh tiny.en

Then run whisper.py and connect another participant with a microphone 