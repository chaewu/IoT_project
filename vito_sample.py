import sounddevice as sd
import time
import os
import dotenv
import json
import requests
import pyaudio
import wave


def delay():
    time.sleep(3)


class SpeachToText:
    input_source = sd.query_devices()  # 음성 데이터 입력 input 확인
    dotenv.load_dotenv('.env')
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 48000
    CHUNK = 1024
    RECORD_SECONDS = 5

    def __init__(self, audio):
        self.audio = audio

    def save_wav_file(self):
        stream = self.audio.open(format=self.FORMAT,
                                 channels=self.CHANNELS,
                                 rate=self.RATE,
                                 input=True,
                                 input_device_index=1,
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
        wavefile = wave.open("audio.wav", 'wb')
        wavefile.setnchannels(self.CHANNELS)
        wavefile.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wavefile.setframerate(self.RATE)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()

        print("recorded data save with 'audio.wav'")

        delay()

    def get_token():
        resp = requests.post(
            'https://openapi.vito.ai/v1/authenticate',
            data={'client_id': os.getenv('CLIENT_ID'),
                  'client_secret': os.getenv('CLIENT_SECRET')}
        )
        resp.raise_for_status()
        token = resp.json().get('access_token')
        delay()

        return token

    def get_media_id(token):
        config = {}
        resp = requests.post(
            'https://openapi.vito.ai/v1/transcribe',
            headers={'Authorization': 'bearer ' + token},
            data={'config': json.dumps(config)},
            files={'file': open('audio.wav', 'rb')}
        )
        resp.raise_for_status()
        media_id = resp.json().get('id')
        delay()

        return media_id

    def stt(token, media_id):
        resp = requests.get(
            'https://openapi.vito.ai/v1/transcribe/' + media_id,
            headers={'Authorization': 'bearer ' + token},
        )
        resp.raise_for_status()
        speach_to_text = resp.json()['results']['utterances'][0]['msg']  # json return data 중 msg string 부분 출력
        delay()

        return speach_to_text

    save_wav_file(p)
    getToken = get_token()
    getMediaId = get_media_id(getToken)
    getSTT = stt(getToken, getMediaId)


if __name__ == '__main__':
    p = pyaudio.PyAudio()
    stt = SpeachToText(p)
