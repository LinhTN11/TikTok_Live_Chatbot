@echo off
echo Starting VoiceVox Docker container...
docker run --rm -it -p 50021:50021 voicevox/voicevox_engine:cpu-ubuntu20.04-latest
echo VoiceVox Docker container stopped.
pause
