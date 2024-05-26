import replicate

import os
import dotenv

dotenv.load_dotenv()

os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")


def image_to_text(image_path: str):
    input = {"image": image_path, "prompt": "Describe this image."}
    output = replicate.run(
        "lucataco/moondream2:392a53ac3f36d630d2d07ce0e78142acaccc338d6caeeb8ca552fe5baca2781e",
        input=input,
    )

    response = ""

    for line in output:
        response += line

    print(response)


image_to_text(
    "https://replicate.delivery/pbxt/KZKNhDQHqycw8Op7w056J8YTX5Bnb7xVcLiyB4le7oUgT2cY/moondream2.png"
)
