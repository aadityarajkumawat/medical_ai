from flask import Flask, request

from transformers import AutoModelForCausalLM
import os

from transformers import AutoTokenizer
from PIL import Image

import subprocess

subprocess.run(
    [
        "pip3",
        "install",
        "torch",
        "torchvision",
        "torchaudio",
        "--index-url",
        "https://download.pytorch.org/whl/cpu",
    ]
)

model = AutoModelForCausalLM.from_pretrained(
    "vikhyatk/moondream2", trust_remote_code=True
)

model_id = "vikhyatk/moondream2"
revision = "2024-05-08"

tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)


def image_to_text(image_path: str):
    image = Image.open(image_path)
    enc_image = model.encode_image(image)
    return model.answer_question(enc_image, "Describe this image.", tokenizer)


app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/image_to_text", methods=["POST"])
def image_to_text_endpoint():
    json = request.json
    url = json["url"]
    return image_to_text(url)


if __name__ == "__main__":
    app.run(port=os.getenv("PORT"), host="0.0.0.0")
