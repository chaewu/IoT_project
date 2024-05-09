import sounddevice as sd
import time
import os
import dotenv
import json
import requests
import pyaudio
import wave
from openai import OpenAI

dotenv.load_dotenv('.env')


def delay():
    time.sleep(3)


def save_wav_file():
    stream = pyaudio.PyAudio().open(
        format=pyaudio.paInt16,
        channels=1,
        rate=48000,
        input=True,
        input_device_index=0,
        frames_per_buffer=1024
    )

    print("record started")

    # 프레임 데이터 저장
    frames = []

    # 녹음 시작
    for i in range(0, int(48000 / 1024 * 5)):
        data = stream.read(1024)
        frames.append(data)

    print("record ended")

    # 녹음 스트림 닫기
    stream.stop_stream()
    stream.close()
    pyaudio.PyAudio().terminate()

    # 녹음된 데이터를 WAV 파일로 저장
    wavefile = wave.open("audio_files/audio.wav", 'wb')
    wavefile.setnchannels(1)
    wavefile.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
    wavefile.setframerate(48000)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()

    print("recorded data save with 'audio.wav'")
    delay()


def get_token():
    resp = requests.post("https://openapi.vito.ai/v1/authenticate",
                         data={
                             "client_id": os.getenv('CLIENT_ID'),
                             "client_secret": os.getenv('CLIENT_SECRET')
                         })

    resp.raise_for_status()
    token = resp.json().get('access_token')
    delay()

    return token


def get_media_id():
    resp = requests.post("https://openapi.vito.ai/v1/transcribe",
                         headers={"Authorization": "bearer " + get_token()},
                         data={"config": json.dumps({})},
                         files={"file": open("audio_files/audio.wav", "rb")})

    resp.raise_for_status()
    media_id = resp.json().get('id')
    delay()

    return media_id


def speach_to_text():
    resp = requests.get("https://openapi.vito.ai/v1/transcribe/" + get_media_id(),
                        headers={"Authorization": "bearer " + get_token()})
    resp.raise_for_status()
    stt = resp.json()['results']['utterances'][0]['msg']  # json return data 중 msg string 부분 출력
    delay()

    return stt


def openai_parser(text):
    model = "gpt-3.5-turbo"
    client = OpenAI(api_key=os.getenv('OPEN_API_KEY'))
    messages = ({"role": "system",
                 "content": "From now on, you are an AI model that recommends teas based on the user’s mood."
                 },
                {"role": "user",
                 "content": text})

    completion = client.chat.completions.create(model=model, messages=messages)
    open_ai_text = completion.choices[0].message.content

    delay()

    return open_ai_text


save_wav_file()
stt = speach_to_text()
print(openai_parser(stt))
