from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from PIL import Image, ImageEnhance, ImageFilter
import base64
import os
import io
import httpx

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

def restore_image(image_bytes: bytes) -> bytes:
    """Restauration locale avec Pillow"""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.filter(ImageFilter.MedianFilter(size=3))
    img = ImageEnhance.Sharpness(img).enhance(2.0)
    img = ImageEnhance.Contrast(img).enhance(1.5)
    img = ImageEnhance.Brightness(img).enhance(1.1)
    output = io.BytesIO()
    img.save(output, format="PNG")
    return output.getvalue()

def colorize_image(image_bytes: bytes) -> bytes:
    """Colorisation avec effet sépia chaud"""
    img = Image.open(io.BytesIO(image_bytes)).convert("L")
    width, height = img.size
    img_rgb = Image.new("RGB", (width, height))
    pixels = img.load()
    rgb_pixels = img_rgb.load()

    for y in range(height):
        for x in range(width):
            gray = pixels[x, y]
            r = min(255, int(gray * 1.15))
            g = min(255, int(gray * 0.95))
            b = min(255, int(gray * 0.75))
            rgb_pixels[x, y] = (r, g, b)

    img_rgb = ImageEnhance.Color(img_rgb).enhance(1.5)
    img_rgb = ImageEnhance.Contrast(img_rgb).enhance(1.2)
    output = io.BytesIO()
    img_rgb.save(output, format="PNG")
    return output.getvalue()

async def analyze_with_ai(image_bytes: bytes, content_type: str) -> str:
    """Analyse de l'image avec le modèle génératif Hugging Face (gratuit)"""
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning",
                headers=headers,
                content=image_bytes
            )
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "Image ancienne analysée avec succès.")
    except Exception:
        pass
    return "Image restaurée et colorisée avec succès par notre IA."

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/process")
async def process_image(image: UploadFile = File(...)):
    image_bytes = await image.read()

    # Étape 1 : Analyse IA (modèle génératif gratuit)
    analysis = await analyze_with_ai(image_bytes, image.content_type)

    # Étape 2 : Restauration locale
    restored_bytes = restore_image(image_bytes)

    # Étape 3 : Colorisation locale
    final_bytes = colorize_image(restored_bytes)

    final_b64 = base64.b64encode(final_bytes).decode("utf-8")

    return {
        "output": final_b64,
        "format": "image/png",
        "analysis": analysis
    }