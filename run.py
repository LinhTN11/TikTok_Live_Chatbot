import openai
import winsound
import sys
import pytchat
import time
import re
import pyaudio
import keyboard
import wave
import threading
import json
import socket
import socketio
from emoji import demojize
# Handle missing config file
try:
    from config import *
except ModuleNotFoundError:
    print("Config file not found. Using default values...")
    api_key = None
    owner_name = "User"
from utils.translate import *
from utils.TTS import *
from utils.subtitle import *
from utils.promptMaker import *
from utils.twitch_config import *
import requests

# to help the CLI write unicode characters to the terminal
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

# use your own API Key, you can get it from https://openai.com/. I place my API Key in a separate file called config.py
# openai.api_key = api_key

conversation = []
# Create a dictionary to hold the message data
history = {"history": conversation}

mode = 0
total_characters = 0
chat = ""
chat_now = ""
chat_prev = ""
is_Speaking = False
blacklist = ["Nightbot", "streamelements"]

sio = socketio.Client()
tiktok_connected = False

# function to get the user's input audio
def record_audio():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    WAVE_OUTPUT_FILENAME = "input.wav"
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    frames = []
    print("Recording...")
    while keyboard.is_pressed('RIGHT_SHIFT'):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Stopped recording.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    transcribe_audio("input.wav")

# function to transcribe the user's audio
def transcribe_audio(file):
    global chat_now
    try:
        audio_file= open(file, "rb")
        # Translating the audio to English
        # transcript = openai.Audio.translate("whisper-1", audio_file)
        # Transcribe the audio to detected language
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        chat_now = transcript.text
        print ("Question: " + chat_now)
    except Exception as e:
        print("Error transcribing audio: {0}".format(e))
        return

    result = owner_name + " said " + chat_now
    conversation.append({'role': 'user', 'content': result})
    openai_answer()

# function to get an answer from OpenAI
def openai_answer():
    global total_characters, conversation

    total_characters = sum(len(d['content']) for d in conversation)

    while total_characters > 4000:
        try:
            # print(total_characters)
            # print(len(conversation))
            conversation.pop(2)
            total_characters = sum(len(d['content']) for d in conversation)
        except Exception as e:
            print("Error removing old messages: {0}".format(e))

    with open("conversation.json", "w", encoding="utf-8") as f:
        # Write the message data to the file in JSON format
        json.dump(history, f, indent=4)

    prompt = getPrompt()

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt,
        max_tokens=128,
        temperature=1,
        top_p=0.9
    )
    message = response['choices'][0]['message']['content']
    conversation.append({'role': 'assistant', 'content': message})

    translate_text(message)

# function to capture livechat from youtube
def yt_livechat(video_id):
        global chat

        live = pytchat.create(video_id=video_id)
        while live.is_alive():
        # while True:
            try:
                for c in live.get().sync_items():
                    # Ignore chat from the streamer and Nightbot, change this if you want to include the streamer's chat
                    if c.author.name in blacklist:
                        continue
                    # if not c.message.startswith("!") and c.message.startswith('#'):
                    if not c.message.startswith("!"):
                        # Remove emojis from the chat
                        chat_raw = re.sub(r':[^\s]+:', '', c.message)
                        chat_raw = chat_raw.replace('#', '')
                        # chat_author makes the chat look like this: "Nightbot: Hello". So the assistant can respond to the user's name
                        chat = c.author.name + ' berkata ' + chat_raw
                        print(chat)
                        
                    time.sleep(1)
            except Exception as e:
                print("Error receiving chat: {0}".format(e))

def twitch_livechat():
    global chat
    sock = socket.socket()

    sock.connect((server, port))

    sock.send(f"PASS {token}\n".encode('utf-8'))
    sock.send(f"NICK {nickname}\n".encode('utf-8'))
    sock.send(f"JOIN {channel}\n".encode('utf-8'))

    regex = r":(\w+)!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :(.+)"

    while True:
        try:
            resp = sock.recv(2048).decode('utf-8')

            if resp.startswith('PING'):
                    sock.send("PONG\n".encode('utf-8'))

            elif not user in resp:
                resp = demojize(resp)
                match = re.match(regex, resp)

                username = match.group(1)
                message = match.group(2)

                if username in blacklist:
                    continue
                
                chat = username + ' said ' + message
                print(chat)

        except Exception as e:
            print("Error receiving chat: {0}".format(e))

# translating is optional
def translate_text(text):
    global is_Speaking
    try:
        print("\nShiro trả lời: " + text)
        
        # Translate to Japanese
        tts = translate_google(text, "VI", "JA")
        
        # Convert remaining Latin characters to katakana
        tts = re.sub(r'[a-zA-Z]+', lambda m: convert_to_katakana(m.group()), tts)
        print("Japanese: " + tts)
        
        # Save all text files with proper paths and UTF-8 encoding
        base_path = "web/public"
        
        # Save Japanese response
        with open(f"{base_path}/japanese.txt", "w", encoding="utf-8") as f:
            f.write(tts)
            
        # Save Vietnamese response
        with open(f"{base_path}/output.txt", "w", encoding="utf-8") as f:
            f.write(text)
            
        # Save user chat
        with open(f"{base_path}/chat.txt", "w", encoding="utf-8") as f:
            f.write(chat_now)
            
        # TTS and audio playback
        voicevox_tts(tts)
        is_Speaking = True
        winsound.PlaySound("test.wav", winsound.SND_FILENAME)
        is_Speaking = False
        
    except Exception as e:
        print("Lỗi xử lý câu trả lời:", str(e))

def convert_to_katakana(text):
    # Bảng chuyển đổi Latin sang Katakana
    latin_to_kata = {
        'a': 'ア', 'i': 'イ', 'u': 'ウ', 'e': 'エ', 'o': 'オ',
        'ka': 'カ', 'ki': 'キ', 'ku': 'ク', 'ke': 'ケ', 'ko': 'コ',
        'sa': 'サ', 'shi': 'シ', 'su': 'ス', 'se': 'セ', 'so': 'ソ',
        'ta': 'タ', 'chi': 'チ', 'tsu': 'ツ', 'te': 'テ', 'to': 'ト',
        'na': 'ナ', 'ni': 'ニ', 'nu': 'ヌ', 'ne': 'ネ', 'no': 'ノ',
        'ha': 'ハ', 'hi': 'ヒ', 'fu': 'フ', 'he': 'ヘ', 'ho': 'ホ',
        'ma': 'マ', 'mi': 'ミ', 'mu': 'ム', 'me': 'メ', 'mo': 'モ',
        'ya': 'ヤ', 'yu': 'ユ', 'yo': 'ヨ',
        'ra': 'ラ', 'ri': 'リ', 'ru': 'ル', 're': 'レ', 'ro': 'ロ',
        'wa': 'ワ', 'wo': 'ヲ', 'n': 'ン'
    }
    
    # Chuyển về lowercase để dễ xử lý
    text = text.lower()
    # Thay thế các ký tự Latin bằng katakana tương ứng
    for rom, kata in latin_to_kata.items():
        text = text.replace(rom, kata)
    return text

def preparation():
    global conversation, chat_now, chat, chat_prev
    while True:
        # If the assistant is not speaking, and the chat is not empty, and the chat is not the same as the previous chat
        # then the assistant will answer the chat
        chat_now = chat
        if is_Speaking == False and chat_now != chat_prev:
            # Saving chat history
            conversation.append({'role': 'user', 'content': chat_now})
            chat_prev = chat_now
            openai_answer()
        time.sleep(1)

def get_local_ai_response(prompt):
    url = "http://127.0.0.1:1234/v1/chat/completions"
    headers = {
        "Content-Type": "application/json" 
    }
    data = {
        "messages": prompt,
        "temperature": 0.7,
        "top_p": 0.8,
        "max_tokens": 128,
        "presence_penalty": 0.5,
        "frequency_penalty": 0.5
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            print(f"Lỗi kết nối LM Studio (Status code: {response.status_code})")
            return "B-baka! Không thể kết nối với LM Studio... Hãy kiểm tra lại!"
            
    except requests.exceptions.ConnectionError:
        print("Không thể kết nối tới LM Studio - Hãy đảm bảo LM Studio đang chạy...")
        return "Hmmm... Không thể kết nối tới LM Studio. Bạn đã khởi động nó chưa?"
        
    except requests.exceptions.Timeout:
        print("LM Studio phản hồi quá chậm...") 
        return "LM Studio đang phản hồi chậm quá... Có lẽ tôi nên nghỉ ngơi một chút!"
        
    except Exception as e:
        print(f"Lỗi không xác định khi gọi LM Studio: {str(e)}")
        return "B-baka! Có gì đó không ổn với LM Studio..."

# Replace record_audio with text_input
def text_input():
    global chat_now
    chat_now = input("Nhập tin nhắn của bạn: ")
    print("\nBạn: " + chat_now)
    
    # Thêm "nói" thay vì "said" để phù hợp tiếng Việt
    result = f"{owner_name} nói: " + chat_now
    conversation.append({'role': 'user', 'content': result})
    openai_answer()

# Modify openai_answer to use local AI
def openai_answer():
    global total_characters, conversation

    total_characters = sum(len(d['content']) for d in conversation)

    while total_characters > 4000:
        try:
            conversation.pop(2)
            total_characters = sum(len(d['content']) for d in conversation)
        except Exception as e:
            print("Error removing old messages: {0}".format(e))

    with open("conversation.json", "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

    prompt = getPrompt()
    message = get_local_ai_response(prompt)
    conversation.append({'role': 'assistant', 'content': message})

    translate_text(message)

def getPrompt():
    prompt = []
    prompt.append(getIdentity("characterConfig/Shiro/identity_vi.txt"))
    prompt.append({
        "role": "system",
        "content": """NGUYÊN TẮC TRẢ LỜI:
        1. TRẢ LỜI ĐÚNG nội dung người dùng hỏi
        2. KHÔNG tự ý giới thiệu bản thân khi không được hỏi
        3. Giữ tính cách tsundere nhưng phải trả lời có nội dung
        4. Trả lời bằng tiếng Việt, chỉ dùng một số từ tiếng Nhật cơ bản
        5. Luôn chào lại khi được chào
        """
    })
    
    # Chỉ thêm tin nhắn cuối cùng vào prompt
    prompt.append({
        "role": "user", 
        "content": conversation[-1]['content']
    })
    
    return prompt

def connect_tiktok(username):
    global tiktok_connected
    try:
        sio.connect('http://localhost:3000')
        response = requests.post('http://localhost:3000/connect', 
                               json={'username': username})
        if response.status_code == 200:
            tiktok_connected = True
            print(f"Connected to TikTok live of {username}")
            return True
    except Exception as e:
        print(f"Failed to connect to TikTok: {str(e)}")
    return False

@sio.on('chat')
def on_tiktok_chat(data):
    global chat
    if data['nickname'] not in blacklist:
        chat = f"{data['nickname']} nói {data['comment']}"
        print(chat)

@sio.on('gift')
def on_tiktok_gift(data):
    global chat
    gift_message = ""
    diamond_count = data['diamondCount'] * data['repeatCount']
    
    if diamond_count >= 100:
        gift_message = f"{data['nickname']} đã tặng {data['repeatCount']} {data['giftName']} (trị giá {diamond_count} kim cương)!!!!"
    elif diamond_count >= 10:
        gift_message = f"{data['nickname']} tặng {data['repeatCount']} {data['giftName']}"
    else:
        gift_message = f"{data['nickname']} gửi {data['giftName']}"
        
    chat = f"GIFT: {gift_message}"
    print(chat)

def generate_subtitle(chat_now, text):
    base_path = "web/public"
    
    try:
        # Write output.txt (Vietnamese response)
        with open(f"{base_path}/output.txt", "w", encoding="utf-8") as f:
            words = text.split()
            lines = [words[i:i+10] for i in range(0, len(words), 10)]
            for line in lines:
                f.write(" ".join(line) + "\n")
                
        # Write chat.txt (user message)  
        with open(f"{base_path}/chat.txt", "w", encoding="utf-8") as f:
            words = chat_now.split()
            lines = [words[i:i+10] for i in range(0, len(words), 10)]
            for line in lines:
                f.write(" ".join(line) + "\n")
                
    except Exception as e:
        print("Lỗi ghi file subtitle:", str(e))

if __name__ == "__main__":
    try:
        # Changed mode description for Mode 1
        mode = input("Mode (1-Text Input, 2-Youtube Live, 3-Twitch Live, 4-TikTok Live): ")

        if mode == "1":
            print("Type your message and press Enter")
            while True:
                text_input()
            
        elif mode == "2":
            live_id = input("Livestream ID: ")
            # Threading is used to capture livechat and answer the chat at the same time
            t = threading.Thread(target=preparation)
            t.start()
            yt_livechat(live_id)

        elif mode == "3":
            # Threading is used to capture livechat and answer the chat at the same time
            print("To use this mode, make sure to change utils/twitch_config.py to your own config")
            t = threading.Thread(target=preparation)
            t.start()
            twitch_livechat()

        elif mode == "4":
            username = input("TikTok username (include @): ")
            if connect_tiktok(username):
                t = threading.Thread(target=preparation)
                t.start()
                while True:
                    if not tiktok_connected:
                        break
                    time.sleep(1)
            else:
                print("Failed to connect to TikTok live")
                
    except KeyboardInterrupt:
        if mode in ["2", "3", "4"]:
            t.join()
        if mode == "4":
            sio.disconnect()
        print("Stopped")

