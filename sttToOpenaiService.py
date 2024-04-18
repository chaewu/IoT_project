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


class SttService:
    def __init__(self):
        self.input_source = sd.query_devices()
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 48000
        self.CHUNK = 1024
        self.RECORD_SECONDS = 5
        self.audio = pyaudio.PyAudio()
        self.config = {}
        self.files = {"file": open("audio_files/audio.wav", "rb")}
        self.getMediaIdData = {"config": json.dumps(self.config)}
        self.headers = {"Authorization": "bearer " + self.get_token()}
        self.getTokenData = {
            "client_id": os.getenv('CLIENT_ID'),
            "client_secret": os.getenv('CLIENT_SECRET')
        }
        self.urls = {
            "getTokenUrl": "https://openapi.vito.ai/v1/authenticate",
            "getMediaIdUrl": "https://openapi.vito.ai/v1/transcribe",
            "speachToTextUrl": "https://openapi.vito.ai/v1/transcribe" + self.get_media_id()
        }

    def save_wav_file(self):
        stream = self.audio.open(format=self.FORMAT,
                                 channels=self.CHANNELS,
                                 rate=self.RATE,
                                 input=True,
                                 input_device_index=0,
                                 frames_per_buffer=self.CHUNK)

        print("record started")

        # 프레임 데이터 저장
        frames = []

        # 녹음 시작
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = stream.read(self.CHUNK)
            frames.append(data)

        print("record ended")

        # 녹음 스트림 닫기
        stream.stop_stream()
        stream.close()
        self.audio.terminate()

        # 녹음된 데이터를 WAV 파일로 저장
        wavefile = wave.open("audio_files/audio.wav", 'wb')
        wavefile.setnchannels(self.CHANNELS)
        wavefile.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wavefile.setframerate(self.RATE)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()

        print("recorded data save with 'audio.wav'")

        delay()

    def get_token(self):
        resp = requests.post(self.urls["getTokenUrl"], data=self.getTokenData)
        resp.raise_for_status()
        token = resp.json().get('access_token')

        delay()

        return token

    def get_media_id(self):
        resp = requests.post(self.urls["getMediaIdUrl"], headers=self.headers, data=self.getMediaIdData,
                             files=self.files)

        resp.raise_for_status()
        media_id = resp.json().get('id')

        delay()

        return media_id

    def speach_to_text(self):
        resp = requests.get(self.urls["speachToTextUrl"], headers=self.headers)
        resp.raise_for_status()
        speach_to_text = resp.json()['results']['utterances'][0]['msg']  # json return data 중 msg string 부분 출력
        delay()

        return speach_to_text


class OpenAIService:
    def __init__(self, text):
        self.model = "gpt-3.5-turbo"
        self.client = OpenAI(api_key=os.getenv('OPEN_API_KEY'))

        self.messages = [
            {
                "role": "system",
                "content": "From now on, you are an AI model that recommends teas based on the user’s mood."
            },

            {
                "role": "user", "content": text
            }
        ]

    def openai_parser(self):
        completion = self.client.chat.completions.create(model=self.model, messages=self.messages)
        open_ai_text = completion.choices[0].message.content

        delay()

        return open_ai_text


if __name__ == '__main__':
    A = SttService()
    A.save_wav_file()
    userSpeach = A.speach_to_text()

    print("User : " + userSpeach)

    print("TeaBot : " + OpenAIService(userSpeach).openai_parser())
