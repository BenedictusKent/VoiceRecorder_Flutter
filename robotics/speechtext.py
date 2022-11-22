import speech_recognition as sr
import Levenshtein

# def getSoundexList(arr):
#     res = [soundex(x) for x in arr]
#     return res

filename = "E5.wav"

r = sr.Recognizer()

with sr.AudioFile(filename) as source:
    audio_data = r.record(source)
    text = r.recognize_google(audio_data)
    print(text)

# while True:
#     try:
#         with sr.Microphone() as mic:
#             recognizer.adjust_for_ambient_noise(mic, duration=0.2)
#             audio = recognizer.listen(mic)
#             text = recognizer.recognize_google(audio)
#             print(text)
#     except sr.UnknownValueError():
#         recognizer = sr.Recognizer()
#         continue

# Valid commands
piece = ['car', 'horse', 'elephant', 'general', 'king', 'canon', 'soldier']
position = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']

# Analyze commands
curr_piece, curr_pos = text.split()
curr_piece = curr_piece.lower()
curr_pos = curr_pos.lower()
if curr_piece in piece:
    print(curr_piece, end=' ')
# else:
#     print(soundex(curr_piece))
#     print(getSoundexList(curr_piece))
