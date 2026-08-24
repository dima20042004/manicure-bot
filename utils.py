import hashlib
from PIL import Image
from sklearn.cluster import KMeans
import numpy as np
import os

def extract_colors(image_path, n_colors=5):
    img = Image.open(image_path).convert('RGB')
    img = img.resize((150, 150))
    data = np.array(img).reshape(-1, 3)
    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(data)
    centers = kmeans.cluster_centers_.astype(int)
    hex_colors = ['#{:02x}{:02x}{:02x}'.format(*c) for c in centers]
    return hex_colors

def generate_prompt(user_prompt, image_paths):
    colors = []
    for path in image_paths[:5]:
        try:
            colors.extend(extract_colors(path, 3))
        except:
            continue
    color_str = ", ".join(colors[:5]) if colors else "пастельные тона"
    base = user_prompt if user_prompt else "стильный дизайн маникюра"
    return f"{base}, цвета: {color_str}, высокое качество, 4k, детализированный, маникюр, ногти, глянцевый финиш, профессиональное фото"

def image_hash(image_path):
    with open(image_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()