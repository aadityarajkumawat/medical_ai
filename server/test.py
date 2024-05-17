from gradio_client import Client

d = {"this": "is a value"}

client = Client(
    "https://adityaedy01-mms.hf.space/",
    hf_token="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",
)
# out = client.view_api(return_format="str")

# with open("api.json", "w") as f:
#     f.write(out)


result = client.predict(
    "haye, sidee wax u socdaan?", "som (Somali)", 1, api_name="/predict_1"
)

audio_path, text = result

print(audio_path, text)

from pydub import AudioSegment


def convert_wav_to_mp3(wav_file_path, mp3_file_path):
    # Load the WAV file
    audio = AudioSegment.from_wav(wav_file_path)

    # Export as MP3
    audio.export(mp3_file_path, format="mp3")
    print(f"Converted {wav_file_path} to {mp3_file_path}")


convert_wav_to_mp3(audio_path, "./output.mp3")
# i = 0
# while result.running():
#     i += 1

# print(result.result())


# client = Client("abidlabs/whisper-large-v2")  # connecting to a Hugging Face Space
# d = client.predict("/Users/aditya/me.m4a", api_name="/predict")

# print(d)

client = Client("https://adityaedy01-mms.hf.space/")
result = client.predict(
    "Record from Mic",  # str  in 'Audio input' Radio component
    "/Users/aditya/me.m4a",  # str (filepath or URL to file) in 'Use mic' Audio component
    "/Users/aditya/me.m4a",  # str (filepath or URL to file) in 'Upload file' Audio component
    "eng (English)",
    api_name="/predict",
)
print(result)
