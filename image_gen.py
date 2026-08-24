from diffusers import StableDiffusionPipeline
import torch
import os
import datetime
from utils import generate_prompt
import config

MODEL_ID = "runwayml/stable-diffusion-v1-5"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"🔧 Используется устройство: {DEVICE}")
print("📦 Загрузка модели Stable Diffusion... (первый раз 5-10 минут)")

try:
    pipe = StableDiffusionPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
        safety_checker=None,
        requires_safety_checker=False
    )
    pipe = pipe.to(DEVICE)
    
    if DEVICE == "cuda":
        pipe.enable_attention_slicing()
        print("⚡ CUDA оптимизация включена")
    
    print("✅ Модель загружена и готова к работе!")
    
except Exception as e:
    print(f"❌ Ошибка загрузки модели: {e}")
    print("⚠️ Бот будет работать, но генерация недоступна")
    pipe = None

def generate_image(user_prompt, image_paths, order_id, user_id):
    if pipe is None:
        raise Exception("Модель не загружена. Проверьте интернет или перезапустите бота.")
    
    prompt = generate_prompt(user_prompt, image_paths)
    negative_prompt = "уродливый, плохое качество, размытый, искаженный, деформированный"
    
    print(f"🎨 Генерация по запросу: {prompt[:100]}...")
    
    with torch.autocast(DEVICE):
        images = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=25,
            guidance_scale=7.0,
            width=512,
            height=512
        ).images
    
    os.makedirs(config.IMAGES_DIR, exist_ok=True)
    filename = f"order_{order_id}_user_{user_id}_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}.png"
    path = os.path.join(config.IMAGES_DIR, filename)
    images[0].save(path)
    
    print(f"✅ Изображение сохранено: {path}")
    return path