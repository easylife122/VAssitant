import speech_recognition as sr
# import pyttsx3
import openai
import io
import os
from pydub import AudioSegment
import whisper
import argparse
from pythonosc import udp_client


# openai ChatBot model
openai.api_key = ' '

# Text to Speech pyttsx
'''
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
'''

# Text to Speech Whisper
audio_model = whisper.load_model('base')
option = whisper.DecodingOptions(fp16=False)

# Sound Recognize
r = sr.Recognizer()
mic = sr.Microphone(device_index=1)

conversation = ''
user_name = 'Dan'
bot_name = 'John'

while True:
    with mic as source:
        print('\n Listening...')
        r.adjust_for_ambient_noise(source, duration=0.2)
        audio = r.listen(source)
    print("no longer listening")

    try:
        # user_input = r.recognize_google(audio, language="zh-tw")

        # Save mic input into .wav file
        data = io.BytesIO(audio.get_wav_data())
        audio_clip = AudioSegment.from_file(data)
        filename = os.path.join('RecordClip.wav')
        audio_clip.export(filename, format="wav")
        audio_data = filename

    except:
        continue

    # Audio to text
    result = audio_model.transcribe(audio_data)
    print(result['text'])

    #Send result to GPT-3
    prompt = user_name + ':' + result['text'] + '\n' + bot_name + ':'
    conversation += prompt

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=conversation,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    response_str = response["choices"][0]['text'].replace('\n','')
    response_str = response_str.split(
        user_name + ':' ,1)[0].split(bot_name+':',1)[0]

    conversation+= response_str +'\n'
    print(response_str)

    # Send data via OSC
    if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument("--ip", default="127.0.0.1", help='The ip of the OSC server')
        parser.add_argument("--port", type=int, default=7000, help='The port of the OSC server is listening on')

        args = parser.parse_args()
        client = udp_client.SimpleUDPClient(args.ip, args.port)
        client.send_message('/GPT', response_str)
        print("Send")


    # Delete Audio file
    os.remove(audio_data)



    # engine.say(response_str)
    # engine.runAndWait()
