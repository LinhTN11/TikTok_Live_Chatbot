import os
import torch
import requests
import urllib.parse
from utils.katakana import *

# https://github.com/snakers4/silero-models#text-to-speech
def silero_tts(tts, language, model, speaker):
    device = torch.device('cpu')
    torch.set_num_threads(4)
    local_file = 'model.pt'

    if not os.path.isfile(local_file):
        torch.hub.download_url_to_file(f'https://models.silero.ai/models/tts/{language}/{model}.pt',
                                    local_file)  

    model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
    model.to(device)

    example_text = "i'm fine thank you and you?"
    sample_rate = 48000

    audio_paths = model.save_wav(text=tts,
                                speaker=speaker,
                                sample_rate=sample_rate)
    
def voicevox_tts(tts):
    voicevox_url = 'http://localhost:50021'
    try:
        params_encoded = urllib.parse.urlencode({'text': tts, 'speaker': 14})  # Changed from 46 to 14
        request = requests.post(f'{voicevox_url}/audio_query?{params_encoded}')
        if request.status_code != 200:
            print("Error getting audio query from VoiceVox")
            return
            
        params_encoded = urllib.parse.urlencode({'speaker': 14, 'enable_interrogative_upspeak': True})  # Changed from 46 to 14
        request = requests.post(f'{voicevox_url}/synthesis?{params_encoded}', json=request.json())
        
        if request.status_code == 200:
            with open("test.wav", "wb") as outfile:
                outfile.write(request.content)
        else:
            print("Error synthesizing audio with VoiceVox")
    except Exception as e:
        print("Error with VoiceVox TTS:", str(e))

if __name__ == "__main__":
    voicevox_tts()
