import sounddevice as sd
import time
import os
import dotenv
import json
import requests
import pyaudio
import wave
from openai import OpenAI


def delay():
    time.sleep(5)


class STTService:
    def __init__(self):
        self.input_source = sd.query_devices()  # 음성 데이터 입력 input 확인
        dotenv.load_dotenv('.env')
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 48000
        self.CHUNK = 1024
        self.RECORD_SECONDS = 5
        self.audio = pyaudio.PyAudio()

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
        wavefile = wave.open("audio_files/depress.wav", 'wb')
        wavefile.setnchannels(self.CHANNELS)
        wavefile.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wavefile.setframerate(self.RATE)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()

        print("recorded data save with 'audio.wav'")

        delay()

    def get_token(self):
        resp = requests.post(
            'https://openapi.vito.ai/v1/authenticate',
            data={'client_id': os.getenv('CLIENT_ID'),
                  'client_secret': os.getenv('CLIENT_SECRET')}
        )
        resp.raise_for_status()
        token = resp.json().get('access_token')
        delay()

        return token

    def get_media_id(self, token):
        config = {}
        resp = requests.post(
            'https://openapi.vito.ai/v1/transcribe',
            headers={'Authorization': 'bearer ' + token},
            data={'config': json.dumps(config)},
            files={'file': open('audio_files/depress.wav', 'rb')}
        )
        resp.raise_for_status()
        media_id = resp.json().get('id')
        delay()

        return media_id

    def stt(self, token, media_id):
        resp = requests.get(
            'https://openapi.vito.ai/v1/transcribe/' + media_id,
            headers={'Authorization': 'bearer ' + token},
        )
        resp.raise_for_status()
        speach_to_text = resp.json()['results']['utterances'][0]['msg']  # json return data 중 msg string 부분 출력
        delay()

        return speach_to_text


class OpenAIService:
    def __init__(self):
        dotenv.load_dotenv('.env')

    def openai_parser(self, text):
        client = OpenAI(api_key=os.getenv('OPEN_API_KEY'))

        model = "gpt-3.5-turbo"
        query = text
        messages = [{"role": "system",
                     "content": "From now on, you are an AI model that recommends teas based on the user’s mood."},
                    {"role": "user",
                     "content": query}]

        completion = client.chat.completions.create(model=model, messages=messages)
        open_ai_text = completion.choices[0].message.content
        delay()

        return open_ai_text


if __name__ == '__main__':
    stt = STTService()
    openai = OpenAIService()

    # stt.save_wav_file()
    api_token = stt.get_token()
    result = stt.stt(api_token, stt.get_media_id(api_token))

    print("User : " + result)
    print("Tea Bot : " + openai.openai_parser(result))
