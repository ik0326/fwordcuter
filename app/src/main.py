import streamlit as st
from vosk import Model, KaldiRecognizer, SetLogLevel
import waveCob.cutCob as cb
from waveCob.voiceWave import AudioContorol
from pydub import AudioSegment
import pandas as pd
import os
import wave
import json

SETINGJSON = "../include/userdic.json"

def setSoundEffectFile() -> str:
    #もし、選択された効果音ファイルがあれば、そのファイルパスを渡す。
    pass

def record(recodeTime:int, ngword:list, soundEfect:str="../sounds/beep.wav"):
    #!/usr/bin/env python3

    AUDIO = "../include/inputVoice.wav"
    OUTPUTFILE = '../output/output.wav'
    EFFECTFILE = '../sounds/beep.wav' 
    RECODETIME = recodeTime
    NGWORD = ngword
    if not os.path.exists("../include/model"):
        print ("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
        exit (1)

    w = AudioContorol(AUDIO,seconds=RECODETIME)
    st.write("record start")
    w.record() #レコード終了
    st.write("record finish")
    wf = wave.open(AUDIO, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print ("Audio file must be WAV format mono PCM.")
        exit (1)

    model = Model("../include/model")
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    sound = AudioSegment.from_wav(AUDIO)
    bar = st.progress(0)
    cnt:int = 0
    while True:
        data = wf.readframes(4000)
        if len(data) <= 0:
            print(json.loads(rec.Result()))
            break
        if rec.AcceptWaveform(data):
            output = rec.Result()
            json_dict = json.loads(output)
            st.write(json_dict['text'])
            st.dataframe(json_dict)
            for word in json_dict['result']:
                if word['word'] in NGWORD:
                    print('NG wordが検出されました')
                    print(f'{word["start"]}から{word["end"]}の範囲を書き換えました。')
                    sound = cb.chain(waveAudioSegment=sound,effectfile=EFFECTFILE,start=word['start'],end=word['end'])
                print('word:', word['word'])
                print('単語の開始:',word['start'])
                print('単語の終了:',word['end'])
                print()
        cnt += 1
        if cnt > 99:continue
        bar.progress(cnt)
    bar.progress(100)
    sound.export(OUTPUTFILE,format='wav')

    # print(json_dict['text'])

    print(json.loads(rec.FinalResult())['text'])

def main():
    try:
        with open(SETINGJSON) as f:
            NG = json.load(f)
        if NG['ユーザー辞書'] == []:
            NG = {"ユーザー辞書":["嫌い","あほ"],"config":{"snow":True}}
            st.warning("辞書が空だったため、適当に補いました。")
            
    except:
        NG = {"ユーザー辞書":["嫌い","あほ"],"config":{"snow":True}}
        st.warning("辞書が空だったため、適当に補いました。")
    NG_list = NG['ユーザー辞書']
    st.title("Fワード検出機")
    tab1,tab2 = st.tabs(['実行',"settings"])
    st.sidebar.title("設定項目")
    recodeSeconds = st.sidebar.slider("録音時間(second)",min_value=1,max_value=30,help="録音したい時間を選択してください。")
    st.sidebar.write("選択秒数：",recodeSeconds)
    
    with tab2:
        ipt = st.text_input("write word",key="setword") 
        add_column, del_column = st.columns(2)
        with add_column:
            if st.button("追加"):
                if ipt == "":st.warning("追加したい単語をテキストボックスに入力してください。")
                if ipt not in NG['ユーザー辞書'] and ipt != "":
                    if len(ipt) > 20:
                        st.error("単語が長すぎます。")
                    else:
                        NG['ユーザー辞書'].append(ipt)
                        with open(SETINGJSON, "w") as f:
                            json.dump(NG, f, indent=4)
                        st.info("登録しました。")
                else:
                    if ipt != "":st.error("すでに登録されています。")
                

        with del_column:
            if st.button("削除"):
                if ipt == "":
                    st.warning("削除したい単語をテキストボックスに入力してください。")
                elif ipt not in NG["ユーザー辞書"]:
                    st.error("該当の単語は存在しません。")
                else:
                    NG['ユーザー辞書'].remove(ipt)
                    with open(SETINGJSON,"w") as f:
                        json.dump(NG, f, indent=4)
                        st.info("正常に削除しました。")
                
        st.dataframe(pd.DataFrame(NG['ユーザー辞書']))
        NG["config"]["snow"] = st.checkbox("snowエフェクトをオフにする",value=NG['config']['snow'])

    with tab1:
        ngword = st.multiselect(
        '遮断する言葉を選んでください', NG_list
        )
        NGWORD = [str(word) for word in ngword]

        if st.button("録音"):
            st.write('Running...')
            record(recodeSeconds,NGWORD)
            st.write('選択秒数：',recodeSeconds)
            st.subheader("NGワードを削除しました✨")
            st.audio("../output/output.wav", format="audio/wav", start_time=0, sample_rate=None)
            st.download_button(label="download",data="",file_name="output.wav")
            if not NG['config']['snow']:
                st.snow()
    with open(SETINGJSON, "w") as f:
        json.dump(NG, f, indent=4)

if __name__ == '__main__':
    main()