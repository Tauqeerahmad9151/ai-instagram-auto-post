import os
import time
import random
from urllib.parse import quote

import requests


IG_ID = "17841403495401351"
IG_TOKEN = os.getenv("IG_ACCESS_TOKEN")
POLLINATIONS_KEY = os.getenv("POLLINATIONS_API_KEY")

API_VERSION = "v23.0"


TOPICS = [
    "Mind blowing artificial intelligence facts",
    "A futuristic Indian city in 2050",
    "The future of robots and humans",
    "Amazing technology of the future",
    "A mysterious AI discovery",
    "The future of space technology",
    "Future technology changing everyday life",
    "What the world may look like in 2100"
]


# =========================
# CHECK KEYS
# =========================

if not IG_TOKEN:
    print("ERROR: IG_ACCESS_TOKEN missing")
    raise SystemExit

if not POLLINATIONS_KEY:
    print("ERROR: POLLINATIONS_API_KEY missing")
    raise SystemExit


# =========================
# TOPIC
# =========================

topic = random.choice(TOPICS)

print()
print("==============================")
print("AUTOMATIC INSTAGRAM POST")
print("==============================")
print("Topic:", topic)


# =========================
# AI IMAGE
# =========================

prompt = f"""
Create a photorealistic cinematic Instagram image about:

{topic}

Vertical 4:5 composition.
Highly detailed.
Modern cinematic lighting.
Eye-catching social media image.
No text.
No watermark.
No logo.
"""

print()
print("Generating AI image...")


image_url = (
    "https://gen.pollinations.ai/image/"
    + quote(prompt, safe="")
    + "?model=flux&width=1080&height=1350&nologo=true"
)


image_response = requests.get(
    image_url,
    headers={
        "Authorization": f"Bearer {POLLINATIONS_KEY}"
    },
    timeout=180
)


print("Image status:", image_response.status_code)


content_type = image_response.headers.get(
    "Content-Type",
    ""
)

print("Image type:", content_type)


if image_response.status_code != 200:
    print("IMAGE GENERATION FAILED")
    print(image_response.text[:2000])
    raise SystemExit


if not content_type.startswith("image/"):
    print("Generated response is not an image.")
    raise SystemExit


with open("generated.jpg", "wb") as f:
    f.write(image_response.content)


print("AI image saved: generated.jpg")


# =========================
# AI CAPTION
# =========================

print()
print("Generating caption...")


caption_prompt = f"""
Create a short engaging Instagram caption about:

{topic}

Use Hindi/Hinglish.
Make it interesting and viral.
Use a few emojis.
Add exactly 5 relevant hashtags.
No markdown.
"""


caption_response = requests.post(
    "https://gen.pollinations.ai/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {POLLINATIONS_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "openai",
        "messages": [
            {
                "role": "user",
                "content": caption_prompt
            }
        ]
    },
    timeout=120
)


print("Caption status:", caption_response.status_code)


if caption_response.status_code != 200:
    print("CAPTION ERROR")
    print(caption_response.text[:2000])
    raise SystemExit


caption = (
    caption_response
    .json()["choices"][0]["message"]["content"]
    .strip()
)


print()
print("CAPTION:")
print(caption)


# =========================
# UPLOAD IMAGE
# =========================

print()
print("Uploading image...")


with open("generated.jpg", "rb") as image_file:

    upload_response = requests.post(
        "https://catbox.moe/user/api.php",

        data={
            "reqtype": "fileupload"
        },

        files={
            "fileToUpload": (
                "generated.jpg",
                image_file,
                "image/jpeg"
            )
        },

        timeout=120
    )


print(
    "Upload status:",
    upload_response.status_code
)


if upload_response.status_code != 200:

    print("IMAGE UPLOAD FAILED")
    print(upload_response.text)
    raise SystemExit


public_image_url = upload_response.text.strip()


if not public_image_url.startswith("http"):

    print("Invalid image URL:")
    print(public_image_url)
    raise SystemExit


print()
print("PUBLIC IMAGE URL:")
print(public_image_url)


# =========================
# VERIFY PUBLIC IMAGE
# =========================

print()
print("Public image URL ready. Sending to Instagram...")

# =========================
# INSTAGRAM CONTAINER
# =========================

print()
print("Creating Instagram container...")


create_url = (
    f"https://graph.instagram.com/"
    f"{API_VERSION}/{IG_ID}/media"
)


create_response = requests.post(

    create_url,

    data={
        "image_url": public_image_url,
        "caption": caption,
        "access_token": IG_TOKEN
    },

    timeout=120
)


print()
print("CONTAINER RESPONSE:")
print(create_response.text)


if not create_response.ok:

    print()
    print("CONTAINER CREATION FAILED.")
    raise SystemExit


creation_id = (
    create_response
    .json()
    .get("id")
)


if not creation_id:

    print("No creation ID received.")
    raise SystemExit


print()
print("Container ID:", creation_id)


# =========================
# WAIT FOR PROCESSING
# =========================

print()
print("Waiting for Instagram processing...")


status_url = (
    f"https://graph.instagram.com/"
    f"{API_VERSION}/{creation_id}"
)


finished = False


for attempt in range(12):

    time.sleep(5)

    status_response = requests.get(

        status_url,

        params={
            "fields": "status_code,status",
            "access_token": IG_TOKEN
        },

        timeout=60
    )


    print(
        f"Status {attempt + 1}/12:",
        status_response.text
    )


    if not status_response.ok:
        continue


    status_data = status_response.json()


    status_code = status_data.get(
        "status_code"
    )


    if status_code == "FINISHED":

        finished = True
        break


    if status_code in (
        "ERROR",
        "EXPIRED"
    ):

        print(
            "Instagram container failed."
        )

        raise SystemExit


if not finished:

    print(
        "Instagram container did not finish."
    )

    raise SystemExit


# =========================
# PUBLISH
# =========================

print()
print("Publishing to Instagram...")


publish_url = (
    f"https://graph.instagram.com/"
    f"{API_VERSION}/{IG_ID}/media_publish"
)


publish_response = requests.post(

    publish_url,

    data={
        "creation_id": creation_id,
        "access_token": IG_TOKEN
    },

    timeout=120
)


print()
print("PUBLISH RESPONSE:")
print(publish_response.text)


if not publish_response.ok:

    print()
    print("INSTAGRAM PUBLISH FAILED.")
    raise SystemExit


print()
print("================================")
print("SUCCESS - INSTAGRAM POSTED")
print("================================")