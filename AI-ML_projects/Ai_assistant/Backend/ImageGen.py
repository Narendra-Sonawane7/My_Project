import os
import time
from PIL import Image
import requests
from io import BytesIO

def ImageGen(prompt):
    """Generate using free public APIs - NO API KEY!"""
    try:
        os.makedirs("Database", exist_ok=True)

        print(f"🎨 Generating: {prompt}\n")

        # Service 1: Limewire AI (FREE, NO KEY)
        print("1️⃣ Trying Limewire AI...")
        try:
            url = "https://api.limewire.com/api/image/generation"

            payload = {
                "prompt": prompt,
                "aspect_ratio": "1:1"
            }

            response = requests.post(url, json=payload, timeout=60)

            if response.status_code == 200:
                result = response.json()
                img_url = result['data'][0]['asset_url']

                # Download
                img_data = requests.get(img_url, timeout=30)
                image = Image.open(BytesIO(img_data.content))
                image.save("Database/Image.png", "PNG")
                print("✅ Success!\n")
                return True
        except Exception as e:
            print(f"   ❌ {str(e)[:50]}\n")

        # Service 2: Craiyon (formerly DALL-E mini) - NO KEY!
        print("2️⃣ Trying Craiyon...")
        try:
            url = "https://backend.craiyon.com/generate"

            payload = {
                "prompt": prompt,
                "version": "c4ue22fb7kb6wlac"
            }

            response = requests.post(url, json=payload, timeout=120)

            if response.status_code == 200:
                result = response.json()
                # Craiyon returns base64 images
                import base64
                img_data = base64.b64decode(result['images'][0])
                image = Image.open(BytesIO(img_data))
                image.save("Database/Image.png", "PNG")
                print("✅ Success!\n")
                return True
        except Exception as e:
            print(f"   ❌ {str(e)[:50]}\n")

        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def OpenImage():
    if os.path.exists("Database/Image.png"):
        Image.open("Database/Image.png").show()
        print("✅ Displayed!")
        return True
    return False

def Main(newprompt):
    print(f"\n{'='*60}")
    print(f"🎨 SEEU - No API Key Needed!")
    print(f"{'='*60}\n")

    if ImageGen(newprompt):
        OpenImage()
        print("✅ Complete!\n")
    else:
        print("❌ Try again in 1 minute (rate limit)\n")

if __name__ == "__main__":
    Main("a beautiful sunset over mountains, photorealistic")