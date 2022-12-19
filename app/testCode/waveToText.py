#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer, SetLogLevel
import waveCob.cutCob as cb
from waveCob.voiceWave import AudioContorol
from pydub import AudioSegment
import os
import wave
import json

SetLogLevel(0)

AUDIO = "inputVoice.wav"
OUTPUTFILE = 'output.wav'
EFFECTFILE = 'beep.wav'
RECODETIME = int(input('recode time:'))
NGWORD = ['攻撃','嫌い','好き','ファック','ファッキュー']
if not os.path.exists("model"):
    print ("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
    exit (1)

w = AudioContorol(AUDIO,seconds=RECODETIME)
w.record() #レコード終了
wf = wave.open(AUDIO, "rb")
if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
    print ("Audio file must be WAV format mono PCM.")
    exit (1)

model = Model("model")
rec = KaldiRecognizer(model, wf.getframerate())
rec.SetWords(True)

search = [] 
sound = AudioSegment.from_wav(AUDIO)
while True:
    data = wf.readframes(4000)
    if len(data) <= 0:
        print(json.loads(rec.Result()))
        break
    if rec.AcceptWaveform(data):
        output = rec.Result()
        json_dict = json.loads(output)
        for word in json_dict['result']:
            if word['word'] in NGWORD:
                print('NG wordが検出されました')
                print(f'{word["start"]}から{word["end"]}の範囲を書き換えました。')
                sound = cb.chain(waveAudioSegment=sound,effectfile=EFFECTFILE,start=word['start'],end=word['end'])
            print('word:', word['word'])
            print('単語の開始:',word['start'])
            print('単語の終了:',word['end'])
            print()
sound.export(OUTPUTFILE,format='wav')

# print(json_dict['text'])

print(json.loads(rec.FinalResult())['text'])